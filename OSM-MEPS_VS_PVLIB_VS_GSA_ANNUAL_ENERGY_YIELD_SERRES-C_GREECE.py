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

#dc_power_pvlib = poa_irradiance * num_panels * 0.25 * (1 + temp_coeff * (temp_cell - 25))
dc_power_pvlib = poa_irradiance / stc_irradiance * num_panels * panel_power_max * (1 + temp_coeff * (temp_cell - 25))
ac_power_pvlib = dc_power_pvlib * inverter_efficiency
df['pvlib_energy_kWh'] = (ac_power_pvlib / 1000).resample('h').mean()
daily_energy_pvlib = df['pvlib_energy_kWh'].resample('D').sum()

# === OSM-MEPS MODEL ===
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
df['dc_power'] *= (1 - 0.0002 * df['relative_humidity']) #Environmental derating (humidity)
df['ac_power'] = df['dc_power'] * inverter_efficiency_epsm
df['scaled_power'] = df['ac_power'] * num_panels
df['actual_power'] = df['scaled_power'] * (1 - 0.05) # dust and soiling-site dependent empirical coefficient

# Mask for May to August
april_to_sep_mask = df.index.month.isin([4,5, 6, 7, 8,9])

# Apply extra derating only for April to September
df.loc[april_to_sep_mask, 'actual_power'] *= (1 - 0.15) # Post-system empirical loss factors (cables, mismatch)

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
plt.savefig("Figure_16.pdf", format='pdf')
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
