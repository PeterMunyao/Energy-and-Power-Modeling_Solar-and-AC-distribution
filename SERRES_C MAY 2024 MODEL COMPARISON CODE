import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pvlib

# Load and prepare satellite-based weather data
file_path = "csv_40.886273_23.912687_fixed_23_180_PT5M.csv"
df = pd.read_csv(file_path)
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

# Filter for December 2024
df = df[(df.index.month == 5) & (df.index.year == 2024)]

# Ensure required columns are present
required_columns = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth',
                    'cloud_opacity', 'relative_humidity', 'wind_speed_10m']
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Column '{col}' is missing. Filling with zeros.")
        df[col] = 0

# System configuration
tilt = 25
azimuth = 180
panel_power_max = 390  # W
system_capacity_kw = 1010.88
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)
inverter_efficiency_pvlib = 0.99
inverter_efficiency_epsm = 0.99
temp_coeff_pvlib = -0.005
temp_coeff_epsm = -0.005
stc_irradiance = 1000  # W/m²

# PVLIB Method
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

# Use SAPM temperature model correctly (no keyword args)
temp_cell = pvlib.temperature.sapm_cell(
    poa_irradiance, df['air_temp'], df['wind_speed_10m'], -3.47, -0.0594, 3
)

dc_power_pvlib = poa_irradiance * num_panels * 0.25 * (1 + temp_coeff_pvlib * (temp_cell - 25))
ac_power_pvlib = dc_power_pvlib * inverter_efficiency_pvlib
df['pvlib_energy_kWh'] = (ac_power_pvlib / 1000).resample('H').mean()
daily_energy_pvlib = df['pvlib_energy_kWh'].resample('D').sum()

# SM-EPSM Method
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

df['dc_power'] = panel_power_max * (1 + temp_coeff_epsm * (df['module_temp'] - nominal_operating_cell_temp))
df['dc_power'] *= df['poa_total'] / stc_irradiance
df['dc_power'] *= (1 - 0.002 * df['relative_humidity'])

df['ac_power'] = df['dc_power'] * inverter_efficiency_epsm
df['scaled_power'] = df['ac_power'] * num_panels
df['actual_power'] = df['scaled_power'] * (1 - 0.01) * (1 - 0.01)

df['epsm_energy_kWh'] = df['actual_power'].resample('H').mean() / 1000
daily_energy_epsm = df['epsm_energy_kWh'].resample('D').sum()

# PVOutput actual data
manual_data = {
    "Date": pd.date_range(start="2024-05-01", end="2024-05-31", freq='D').strftime('%Y-%m-%d'),
    "Generated_kWh": [
        4471.536, 5772.225, 3702.504, 3584.121, 6990.819, 6829.450, 6460.444,
        5794.024, 5301.733, 1044.504, 3872.221, 6579.276, 6007.701, 1795.759, 1705.524,
        1321.289, 6132.768, 6256.532, 4255.149, 5485.074, 5686.328, 6509.426, 6316.062,
        6730.487, 6427.825, 6274.672, 6623.742, 5381.349, 6120.793, 6473.117, 6159.159
    ]
}
pvoutput_df = pd.DataFrame(manual_data)
pvoutput_df['Date'] = pd.to_datetime(pvoutput_df['Date'])
pvoutput_df.set_index('Date', inplace=True)

# Final Plot
plt.rcParams["font.family"] = "Garamond"
plt.figure(figsize=(15, 7))

# Increase line width for all plots
line_width = 3.5

# Plot data
plt.plot(daily_energy_pvlib.index, daily_energy_pvlib, label="PVLIB-Model", linestyle='-', linewidth=line_width, color='orange')
plt.plot(daily_energy_epsm.index, daily_energy_epsm, label="OSM-MEPS-Model", linestyle='--', linewidth=line_width, color='green')
plt.plot(pvoutput_df.index, pvoutput_df['Generated_kWh'], label="SERRES C Measured ", linestyle='-', marker='o', linewidth=line_width, markersize=6, color='blue')

# Labels and title with increased font size
plt.xlabel("Date", fontsize=20)
plt.ylabel("Daily Energy (kWh)", fontsize=20)
plt.title("Serres-C Daily Solar Energy (May 2024): Modeled vs Measured", fontsize=20)

plt.legend(
    fontsize=17,
    loc='upper center',
    bbox_to_anchor=(0.5, -0.15),  # (x, y) position below the plot
    ncol=2,                       # number of legend columns (adjust as needed)
    frameon=False                 # optional: removes the box around the legend
)


# Ticks
plt.xticks(rotation=0, fontsize=18)
plt.yticks(fontsize=18)

# Layout and save
plt.tight_layout()
plt.savefig("SERRES_C_Comparison_PVLIB_OSM-MEPS_PVOutput_2.pdf", format='pdf')
plt.show()



------------------------------------------------


from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# Convert both series to the same timezone (e.g., UTC) or remove timezone information
daily_energy_pvlib.index = daily_energy_pvlib.index.tz_localize(None)  # Remove timezone info if any
daily_energy_epsm.index = daily_energy_epsm.index.tz_localize(None)  # Remove timezone info if any
pvoutput_df.index = pvoutput_df.index.tz_localize(None)  # Ensure PVOutput dataframe has no timezone info

# Ensure both series have the same index (in case of mismatched timestamps)
daily_energy_pvlib_aligned = daily_energy_pvlib.reindex(pvoutput_df.index, method='nearest')
daily_energy_epsm_aligned = daily_energy_epsm.reindex(pvoutput_df.index, method='nearest')

# Error metrics function
def compute_error_metrics(actual, predicted):
    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    return mse, rmse, mae, r2

# PVLIB vs PVOutput
mse_pvlib, rmse_pvlib, mae_pvlib, r2_pvlib = compute_error_metrics(pvoutput_df['Generated_kWh'], daily_energy_pvlib_aligned)
# SM-EPSM vs PVOutput
mse_epsm, rmse_epsm, mae_epsm, r2_epsm = compute_error_metrics(pvoutput_df['Generated_kWh'], daily_energy_epsm_aligned)

# Print the results
print(f"PVLIB vs PVOutput_SERRES-C Metrics: MSE = {mse_pvlib:.3f}, RMSE = {rmse_pvlib:.3f}, MAE = {mae_pvlib:.3f}, R² = {r2_pvlib:.3f}")
print(f"OSM-MEPS vs PVOutput_SERRES-C Metrics: MSE = {mse_epsm:.3f}, RMSE = {rmse_epsm:.3f}, MAE = {mae_epsm:.3f}, R² = {r2_epsm:.3f}")
