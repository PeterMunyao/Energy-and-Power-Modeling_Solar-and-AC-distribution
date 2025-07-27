import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set font to Garamond
# Set Garamond font
plt.rcParams["font.family"] = "Garamond"

# Load CSV Data
file_path = 'csv_40.886273_23.912687_fixed_23_180_PT5M.csv'
df = pd.read_csv(file_path)

# Convert 'period_end' to datetime and set as index
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

# Ensure required columns exist
required_columns = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth', 'cloud_opacity', 'relative_humidity', 'wind_speed_10m']
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Column '{col}' is missing in CSV. Filling with zeros.")
        df[col] = 0

# System Parameters
panel_power_max = 390  # W per panel
system_capacity_kw = 1010.88  # System capacity in kW
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)

surface_tilt = 25  # degrees
surface_azimuth = 180  # 0 degrees (North)

temp_coeff = -0.005  # Temperature coefficient -0.50% per degree Celsius
nominal_operating_cell_temp = 45  # °C
inverter_efficiency = 0.98
stc_irradiance = 1000  # W/m²

# Extract December Data
december_data = df[(df.index.month == 12) & (df.index.year == 2024)].copy()

# Convert angles to radians
surface_tilt_rad = np.radians(surface_tilt)
surface_azimuth_rad = np.radians(surface_azimuth)

# Handle negative azimuth values
december_data['azimuth'] = december_data['azimuth'] % 360
azimuth_rad = np.radians(december_data['azimuth'])
zenith_rad = np.radians(december_data['zenith'])

# Angle of Incidence (AOI) Calculation
aoi = np.degrees(np.arccos(
    np.cos(zenith_rad) * np.cos(surface_tilt_rad) +
    np.sin(zenith_rad) * np.sin(surface_tilt_rad) * np.cos(azimuth_rad - surface_azimuth_rad)
))
aoi = np.clip(aoi, 0, 180)

# Plane of Array (POA) Irradiance Calculation
december_data['poa_direct'] = december_data['dni'] * np.cos(np.radians(aoi)) * (1 - december_data['cloud_opacity'] / 100)
december_data['poa_direct'] = december_data['poa_direct'].clip(lower=0)
december_data['poa_diffuse'] = december_data['dhi'] * (1 + np.cos(surface_tilt_rad)) / 2
december_data['poa_sky_diffuse'] = december_data['ghi'] * december_data['albedo'] * (1 - np.cos(surface_tilt_rad)) / 2
december_data['poa_total'] = december_data['poa_direct'] + december_data['poa_diffuse'] + december_data['poa_sky_diffuse']

# Module Temperature Calculation
december_data['module_temp'] = nominal_operating_cell_temp + december_data['poa_total'] / 800 * (28 - december_data['air_temp'])

# DC Power Calculation
december_data['dc_power'] = panel_power_max * (1 + temp_coeff * (december_data['module_temp'] - nominal_operating_cell_temp))
december_data['dc_power'] *= december_data['poa_total'] / stc_irradiance
december_data['dc_power'] *= (1 - 0.002 * december_data['relative_humidity'])

# AC Power Calculation
december_data['ac_power'] = december_data['dc_power'] * inverter_efficiency
december_data['scaled_power'] = december_data['ac_power'] * num_panels

# Apply Losses
conductor_loss_factor = 0.01
other_loss_factor = 0.01
december_data['actual_ac_power'] = december_data['ac_power'] * (1 - conductor_loss_factor) * (1 - other_loss_factor)
december_data['scaled_actual_power'] = december_data['actual_ac_power'] * num_panels

# Energy Calculation (Averaging 5-minute power over 1 hour)
december_data['energy_kwh'] = december_data['scaled_actual_power'].resample('H').mean() / 1000
december_energy_kwh_actual = december_data['energy_kwh'].resample('D').sum()

total_december_energy_mwh_actual = december_energy_kwh_actual.sum() / 1000
print(f"Total energy output for December 2024 (after system losses): {total_december_energy_mwh_actual:.2f} MWh")

# Plotting
plt.figure(figsize=(12, 5))
plt.plot(december_energy_kwh_actual.index, december_energy_kwh_actual, 'g-', label='Daily Energy Production (kWh)', linewidth=2)
plt.xlabel("Date", fontsize=16)
plt.ylabel("Energy (kWh)", fontsize=16)
plt.title("Daily Energy Production for Serres-C, Greece in December 2024 using SM-EPSM." , fontsize=16)
plt.legend()
plt.grid(True, linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.savefig("SERREC_C_December_2024_with_losses_SM-EPSM.pdf", format="pdf")
plt.show()

#----------------------------------------------------
#----------------------------------------------------
#----------------------------------------------------
#------------------------PVLIB-----------------------
#----------------------VALIDATION--------------------
#----------------------------------------------------

import pandas as pd
import numpy as np
import pvlib
import matplotlib.pyplot as plt
from pvlib.irradiance import get_total_irradiance
from pvlib.temperature import sapm_cell

# Load CSV data
file_path = "csv_40.886273_23.912687_fixed_23_180_PT5M.csv"
df = pd.read_csv(file_path, parse_dates=["period_end"], index_col="period_end")

# Filter data for December 2024
df = df[df.index.month == 12]

# Extract necessary weather data
ghi = df["ghi"]  # Global Horizontal Irradiance (W/m²)
dni = df["dni"]  # Direct Normal Irradiance (W/m²)
dhi = df["dhi"]  # Diffuse Horizontal Irradiance (W/m²)
temp_amb = df["air_temp"]  # Ambient Temperature (°C)
wind_speed = df["wind_speed_10m"]  # Wind Speed (m/s)

# System Parameters
tilt = 25  # Panel tilt angle (degrees)
azimuth = 180  # South-facing panels
panel_power_max = 390  # W per panel
system_capacity_kw = 1010.88  # System capacity in kW
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)
efficiency_stc = 0.25  # Assuming the panel has 24% efficiency at STC
temp_coeff = -0.004  # Power temperature coefficient (%/°C)
inverter_efficiency = 0.99  # Inverter efficiency (99%)
losses = 1  # Total losses factor (soiling, mismatch, wiring, etc.)

# Calculate POA irradiance
solar_position = pvlib.solarposition.get_solarposition(df.index, 40.886273, 23.912687)
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

# Cell Temperature Calculation
temp_cell = sapm_cell(poa_irradiance, temp_amb, wind_speed, -3.47, -0.0594, 3)

# DC Power Output Calculation
dc_power = poa_irradiance * num_panels * efficiency_stc * (1 + temp_coeff * (temp_cell - 25))

# AC Power Output with Losses
ac_power = dc_power * inverter_efficiency * losses

df["AC_Power_kW"] = ac_power / 1000  # Convert to kW

# Energy Calculation (5-minute intervals to hourly energy)
df["Energy_kWh"] = df["AC_Power_kW"].resample('H').mean()  # Hourly energy in kWh

df["Daily_Energy_kWh"] = df["Energy_kWh"].resample('D').sum()  # Daily energy in kWh

# Capacity Factor Calculation
cf = df["AC_Power_kW"].sum() / (system_capacity_kw * len(df) * 5 / 60)  # 5-minute intervals

print(f"Capacity Factor: {cf:.2%}")

# Set Garamond font
plt.rcParams["font.family"] = "Garamond"

# Plot Power Output for December and save as PDF
plt.figure(figsize=(12, 5))
plt.plot(df.index, df["AC_Power_kW"], label="AC Power (kW)", color='green')
plt.xlabel("Time")
plt.ylabel("Power (kW)")
plt.title("PV System Power Output at 5 minutes for Serres C using pvlib (December 2024)")
plt.legend()
plt.grid()
plt.savefig("power_output_december.pdf", format="pdf")
plt.show()

# Plot Daily Energy Output for December as a line graph and save as PDF
plt.figure(figsize=(12, 5))
plt.plot(df["Daily_Energy_kWh"].dropna().index, df["Daily_Energy_kWh"].dropna(), label="Daily Energy (kWh)", linestyle='-', color='orange')
plt.xlabel("Date", fontsize=16)
plt.ylabel("Energy (kWh)", fontsize=16)
plt.title("Daily Energy Production for Serres C using pvlib (December 2024)", fontsize=16)
plt.legend()
plt.grid()
plt.savefig("PVLIB_NJAGU_daily_energy_december.pdf", format="pdf")
plt.show()

# Save results
df.to_csv("solar_power_output_december.csv")


