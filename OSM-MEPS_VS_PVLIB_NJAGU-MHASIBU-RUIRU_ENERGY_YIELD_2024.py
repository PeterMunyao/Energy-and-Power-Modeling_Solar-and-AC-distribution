import pandas as pd
import numpy as np
import pvlib
import matplotlib.pyplot as plt
from pvlib.irradiance import get_total_irradiance
from pvlib.temperature import sapm_cell

# Set Garamond font
plt.rcParams["font.family"] = "Garamond"
plt.rcParams.update({'font.size': 14})

# === Load Data ===
file_path = 'csv_-1.11665_36.92927_fixed_23_0_PT5M_2024.csv'
df = pd.read_csv(file_path)
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

# === Weather Data ===
ghi = df["ghi"]
dni = df["dni"]
dhi = df["dhi"]
temp_amb = df["air_temp"]
wind_speed = df.get("wind_speed_10m", pd.Series(0, index=df.index))  # Handle missing wind

# === PVLIB Parameters ===
tilt = 25
azimuth = 180
panel_power_max = 350
system_capacity_kw = 8.75
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)
efficiency_stc = 0.25
temp_coeff = -0.004
inverter_efficiency = 0.975
losses = 1

latitude = -1.11665
longitude = 36.92927

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
temp_cell = sapm_cell(poa_irradiance, temp_amb, wind_speed, -3.47, -0.0594, 3)

dc_power = poa_irradiance * num_panels * efficiency_stc * (1 + temp_coeff * (temp_cell - 25))
ac_power = dc_power * inverter_efficiency * losses

df["AC_Power_kW_pvlib"] = ac_power / 1000
df["Energy_kWh_pvlib"] = df["AC_Power_kW_pvlib"].resample('h').mean()
df["Daily_Energy_kWh_pvlib"] = df["Energy_kWh_pvlib"].resample('D').sum()
annual_pvlib = df["Daily_Energy_kWh_pvlib"].sum()

# === OSM-MEPS Model ===
required_cols = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth']
for col in required_cols:
    if col not in df.columns:
        df[col] = 0

panel_area = 1.6
total_area = 40
num_panels_simple = int(total_area / panel_area)
panel_power_max_simple = 350

tilt_simple = 22.5
azimuth_simple = 90

tilt_rad = np.radians(tilt_simple)
az_rad = np.radians(azimuth_simple)
zen_rad = np.radians(df['zenith'])
sun_az_rad = np.radians(df['azimuth'])

aoi = np.degrees(np.arccos(
    np.cos(zen_rad) * np.cos(tilt_rad) +
    np.sin(zen_rad) * np.sin(tilt_rad) * np.cos(sun_az_rad - az_rad)
))
aoi = np.clip(aoi, 0, 90)

poa_direct = df['dni'] * np.cos(np.radians(aoi)).clip(lower=0)
poa_diffuse = df['dhi'] * (1 + np.cos(tilt_rad)) / 2
poa_reflected = df['ghi'] * df['albedo'] * (1 - np.cos(tilt_rad)) / 2
poa_total_simple = poa_direct + poa_diffuse + poa_reflected

module_temp = 45 + poa_total_simple / 800 * (28 - df['air_temp'])

temp_coeff_simple = -0.0045
panel_power = panel_power_max_simple * (1 + temp_coeff_simple * (module_temp - 45))
dc_power_simple = panel_power * poa_total_simple / 1000
ac_power_simple = dc_power_simple * 0.87

scaled_power = ac_power_simple * num_panels_simple

df["AC_Power_kW_simple"] = scaled_power / 1000
df["Energy_kWh_simple"] = df["AC_Power_kW_simple"].resample('h').mean()
df["Daily_Energy_kWh_simple"] = df["Energy_kWh_simple"].resample('D').sum()
annual_simple = df["Daily_Energy_kWh_simple"].sum()

# === Plotting ===
fig, ax = plt.subplots(figsize=(11,6), facecolor='#f9f9f9')
ax.set_facecolor('#f9f9f9')

line1, = ax.plot(df["Daily_Energy_kWh_pvlib"].dropna(), 
                 color='orange', 
                 linewidth=2.45, 
                 label=f"PVLIB Model: {annual_pvlib:,.2f} kWh/year")

line2, = ax.plot(df["Daily_Energy_kWh_simple"].dropna(), 
                 color='blue', 
                 linewidth=2.45, 
                 label=f"OSM-MEPS Model: {annual_simple:,.2f} kWh/year")

ax.set_xlabel("Date", fontsize=18, fontweight='bold')
ax.set_ylabel("Daily Energy (kWh)", fontsize=18, fontweight='bold')

ax.grid(True, linestyle='--', alpha=0.5)
ax.tick_params(axis='both', labelsize=15)

# Legend
ax.legend(loc='upper center',
          bbox_to_anchor=(0.5, -0.15),
          fontsize=16,
          ncol=2,
          frameon=False)

plt.tight_layout()
plt.savefig("NJAGU_FINAL_KENYA_PVLIB_vs_OSM_MEPS_daily_energy.pdf", format="pdf", bbox_inches='tight')
plt.show()

# === Save Output ===
df.to_csv("solar_power_output_combined_2024.csv")

# ---------------------------------------------------------
# 7. Compute Error Metrics

# Drop any missing values
comparison_df = df[["Daily_Energy_kWh_pvlib", "Daily_Energy_kWh_simple"]].dropna()

y_true = comparison_df["Daily_Energy_kWh_pvlib"]
y_pred = comparison_df["Daily_Energy_kWh_simple"]

# Error calculations
mae = np.mean(np.abs(y_true - y_pred))                # Mean Absolute Error
mse = np.mean((y_true - y_pred)**2)                    # Mean Squared Error
rmse = np.sqrt(mse)                                    # Root Mean Squared Error
mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100  # Mean Absolute Percentage Error
bias = np.mean(y_pred - y_true)                        # Mean Bias Error

# Print nicely
print("\n----- Error Metrics between pvlib and OSM-MEPS models -----")
print(f"MAE  (Mean Absolute Error):       {mae:.2f} kWh")
print(f"MSE  (Mean Squared Error):         {mse:.2f} (kWh)^2")
print(f"RMSE (Root Mean Squared Error):    {rmse:.2f} kWh")
print(f"MAPE (Mean Absolute Percentage Error): {mape:.2f}%")
print(f"Bias (Mean Bias Error):            {bias:.2f} kWh")



#-----------------------------------------------
#OLD-CODE

import pandas as pd
import numpy as np
import pvlib
import matplotlib.pyplot as plt
from pvlib.irradiance import get_total_irradiance
from pvlib.temperature import sapm_cell

# Set Garamond font
plt.rcParams["font.family"] = "Garamond"
plt.rcParams.update({'font.size': 14})

# === Load Data ===
file_path = 'csv_-1.11665_36.92927_fixed_23_0_PT5M_2024.csv'
df = pd.read_csv(file_path)
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

# === Weather Data ===
ghi = df["ghi"]
dni = df["dni"]
dhi = df["dhi"]
temp_amb = df["air_temp"]
wind_speed = df.get("wind_speed_10m", pd.Series(0, index=df.index))  # Handle missing wind

# === PVLIB Parameters ===
tilt = 25
azimuth = 180
panel_power_max = 350
system_capacity_kw = 8.75
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)
efficiency_stc = 0.25
temp_coeff = -0.004
inverter_efficiency = 0.975
losses = 1

latitude = -1.11665
longitude = 36.92927

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
temp_cell = sapm_cell(poa_irradiance, temp_amb, wind_speed, -3.47, -0.0594, 3)

dc_power = poa_irradiance * num_panels * efficiency_stc * (1 + temp_coeff * (temp_cell - 25))
ac_power = dc_power * inverter_efficiency * losses

df["AC_Power_kW_pvlib"] = ac_power / 1000
df["Energy_kWh_pvlib"] = df["AC_Power_kW_pvlib"].resample('h').mean()
df["Daily_Energy_kWh_pvlib"] = df["Energy_kWh_pvlib"].resample('D').sum()
annual_pvlib = df["Daily_Energy_kWh_pvlib"].sum()

# === OSM-MEPS Model ===
required_cols = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth']
for col in required_cols:
    if col not in df.columns:
        df[col] = 0

panel_area = 1.6
total_area = 40
num_panels_simple = int(total_area / panel_area)
panel_power_max_simple = 350

tilt_simple = 22.5
azimuth_simple = 90

tilt_rad = np.radians(tilt_simple)
az_rad = np.radians(azimuth_simple)
zen_rad = np.radians(df['zenith'])
sun_az_rad = np.radians(df['azimuth'])

aoi = np.degrees(np.arccos(
    np.cos(zen_rad) * np.cos(tilt_rad) +
    np.sin(zen_rad) * np.sin(tilt_rad) * np.cos(sun_az_rad - az_rad)
))
aoi = np.clip(aoi, 0, 90)

poa_direct = df['dni'] * np.cos(np.radians(aoi)).clip(lower=0)
poa_diffuse = df['dhi'] * (1 + np.cos(tilt_rad)) / 2
poa_reflected = df['ghi'] * df['albedo'] * (1 - np.cos(tilt_rad)) / 2
poa_total_simple = poa_direct + poa_diffuse + poa_reflected

module_temp = 45 + poa_total_simple / 800 * (28 - df['air_temp'])

temp_coeff_simple = -0.0045
panel_power = panel_power_max_simple * (1 + temp_coeff_simple * (module_temp - 45))
dc_power_simple = panel_power * poa_total_simple / 1000
ac_power_simple = dc_power_simple * 0.87

scaled_power = ac_power_simple * num_panels_simple

df["AC_Power_kW_simple"] = scaled_power / 1000
df["Energy_kWh_simple"] = df["AC_Power_kW_simple"].resample('h').mean()
df["Daily_Energy_kWh_simple"] = df["Energy_kWh_simple"].resample('D').sum()
annual_simple = df["Daily_Energy_kWh_simple"].sum()

# === Plotting ===
fig, ax = plt.subplots(figsize=(13, 6.5), facecolor='#f0f0f0')
ax.set_facecolor('#f0f0f0')

line1, = ax.plot(df["Daily_Energy_kWh_pvlib"].dropna(), 
                 color='orange', 
                 linewidth=2.5, 
                 label=f"PVLIB Model: {annual_pvlib:,.0f} kWh")

line2, = ax.plot(df["Daily_Energy_kWh_simple"].dropna(), 
                 color='blue', 
                 linewidth=2.5, 
                 label=f"OSM-MEPS Model: {annual_simple:,.0f} kWh")

ax.set_xlabel("Date", fontsize=18)
ax.set_ylabel("Daily Energy (kWh)", fontsize=18)
ax.set_title("Daily PV Energy Output in 2024: PVLIB vs OSM-MEPS\nNjagu-Mhasibu-Ruiru Estate, Kenya", fontsize=17)
ax.grid(True, linestyle='--', alpha=0.5)
ax.tick_params(axis='both', labelsize=15)

# Legend
ax.legend(loc='upper center',
          bbox_to_anchor=(0.5, -0.15),
          fontsize=16,
          ncol=2,
          frameon=False)

plt.tight_layout()
plt.savefig("Njangu_KENYA_PVLIB_vs_OSM_MEPS_daily_energy.pdf", format="pdf", bbox_inches='tight')
plt.show()

# === Save Output ===
df.to_csv("solar_power_output_combined_2024.csv")
