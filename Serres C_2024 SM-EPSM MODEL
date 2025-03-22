import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set font to Garamond
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Garamond']

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

# Convert angles to radians
surface_tilt_rad = np.radians(surface_tilt)
surface_azimuth_rad = np.radians(surface_azimuth)

# Handle negative azimuth values
df['azimuth'] = df['azimuth'] % 360
azimuth_rad = np.radians(df['azimuth'])
zenith_rad = np.radians(df['zenith'])

# Angle of Incidence (AOI) Calculation
aoi = np.degrees(np.arccos(
    np.cos(zenith_rad) * np.cos(surface_tilt_rad) +
    np.sin(zenith_rad) * np.sin(surface_tilt_rad) * np.cos(azimuth_rad - surface_azimuth_rad)
))
aoi = np.clip(aoi, 0, 180)

# Plane of Array (POA) Irradiance Calculation
df['poa_direct'] = df['dni'] * np.cos(np.radians(aoi)) * (1 - df['cloud_opacity'] / 100)
df['poa_direct'] = df['poa_direct'].clip(lower=0)
df['poa_diffuse'] = df['dhi'] * (1 + np.cos(surface_tilt_rad)) / 2
df['poa_sky_diffuse'] = df['ghi'] * df['albedo'] * (1 - np.cos(surface_tilt_rad)) / 2
df['poa_total'] = df['poa_direct'] + df['poa_diffuse'] + df['poa_sky_diffuse']

# Module Temperature Calculation
df['module_temp'] = nominal_operating_cell_temp + df['poa_total'] / 800 * (28 - df['air_temp'])

# DC Power Calculation
df['dc_power'] = panel_power_max * (1 + temp_coeff * (df['module_temp'] - nominal_operating_cell_temp))
df['dc_power'] *= df['poa_total'] / stc_irradiance
df['dc_power'] *= (1 - 0.002 * df['relative_humidity'])

# AC Power Calculation
df['ac_power'] = df['dc_power'] * inverter_efficiency
df['scaled_power'] = df['ac_power'] * num_panels

# Apply Losses
conductor_loss_factor = 0.01
other_loss_factor = 0.01
df['actual_ac_power'] = df['ac_power'] * (1 - conductor_loss_factor) * (1 - other_loss_factor)
df['scaled_actual_power'] = df['actual_ac_power'] * num_panels

# Energy Calculation (Averaging 5-minute power over 1 hour)
df['energy_kwh'] = df['scaled_actual_power'].resample('H').mean() / 1000
df_energy_kwh_actual = df['energy_kwh'].resample('D').sum()

# Calculate Total Yearly Energy in MWh
total_year_energy_mwh_actual = df_energy_kwh_actual.sum() / 1000
print(f"Total energy output for the whole year (after system losses): {total_year_energy_mwh_actual:.2f} MWh")

# Plotting Yearly Energy Production
plt.figure(figsize=(12, 5))
plt.plot(df_energy_kwh_actual.index, df_energy_kwh_actual, 'b-', label='Daily Energy Production (kWh)', linewidth=2)
plt.xlabel("Date", fontsize=16)
plt.ylabel("Energy (kWh)", fontsize=16)
plt.title("Daily Energy Production for Serres -C, Greece (2024) using SM-EPSM", fontsize=16)
plt.legend()
plt.grid(True, linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.savefig("SERREC_C_2024_with_losses_SM-EPSM.pdf", format="pdf")
plt.show()
