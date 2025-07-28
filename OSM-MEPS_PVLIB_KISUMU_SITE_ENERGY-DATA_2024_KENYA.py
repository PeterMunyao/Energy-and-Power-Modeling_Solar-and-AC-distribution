#EDIT-TO-SUITE-YOUR-ANALYSIS

import pandas as pd
import numpy as np
import pvlib
import matplotlib.pyplot as plt
from pvlib.irradiance import get_total_irradiance
from pvlib.temperature import sapm_cell

# Set Garamond font
plt.rcParams["font.family"] = "Garamond"
plt.rcParams.update({'font.size': 14})

# 1. Load the CSV weather data
file_path = 'csv_-0.085477_34.718851_fixed_23_0_PT5M.csv'
df = pd.read_csv(file_path)
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

df.index = df.index.tz_localize(None)

# FILTER for 15 April 2024 to 20 December 2024
df = df.loc['2024-04-15':'2024-12-20']

# 2. Extract weather data
ghi = df["ghi"]
dni = df["dni"]
dhi = df["dhi"]
temp_amb = df["air_temp"]
wind_speed = df["wind_speed_10m"]

# 3. pvlib System Parameters
tilt = 0
azimuth = 0
panel_power_max = 250
system_capacity_kw = 2.00
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)
efficiency_stc = 0.25
temp_coeff = -0.004
inverter_efficiency = 0.85
losses = 1

latitude = -0.085477
longitude = 34.718851
solar_position = pvlib.solarposition.get_solarposition(df.index, latitude, longitude)

poa = get_total_irradiance(
    surface_tilt=tilt,
    surface_azimuth=azimuth,
    dni=dni,
    ghi=ghi,
    dhi=dhi,
    solar_zenith=solar_position["apparent_zenith"],
    solar_azimuth=solar_position["azimuth"],
)
poa_irradiance = poa["poa_global"]

# 4. Dynamic Shading Effect Based on Date (More Shading in December)
def calculate_shading_factor(date):
    # Increase shading in December (around summer solstice)
    # Increase shading in November and December
    if date.month == 12:
        return 0.450  # More shading for December
    elif date.month == 11:
        return 0.50  # More shading for November
    else:
        return 0.58  # Medium shading for other months

# Apply dynamic shading factor
shading_factor = df.index.map(calculate_shading_factor)
poa_irradiance *= shading_factor

# Continue normal calculation
temp_cell = sapm_cell(poa_irradiance, temp_amb, wind_speed, -3.47, -0.0594, 3)

#old line: dc_power = poa_irradiance * num_panels * efficiency_stc * (1 + temp_coeff * (temp_cell - 25))# ERROR
dc_power_pvlib = poa_irradiance / stc_irradiance * num_panels * panel_power_max * (1 + temp_coeff * (temp_cell - 25))
ac_power = dc_power * inverter_efficiency * losses

df["AC_Power_kW_pvlib"] = ac_power / 1000
df["Energy_kWh_pvlib"] = df["AC_Power_kW_pvlib"].resample('h').mean()
df["Daily_Energy_kWh_pvlib"] = df["Energy_kWh_pvlib"].resample('D').sum()

# 5. OSM MEPS calculations (with dynamic shading)
required_columns = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth']
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Column '{col}' missing, filling with 0.")
        df[col] = 0

num_panels_simple = 8
panel_power_max_simple = 250

surface_tilt_simple = 0
surface_azimuth_simple = 0

surface_tilt_rad = np.radians(surface_tilt_simple)
surface_azimuth_rad = np.radians(surface_azimuth_simple)
azimuth_rad = np.radians(df['azimuth'])
zenith_rad = np.radians(df['zenith'])

aoi = np.degrees(np.arccos(
    np.cos(zenith_rad) * np.cos(surface_tilt_rad) +
    np.sin(zenith_rad) * np.sin(surface_tilt_rad) * np.cos(azimuth_rad - surface_azimuth_rad)
))
aoi = np.clip(aoi, 0, 90)

poa_direct = df['dni'] * np.cos(np.radians(aoi))
poa_direct = poa_direct.clip(lower=0)
poa_diffuse = df['dhi'] * (1 + np.cos(surface_tilt_rad)) / 2
poa_reflected = df['ghi'] * df['albedo'] * (1 - np.cos(surface_tilt_rad)) / 2

poa_total_simple = poa_direct + poa_diffuse + poa_reflected

# Apply dynamic shading for the simple model
poa_total_simple *= shading_factor

nominal_operating_cell_temp = 45
module_temp_simple = nominal_operating_cell_temp + poa_total_simple / 800 * (28 - df['air_temp'])

temp_coeff_simple = -0.0045
panel_power_simple = panel_power_max_simple * (1 + temp_coeff_simple * (module_temp_simple - nominal_operating_cell_temp))
dc_power_simple = panel_power_simple * poa_total_simple / 1000
inverter_efficiency_simple = 0.85
ac_power_simple = dc_power_simple * inverter_efficiency_simple

scaled_power_simple = ac_power_simple * num_panels_simple

df["AC_Power_kW_simple"] = scaled_power_simple / 1000
df["Energy_kWh_simple"] = df["AC_Power_kW_simple"].resample('h').mean()
df["Daily_Energy_kWh_simple"] = df["Energy_kWh_simple"].resample('D').sum()

# 6. Load real output energy
real_energy = pd.read_csv('kisumu_sorted.csv')
real_energy['Date'] = pd.to_datetime(real_energy['Date'])
real_energy.set_index('Date', inplace=True)

# Filter real energy to match the same period
real_energy = real_energy.loc['2024-04-15':'2024-12-20']

# Assume the real energy column is named 'Energy' (adjust if different)
real_energy.rename(columns={'Generated_kWh': 'Generated_kWh'}, inplace=True)

# 7. Plot Models + Real Energy with Custom Styling
# 7. Plot Models + Real Energy with Custom Styling
fig, ax = plt.subplots(figsize=(12, 6), facecolor='#f9f9f9')
ax.set_facecolor('#f9f9f9')

# Plot models
ax.plot(df["Daily_Energy_kWh_pvlib"].dropna(), label="PVLIB Model\n (with dynamic shading)", color='orange', linestyle='-', linewidth=2.5)
ax.plot(df["Daily_Energy_kWh_simple"].dropna(), label="OSM-MEPS Model\n (with dynamic shading)", color='green', linestyle='-', linewidth=2.5)

# Plot real measured data
ax.plot(real_energy["Generated_kWh"], label="PV Output Energy: Kisumu, Kenya (Measured)\n (shading: medium)", color='blue', linestyle='-', linewidth=2.5)

# Axes labels
ax.set_xlabel("Date", fontsize=18, fontweight='bold')
ax.set_ylabel("Daily Energy (kWh)", fontsize=18, fontweight='bold')

# Ticks
ax.tick_params(axis='both', labelsize=16)

# Dotted grid lines
ax.grid(True, linestyle=':', linewidth=0.8, color='gray')

# Legend
ax.legend(
    fontsize=15,
    loc='upper center',
    bbox_to_anchor=(0.5, -0.18),
    ncol=3,
    frameon=False
)

# Layout
plt.tight_layout()

# Save and show
plt.savefig("Kisumu_KENYA_1_models_real_energy_comparison_2024_dynamic_shading.pdf", format="pdf", bbox_inches='tight')
plt.show()

#-------------------

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Align indexes to ensure that only matching dates are compared
common_index = real_energy.index.intersection(df.index)

# Extract matching series for comparison
y_true = real_energy.loc[common_index, "Generated_kWh"]
y_pred_pvlib = df.loc[common_index, "Daily_Energy_kWh_pvlib"]
y_pred_simple = df.loc[common_index, "Daily_Energy_kWh_simple"]

# Function to compute error metrics
def compute_metrics(y_true, y_pred, model_name):
    mae = mean_absolute_error(y_true, y_pred)
   
    r2 = r2_score(y_true, y_pred)
    print(f"🔵 {model_name} Metrics:")
    print(f"  - MAE  : {mae:.2f} kWh")

    print(f"  - R²   : {r2:.3f}")
    print()

# Calculate and print metrics for both models
compute_metrics(y_true, y_pred_pvlib, "pvlib Model")
compute_metrics(y_true, y_pred_simple, "OSM-MEPS Simple Model")

#OLD_CODE


#Medium to Heavy SHADING_CASE OF Kisumu, Kenya

import pandas as pd
import numpy as np
import pvlib
import matplotlib.pyplot as plt
from pvlib.irradiance import get_total_irradiance
from pvlib.temperature import sapm_cell

# Set Garamond font
plt.rcParams["font.family"] = "Garamond"
plt.rcParams.update({'font.size': 14})

# 1. Load the CSV weather data
file_path = 'csv_-0.085477_34.718851_fixed_23_0_PT5M.csv'
df = pd.read_csv(file_path)
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

df.index = df.index.tz_localize(None)

# FILTER for 15 April 2024 to 20 December 2024
df = df.loc['2024-04-15':'2024-12-20']

# 2. Extract weather data
ghi = df["ghi"]
dni = df["dni"]
dhi = df["dhi"]
temp_amb = df["air_temp"]
wind_speed = df["wind_speed_10m"]

# 3. pvlib System Parameters
tilt = 0
azimuth = 0
panel_power_max = 250
system_capacity_kw = 2.00
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)
efficiency_stc = 0.25
temp_coeff = -0.004
inverter_efficiency = 0.91
losses = 1

latitude = -0.085477
longitude = 34.718851
solar_position = pvlib.solarposition.get_solarposition(df.index, latitude, longitude)

poa = get_total_irradiance(
    surface_tilt=tilt,
    surface_azimuth=azimuth,
    dni=dni,
    ghi=ghi,
    dhi=dhi,
    solar_zenith=solar_position["apparent_zenith"],
    solar_azimuth=solar_position["azimuth"],
)
poa_irradiance = poa["poa_global"]

# 4. Dynamic Shading Effect Based on Date (More Shading in December)
def calculate_shading_factor(date):
    # Increase shading in December (around summer solstice)
    # Increase shading in November and December
    if date.month == 12:
        return 0.40  # More shading for December
    elif date.month == 11:
        return 0.50  # More shading for November
    else:
        return 0.55  # Medium shading for other months

# Apply dynamic shading factor
shading_factor = df.index.map(calculate_shading_factor)
poa_irradiance *= shading_factor

# Continue normal calculation
temp_cell = sapm_cell(poa_irradiance, temp_amb, wind_speed, -3.47, -0.0594, 3)

#ERROR CODE LINE: dc_power = poa_irradiance * num_panels * efficiency_stc * (1 + temp_coeff * (temp_cell - 25))
dc_power_pvlib = poa_irradiance / stc_irradiance * num_panels * panel_power_max * (1 + temp_coeff * (temp_cell - 25))
ac_power = dc_power_pvlib * inverter_efficiency * losses

df["AC_Power_kW_pvlib"] = ac_power / 1000
df["Energy_kWh_pvlib"] = df["AC_Power_kW_pvlib"].resample('h').mean()
df["Daily_Energy_kWh_pvlib"] = df["Energy_kWh_pvlib"].resample('D').sum()

# 5. OSM MEPS calculations (with dynamic shading)
required_columns = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth']
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Column '{col}' missing, filling with 0.")
        df[col] = 0

num_panels_simple = 8
panel_power_max_simple = 250

surface_tilt_simple = 0
surface_azimuth_simple = 0

surface_tilt_rad = np.radians(surface_tilt_simple)
surface_azimuth_rad = np.radians(surface_azimuth_simple)
azimuth_rad = np.radians(df['azimuth'])
zenith_rad = np.radians(df['zenith'])

aoi = np.degrees(np.arccos(
    np.cos(zenith_rad) * np.cos(surface_tilt_rad) +
    np.sin(zenith_rad) * np.sin(surface_tilt_rad) * np.cos(azimuth_rad - surface_azimuth_rad)
))
aoi = np.clip(aoi, 0, 90)

poa_direct = df['dni'] * np.cos(np.radians(aoi))
poa_direct = poa_direct.clip(lower=0)
poa_diffuse = df['dhi'] * (1 + np.cos(surface_tilt_rad)) / 2
poa_reflected = df['ghi'] * df['albedo'] * (1 - np.cos(surface_tilt_rad)) / 2

poa_total_simple = poa_direct + poa_diffuse + poa_reflected

# Apply dynamic shading for the simple model
poa_total_simple *= shading_factor

nominal_operating_cell_temp = 45
module_temp_simple = nominal_operating_cell_temp + poa_total_simple / 800 * (28 - df['air_temp'])

temp_coeff_simple = -0.0045
panel_power_simple = panel_power_max_simple * (1 + temp_coeff_simple * (module_temp_simple - nominal_operating_cell_temp))
dc_power_simple = panel_power_simple * poa_total_simple / 1000
inverter_efficiency_simple = 0.91
ac_power_simple = dc_power_simple * inverter_efficiency_simple

scaled_power_simple = ac_power_simple * num_panels_simple

df["AC_Power_kW_simple"] = scaled_power_simple / 1000
df["Energy_kWh_simple"] = df["AC_Power_kW_simple"].resample('h').mean()
df["Daily_Energy_kWh_simple"] = df["Energy_kWh_simple"].resample('D').sum()

# 6. Load real output energy
real_energy = pd.read_csv('kisumu_sorted.csv')
real_energy['Date'] = pd.to_datetime(real_energy['Date'])
real_energy.set_index('Date', inplace=True)

# Filter real energy to match the same period
real_energy = real_energy.loc['2024-04-15':'2024-12-20']

# Assume the real energy column is named 'Energy' (adjust if different)
real_energy.rename(columns={'Generated_kWh': 'Generated_kWh'}, inplace=True)

# 7. Plot Models + Real Energy
fig, ax = plt.subplots(figsize=(11, 6), facecolor='#f0f0f0')
plt.gca().set_facecolor('#f0f0f0')

# Models
plt.plot(df["Daily_Energy_kWh_pvlib"].dropna(), label="pvlib Model\n (with dynamic shading)", color='orange', linestyle='-', linewidth=2.5)
plt.plot(df["Daily_Energy_kWh_simple"].dropna(), label="OSM-MEPS Model\n (with dynamic shading)", color='blue', linestyle='-', linewidth=2.5)

# Real measured energy
plt.plot(real_energy["Generated_kWh"], label="PV energy measured: Kisumu, Kenya\n (shading: medium)", color='green', linestyle='--', linewidth=2.5)

# Labels, grid, and legend
plt.xlabel("Date", fontsize=18)
plt.ylabel("Daily Energy (kWh)", fontsize=18)
plt.title("Energy graph for a 2kW_PV system in Kisumu, Kenya (15 April to December 20 2024): Modeled vs Measured", fontsize=15)
plt.xticks(rotation=0, fontsize=16)
plt.yticks(fontsize=16)
plt.grid()

plt.legend(
    fontsize=16, 
    loc='upper center', 
    bbox_to_anchor=(0.5, -0.16), 
    ncol=3, 
    frameon=False
)

plt.tight_layout()
plt.savefig("Kisumu_KENYA_1_models_real_energy_comparison_2024_dynamic_shading.pdf", format="pdf", bbox_inches='tight')
plt.show()
