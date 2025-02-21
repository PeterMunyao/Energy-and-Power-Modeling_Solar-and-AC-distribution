import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pytz

# Load the CSV file
file_path = 'csv_-1.11665_36.92927_fixed_23_0_PT5M_2024.csv'
df = pd.read_csv(file_path)

# Convert 'period_end' column to datetime with UTC handling
df['period_end'] = pd.to_datetime(df['period_end'], errors='coerce', utc=True)
df = df.dropna(subset=['period_end'])  # Remove rows where period_end is NaT
df.set_index('period_end', inplace=True)

# Convert UTC to Kenyan Time (EAT, UTC +3)
kenya_time_zone = pytz.timezone('Africa/Nairobi')
df.index = df.index.tz_convert('UTC').tz_localize(None).tz_localize(kenya_time_zone)

# Ensure required numeric columns exist
columns_needed = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth']
for col in columns_needed:
    if col not in df.columns:
        df[col] = 0  # Fill missing columns with zeros
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)  # Convert and handle NaNs

# Solar Panel Parameters
panel_power_max = 390  # W per panel
panel_area = 1.6  # m² per panel
total_area = 40  # m² total
num_panels = total_area / panel_area
system_capacity_kw = (num_panels * panel_power_max) / 1000

# Convert angles to radians
df['zenith_rad'] = np.radians(df['zenith'])
df['azimuth_rad'] = np.radians(df['azimuth'])

# Define panel orientation
surface_tilt = np.radians(25)  # Convert to radians
surface_azimuth = np.radians(180)

# Calculate Angle of Incidence (AOI)
df['aoi'] = np.degrees(np.arccos(
    np.cos(df['zenith_rad']) * np.cos(surface_tilt) +
    np.sin(df['zenith_rad']) * np.sin(surface_tilt) * np.cos(df['azimuth_rad'] - surface_azimuth)
))
df['aoi'] = np.clip(df['aoi'], 0, 90)

# POA Irradiance Calculations
df['poa_direct'] = df['dni'] * np.cos(np.radians(df['aoi']))
df['poa_direct'] = df['poa_direct'].clip(lower=0)
df['poa_diffuse'] = df['dhi'] * (1 + np.cos(surface_tilt)) / 2
df['poa_sky_diffuse'] = df['ghi'] * df['albedo'] * (1 - np.cos(surface_tilt)) / 2
df['poa_total'] = df['poa_direct'] + df['poa_diffuse'] + df['poa_sky_diffuse']

# Module Temperature Calculation
nominal_operating_cell_temp = 45
df['module_temp'] = nominal_operating_cell_temp + df['poa_total'] / 800 * (28 - df['air_temp'])

# Power Output Calculation
temp_coeff = -0.0045
df['panel_power'] = panel_power_max * (1 + temp_coeff * (df['module_temp'] - nominal_operating_cell_temp))
stc_irradiance = 1000
df['dc_power'] = df['panel_power'] * df['poa_total'] / stc_irradiance

# Inverter Efficiency
inverter_efficiency = 0.86
df['ac_power'] = df['dc_power'] * inverter_efficiency
df['scaled_power'] = df['ac_power'] * num_panels

# Ensure index is in datetime format
df.index = pd.to_datetime(df.index, errors='coerce', utc=True)
df = df.dropna(subset=['scaled_power'])  # Ensure no NaN values in scaled_power

# Filter for January data (handling UTC correctly)
df_january = df[df.index.month == 1]

# Plot January's Power Output
plt.figure(figsize=(8, 4))  # Smaller figure size
plt.plot(df_january.index, df_january['scaled_power'] / 1000, color='red', label="Power Output (kW)")  # Brown color

# Formatting
plt.title("January", fontsize=14, fontweight="bold")
plt.xlabel("Date", fontsize=12, fontweight="bold")
plt.ylabel("Power Output (kW)", fontsize=12, fontweight="bold")
plt.xticks(rotation=0)
plt.grid(True, linestyle='--', alpha=0.6)



# Format x-axis to show day of the month
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d'))

# Save the plot as a PDF
plt.tight_layout()
plt.savefig('Njagu_january_2024.pdf', format='pdf')

# Show the plot
plt.show()
