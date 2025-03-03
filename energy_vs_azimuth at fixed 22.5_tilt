import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the CSV data
file_path = 'csv_-1.11665_36.92927_fixed_23_0_PT5M_2024.csv'
df = pd.read_csv(file_path)
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

# Ensure required columns are present
required_columns = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth']
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Column '{col}' is missing in CSV.")
        df[col] = 0  

# System Parameters
panel_power_max = 350  
panel_area = 1.6  
total_area = 40  
num_panels = int(total_area / panel_area)  
system_capacity_kw = (num_panels * panel_power_max) / 1000  

# Azimuth angles to simulate
azimuth_angles = [0, 3, 10, 45, 80, 90, 100, 135, 180, 350]
tilt_angle = 22.5  

# Energy storage dictionary
energy_outputs = {}
yearly_energy_kwh_results = {}

for azimuth in azimuth_angles:
    surface_tilt_rad = np.radians(tilt_angle)
    surface_azimuth_rad = np.radians(azimuth)
    azimuth_rad = np.radians(df['azimuth'])
    zenith_rad = np.radians(df['zenith'])

    # Angle of Incidence
    aoi = np.degrees(np.arccos(np.cos(zenith_rad) * np.cos(surface_tilt_rad) +
                                np.sin(zenith_rad) * np.sin(surface_tilt_rad) *
                                np.cos(azimuth_rad - surface_azimuth_rad)))
    aoi = np.clip(aoi, 0, 90)

    # Irradiance Calculations
    df['poa_direct'] = df['dni'] * np.cos(np.radians(aoi))
    df['poa_direct'] = df['poa_direct'].clip(lower=0)

    df['poa_diffuse'] = df['dhi'] * (1 + np.cos(surface_tilt_rad)) / 2
    df['poa_sky_diffuse'] = df['ghi'] * df['albedo'] * (1 - np.cos(surface_tilt_rad)) / 2
    df['poa_total'] = df['poa_direct'] + df['poa_diffuse'] + df['poa_sky_diffuse']

    # Module Temperature
    nominal_operating_cell_temp = 45  
    df['module_temp'] = nominal_operating_cell_temp + df['poa_total'] / 800 * (28 - df['air_temp'])

    # Power Output
    temp_coeff = -0.0045  
    df['panel_power'] = panel_power_max * (1 + temp_coeff * (df['module_temp'] - nominal_operating_cell_temp))
    df['dc_power'] = df['panel_power'] * df['poa_total'] / 1000  
    df['ac_power'] = df['dc_power'] * 0.85  
    df['scaled_power'] = df['ac_power'] * num_panels  

    # Convert 5-Minute Power to Energy (kWh)
    df['energy_kwh'] = df['scaled_power'] * (5 / 60) / 1000  # Energy in kWh (5 minutes = 5/60 hour)
    
    # Resample to 1440-minute resolution for visibility (24 hours)
    energy_resampled_kwh = df['energy_kwh'].resample('1440T').sum()  # 1440 minutes = 24 hours
    energy_outputs[azimuth] = energy_resampled_kwh

    # Calculate total yearly energy in kWh for each azimuth
    yearly_energy_kwh = energy_resampled_kwh.sum()
    yearly_energy_kwh_results[azimuth] = yearly_energy_kwh

# Plot results at 1440-minute resolution with default font
plt.figure(figsize=(12, 6))

# Plot each azimuth energy production
for azimuth in azimuth_angles:
    linestyle = '--' if azimuth in [0, 3, 10, 45, 80, 90, 100, 135, 180, 350] else '-'  # Dotted lines for specific azimuths
    plt.plot(energy_outputs[azimuth].index, energy_outputs[azimuth], linestyle, label=f"Azimuth {azimuth}°")

# Set labels and title
plt.xlabel("Time", fontsize=16)
plt.ylabel("Energy (kWh)", fontsize=16)
plt.title("Daily Energy Production at Various Azimuth Angles ( Tilt = 22.5° )", fontsize=16)
plt.grid(True)

# Adjust legend position
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)

# Add yearly energy output below the legend (smaller font size)
text_x_position = 1.05
text_y_position = 0.33  # Adjust this based on your graph's height
for azimuth, yearly_energy_kwh in yearly_energy_kwh_results.items():
    plt.text(text_x_position, text_y_position, f"Azimuth {azimuth}°: {yearly_energy_kwh:.2f} kWh", 
             transform=plt.gca().transAxes, fontsize=10, verticalalignment='bottom')
    text_y_position -= 0.05  # Slightly adjust y-position for next text

plt.subplots_adjust(right=0.8)  # Shift plot left to fit legend

# Save and show the plot
plt.savefig("ENergy_vs_AZIMUTH_22.5_tilt_1440min_resolution.pdf", format="pdf", bbox_inches="tight")
plt.show()
