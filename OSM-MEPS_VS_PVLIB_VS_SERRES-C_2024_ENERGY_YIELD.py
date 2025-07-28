import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pvlib

# === Load and prepare satellite-based weather data ===
file_path = "csv_40.886273_23.912687_fixed_23_180_PT5M.csv"
df = pd.read_csv(file_path)
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

# === Filter for 2024 ===
df = df[df.index.year == 2024]

# === Ensure required columns ===
required_columns = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth',
                    'cloud_opacity', 'relative_humidity', 'wind_speed_10m']
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Column '{col}' is missing. Filling with zeros.")
        df[col] = 0

# === System configuration ===
tilt = 25
azimuth = 180
panel_power_max = 390  # W
system_capacity_kw = 1010.88
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)
inverter_efficiency = 0.99
temp_coeff = -0.005
stc_irradiance = 1000  # W/m²

# === PVLIB Method ===
solar_position = pvlib.solarposition.get_solarposition(df.index, 40.886273, 23.912687)
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=tilt,
    surface_azimuth=azimuth,
    dni=df['dni'],
    ghi=df['ghi'],
    dhi=df['dhi'],
    solar_zenith=solar_position['apparent_zenith'],
    solar_azimuth=solar_position['azimuth']
)
poa_irradiance = poa['poa_global']
temp_cell = pvlib.temperature.sapm_cell(
    poa_irradiance, df['air_temp'], df['wind_speed_10m'], -3.47, -0.0594, 3
)

#old line: dc_power_pvlib = poa_irradiance * num_panels * 0.25 * (1 + temp_coeff * (temp_cell - 25))
dc_power_pvlib = poa_irradiance / stc_irradiance * num_panels * panel_power_max * (1 + temp_coeff * (temp_cell - 25))
ac_power_pvlib = dc_power_pvlib * inverter_efficiency
df['pvlib_energy_kWh'] = (ac_power_pvlib / 1000).resample('h').mean()
daily_energy_pvlib = df['pvlib_energy_kWh'].resample('D').sum()

# === SM-EPSM Method ===
tilt_rad = np.radians(tilt)
azimuth_panel_rad = np.radians(azimuth)
df['azimuth'] = df['azimuth'] % 360
zenith_rad = np.radians(df['zenith'])
azimuth_rad = np.radians(df['azimuth'])

aoi = np.degrees(np.arccos(
    np.cos(zenith_rad) * np.cos(tilt_rad) +
    np.sin(zenith_rad) * np.sin(tilt_rad) * np.cos(azimuth_rad - azimuth_panel_rad)
))
aoi = np.clip(aoi, 0, 180)

df['poa_direct'] = df['dni'] * np.cos(np.radians(aoi)) * (1 - df['cloud_opacity'] / 100)
df['poa_direct'] = df['poa_direct'].clip(lower=0)
df['poa_diffuse'] = df['dhi'] * (1 + np.cos(tilt_rad)) / 2
df['poa_sky_diffuse'] = df['ghi'] * df['albedo'] * (1 - np.cos(tilt_rad)) / 2
df['poa_total'] = df['poa_direct'] + df['poa_diffuse'] + df['poa_sky_diffuse']

df['module_temp'] = 45 + df['poa_total'] / 800 * (28 - df['air_temp'])
df['dc_power'] = panel_power_max * (1 + temp_coeff * (df['module_temp'] - 45))
df['dc_power'] *= df['poa_total'] / stc_irradiance
df['dc_power'] *= (1 - 0.002 * df['relative_humidity'])
df['ac_power'] = df['dc_power'] * inverter_efficiency
df['scaled_power'] = df['ac_power'] * num_panels
df['actual_power'] = df['scaled_power'] * 0.99 * 0.99
df['epsm_energy_kWh'] = df['actual_power'].resample('h').mean() / 1000
daily_energy_epsm = df['epsm_energy_kWh'].resample('D').sum()

# === Load PVOutput actual data ===
pvoutput_actual = pd.read_csv("serres_2024_full_dataset.csv")
pvoutput_actual['Date'] = pd.to_datetime(pvoutput_actual['Date'])
pvoutput_actual.set_index('Date', inplace=True)
pvoutput_actual['Generated_kWh'] = pd.to_numeric(pvoutput_actual['Generated_kWh'], errors='coerce')
pvoutput_actual.dropna(inplace=True)

# === Set Garamond font globally ===
plt.rcParams["font.family"] = "Garamond"

# === Line Plot: Daily Energy ===
fig, ax = plt.subplots(figsize=(13, 6), facecolor='#f9f9f9')
ax.set_facecolor('#f9f9f9')

ax.plot(daily_energy_pvlib.index, daily_energy_pvlib, label="PVLIB Model", linewidth=3, color='orange')
ax.plot(daily_energy_epsm.index, daily_energy_epsm, label="OSM-MEPS Model", linestyle='--', linewidth=3, color='green')

if not pvoutput_actual.empty:
    ax.plot(pvoutput_actual.index, pvoutput_actual['Generated_kWh'], 
            label="Measured Solar PV Energy (Serres-C)", linestyle='-', linewidth=3, color='blue')

ax.set_xlabel("Date", fontsize=18,fontweight='bold')
ax.set_ylabel("Daily Energy (kWh)", fontsize=18,fontweight='bold')
ax.legend(fontsize=18, loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=3)
ax.grid(True, linestyle='--', alpha=0.9)
plt.xticks(fontsize=17)
plt.yticks(fontsize=17)
plt.tight_layout()
plt.savefig("SERRES_C_IEEE_Model_vs_Measured_Energy_Comparison.pdf", format='pdf')
plt.show()




------------------------------------------------------------------------------------------------------


#OLD_CODE


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
