import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pvlib

# === Load and prepare satellite-based weather data ===
file_path = "csv_-34.9599769_138.6414601_fixed_22.5_270_PT5M.csv"
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
tilt = 22.5
azimuth = 270
panel_power_max = 185 # W
system_capacity_kw = 10.175
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)
inverter_efficiency = 0.97
temp_coeff = -0.0034
stc_irradiance = 1000  # W/m²

# === PVLIB Method ===
solar_position = pvlib.solarposition.get_solarposition(df.index, -34.9599769, 138.6414601)
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

#old line: dc_power_pvlib = poa_irradiance * num_panels * 0.25 * (1 + temp_coeff * (temp_cell - 25))
dc_power_pvlib = poa_irradiance / stc_irradiance * num_panels * panel_power_max * (1 + temp_coeff * (temp_cell - 25))
ac_power_pvlib = dc_power_pvlib * inverter_efficiency
df['pvlib_energy_kWh'] = (ac_power_pvlib / 1000).resample('h').mean()
daily_energy_pvlib = df['pvlib_energy_kWh'].resample('D').sum()

# === osm-meps Method ===
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
cos_aoi = np.cos(np.radians(aoi))
cos_aoi[cos_aoi < 0] = 0
df['poa_direct'] = df['dni'] * cos_aoi * (1 - df['cloud_opacity'] / 100)
df['poa_direct'] = df['poa_direct'].clip(lower=0)
df['poa_diffuse'] = df['dhi'] * (1 + np.cos(tilt_rad)) / 2
df['poa_sky_diffuse'] = df['ghi'] * df['albedo'] * (1 - np.cos(tilt_rad)) / 2
df['poa_total'] = df['poa_direct'] + df['poa_diffuse'] + df['poa_sky_diffuse']

nominal_operating_cell_temp = 45
df['module_temp'] = nominal_operating_cell_temp + df['poa_total'] / 1000 * (28 - df['air_temp'])

df['dc_power'] = panel_power_max * (1 + temp_coeff * (df['module_temp'] - nominal_operating_cell_temp))
df['dc_power'] *= df['poa_total'] / stc_irradiance
df['dc_power'] *= (1 - 0.002 * df['relative_humidity'])

df['ac_power'] = df['dc_power'] * inverter_efficiency
df['scaled_power'] = df['ac_power'] * num_panels
df['actual_power'] = df['scaled_power'] * (1 - 0.01) 

# Replace mean() with sum() and apply correct scaling for 5-minute intervals
df['epsm_energy_kWh'] = df['actual_power'] * (5 / 60) / 1000
hourly_energy_epsm = df['epsm_energy_kWh'].resample('h').sum()
daily_energy_epsm = df['epsm_energy_kWh'].resample('D').sum()

# === Load PVOutput actual data ===
pvoutput_actual = pd.read_csv("GLEN_sorted.csv")
pvoutput_actual['Date'] = pd.to_datetime(pvoutput_actual['Date'], dayfirst=False)
pvoutput_actual.set_index('Date', inplace=True)
pvoutput_actual['Generated_kWh'] = pd.to_numeric(pvoutput_actual['Generated_kWh'], errors='coerce')
pvoutput_actual = pvoutput_actual.dropna()

# === Plot: Model vs PVOutput Daily Energy ===
plt.rcParams["font.family"] = "Garamond"

# Create the figure and axis objects with light background
fig, ax = plt.subplots(figsize=(13, 6), facecolor='#f9f9f9')
ax.set_facecolor('#f9f9f9')

# Plot models without markers
ax.plot(daily_energy_pvlib.index, daily_energy_pvlib, label="PVLIB-Model", linestyle='-', linewidth=3, color='orange')
ax.plot(daily_energy_epsm.index, daily_energy_epsm, label="OSM-MEPS Model", linestyle='-', linewidth=3, color='green')

# Plot measured data (no markers)
if not pvoutput_actual.empty:
    measured = pvoutput_actual['Generated_kWh'].dropna()
    ax.plot(
        measured.index,
        measured,
        label="367 Glen Osmond Rooftop PV Output Energy (Measured)",
        linestyle='-',
        linewidth=3,
        color='blue'
    )

# Axis labels with bold formatting
ax.set_xlabel("Date", fontsize=18, fontweight='bold')
ax.set_ylabel("Daily Energy (kWh)", fontsize=18, fontweight='bold')

# Remove title as requested
# ax.set_title("367 Glen Osmond Rooftop PV Output Energy (2024): Modeled vs Measured", fontsize=20)

# Legend styling
ax.legend(fontsize=15.5, loc='lower center', bbox_to_anchor=(0.5, -0.28), ncol=3, frameon=False)

# Dotted grid, tick size
ax.grid(True, linestyle=':', linewidth=0.8, color='gray')
ax.tick_params(axis='both', labelsize=15)

# Layout and save
plt.tight_layout()
plt.savefig("367_Glen_Osmond_Final_Rooftop_PV_Output_Energy.pdf", format='pdf', facecolor=fig.get_facecolor())

# Show plot
plt.show()


#------------------------


from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Align time indexes
measured = pvoutput_actual['Generated_kWh'].dropna()
common_index = measured.index.intersection(daily_energy_pvlib.index)

# Extract aligned series
measured = measured[common_index]
pvlib_pred = daily_energy_pvlib[common_index]
epsm_pred = daily_energy_epsm[common_index]

# === Define function to calculate error metrics ===
def compute_errors(true, pred):
    mae = mean_absolute_error(true, pred)
    rmse = np.sqrt(mean_squared_error(true, pred))
    mbe = np.mean(pred - true)
    r2 = r2_score(true, pred)
    return mae, rmse, mbe, r2

# Calculate for each model
pvlib_errors = compute_errors(measured, pvlib_pred)
epsm_errors = compute_errors(measured, epsm_pred)

# Prepare for plotting
metrics = ['MAE', 'RMSE', 'MBE', 'R²']
pvlib_values = pvlib_errors
epsm_values = epsm_errors

x = np.arange(len(metrics))
width = 0.35

# === Plot Error Metrics ===
fig, ax = plt.subplots(figsize=(11, 6), facecolor='#f0f0f0')
ax.set_facecolor('#f0f0f0')

bar1 = ax.bar(x - width/2, pvlib_values, width, label='PVLIB-Model', color='orange')
bar2 = ax.bar(x + width/2, epsm_values, width, label='OSM-MEPS Model', color='green')
# === Print the error metric values ===
print("Error Metrics Comparison (Model vs Measured PVOutput)")
print("-" * 60)
print(f"{'Metric':<10} | {'PVLIB-Model':>12} | {'OSM-MEPS Model':>15}")
print("-" * 60)
for i, metric in enumerate(metrics):
    print(f"{metric:<10} | {pvlib_values[i]:>12.3f} | {epsm_values[i]:>15.3f}")
print("-" * 60)

# Annotate bars
for bars in [bar1, bar2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', fontsize=12)

# Labels
ax.set_ylabel('Error Value', fontsize=16)
ax.set_title('Model Error Metrics vs Measured Daily PVOutput (2024)', fontsize=18)
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=15)
ax.legend(fontsize=14)
ax.grid(axis='y', linestyle='--', alpha=0.8)

plt.tight_layout()
plt.savefig("367_Glen_Osmond_Model_Error_Metrics_Comparison.pdf", format='pdf')
plt.show()
