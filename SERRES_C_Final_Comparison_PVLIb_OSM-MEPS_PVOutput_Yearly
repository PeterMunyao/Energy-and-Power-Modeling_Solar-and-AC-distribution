import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pvlib

# === Load and prepare satellite-based weather data ===
file_path = "csv_40.886273_23.912687_fixed_23_180_PT5M.csv"
df = pd.read_csv(file_path)
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

# === Filter for the full year 2024 ===
df = df[df.index.year == 2024]

# === Ensure required columns are present ===
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

# SAPM temperature model
temp_cell = pvlib.temperature.sapm_cell(
    poa_irradiance, df['air_temp'], df['wind_speed_10m'], -3.47, -0.0594, 3
)

dc_power_pvlib = poa_irradiance * num_panels * 0.25 * (1 + temp_coeff * (temp_cell - 25))
ac_power_pvlib = dc_power_pvlib * inverter_efficiency
df['pvlib_energy_kWh'] = (ac_power_pvlib / 1000).resample('H').mean()
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

nominal_operating_cell_temp = 45
df['module_temp'] = nominal_operating_cell_temp + df['poa_total'] / 800 * (28 - df['air_temp'])

df['dc_power'] = panel_power_max * (1 + temp_coeff * (df['module_temp'] - nominal_operating_cell_temp))
df['dc_power'] *= df['poa_total'] / stc_irradiance
df['dc_power'] *= (1 - 0.002 * df['relative_humidity'])

df['ac_power'] = df['dc_power'] * inverter_efficiency
df['scaled_power'] = df['ac_power'] * num_panels
df['actual_power'] = df['scaled_power'] * (1 - 0.01) * (1 - 0.01)

df['epsm_energy_kWh'] = df['actual_power'].resample('H').mean() / 1000
daily_energy_epsm = df['epsm_energy_kWh'].resample('D').sum()

# === Load PVOutput actual data ===
pvoutput_actual = pd.read_csv("serres_2024_full_dataset.csv")
pvoutput_actual['Date'] = pd.to_datetime(pvoutput_actual['Date'], dayfirst=False)
pvoutput_actual.set_index('Date', inplace=True)

pvoutput_actual['Generated_kWh'] = pd.to_numeric(pvoutput_actual['Generated_kWh'], errors='coerce')
pvoutput_actual = pvoutput_actual.dropna()

# === Plot: Model vs PVOutput Daily Energy ===
plt.rcParams["font.family"] = "Garamond"
plt.figure(figsize=(13, 6))

plt.plot(daily_energy_pvlib.index, daily_energy_pvlib, label="PVLIB-Model", linestyle='-', linewidth=3, color='orange')
plt.plot(daily_energy_epsm.index, daily_energy_epsm, label="OSM-MEPS Model", linestyle='--', linewidth=3, color='green')

if not pvoutput_actual.empty:
    measured = pvoutput_actual['Generated_kWh'].dropna()
    plt.plot(
        measured.index, 
        measured, 
        label="Serres-C PV Power Plant Output Energy (Measured)", 
        linestyle='-', 
        marker='o', 
        linewidth=3, 
        color='blue'
    )

plt.xlabel("Date", fontsize=18)
plt.ylabel("Daily Energy (kWh)", fontsize=18)
plt.title("Serres-C Daily Solar Energy (2024): Modelled vs Measured", fontsize=20)
plt.legend(fontsize=17, loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=3)

plt.grid(True, linestyle='--', alpha=0.95)
plt.xticks(rotation=0, fontsize=16)
plt.yticks(fontsize=16)
plt.tight_layout()
plt.savefig("SERRES_C_Final_Comparison_PVLIB_EPSM_PVOutput_Yearly.pdf", format='pdf')
plt.show()

# === Bar Plot: GSA Monthly Totals ===
gsa_data = {
    'Month': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
    'Days': [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
    'Avg_Daily_kWh': [2549, 3344, 4075, 4664, 5159, 5543, 5741, 5454, 4629, 3615, 2622, 2189]
}
gsa_df['Total_Monthly_MWh'] = gsa_df['Total_Monthly_kWh'] / 1000

plt.figure(figsize=(13, 6))
plt.bar(gsa_df['Month'], gsa_df['Total_Monthly_MWh'], color='maroon', width=0.5, edgecolor='black')
plt.title("Monthly Solar Energy for Serres-C using GSA", fontsize=20)
plt.xlabel("Month", fontsize=18)
plt.ylabel("Total Monthly Energy (MWh)", fontsize=18)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("GSA_Final_Averaged_Monthly_Solar_Energy_Barplot_MWh.pdf", format='pdf')
plt.show()
