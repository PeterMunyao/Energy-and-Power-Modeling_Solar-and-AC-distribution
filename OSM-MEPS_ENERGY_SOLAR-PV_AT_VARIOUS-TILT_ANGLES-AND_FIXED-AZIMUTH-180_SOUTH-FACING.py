import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# === Set Garamond font globally ===
plt.rcParams['font.family'] = 'Garamond'
plt.rcParams.update({'font.size': 16})

# === Load and preprocess CSV ===
file_path = 'csv_-1.11665_36.92927_fixed_23_0_PT5M_2024.csv'
df = pd.read_csv(file_path)
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

# === Ensure necessary columns ===
required_columns = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth']
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Column '{col}' is missing. Defaulting to 0.")
        df[col] = 0

# === System Configuration ===
panel_power_max = 350  # Watts
panel_area = 1.6       # m²
total_area = 40        # m²
num_panels = int(total_area / panel_area)
inverter_efficiency = 0.85
stc_irradiance = 1000
tilt_angles = [0, 3, 5, 10, 15, 22.5, 30, 45, 60, 80, 90, 100, 140, 170, 179, 180]
surface_azimuth = 180  # South-facing

# === Compute results ===
energy_results = {}
yearly_energy_kwh_results = {}

for tilt in tilt_angles:
    tilt_rad = np.radians(tilt)
    azimuth_rad = np.radians(df['azimuth'])
    zenith_rad = np.radians(df['zenith'])
    surface_azimuth_rad = np.radians(surface_azimuth)

    aoi = np.degrees(np.arccos(np.cos(zenith_rad) * np.cos(tilt_rad) +
                               np.sin(zenith_rad) * np.sin(tilt_rad) *
                               np.cos(azimuth_rad - surface_azimuth_rad)))
    aoi = np.clip(aoi, 0, 90)

    df['poa_direct'] = df['dni'] * np.cos(np.radians(aoi)).clip(lower=0)
    df['poa_diffuse'] = df['dhi'] * (1 + np.cos(tilt_rad)) / 2
    df['poa_reflected'] = df['ghi'] * df['albedo'] * (1 - np.cos(tilt_rad)) / 2
    df['poa_total'] = df['poa_direct'] + df['poa_diffuse'] + df['poa_reflected']

    df['module_temp'] = 45 + df['poa_total'] / 800 * (28 - df['air_temp'])
    df['panel_power'] = panel_power_max * (1 + (-0.0045) * (df['module_temp'] - 45))
    df['dc_power'] = df['panel_power'] * df['poa_total'] / stc_irradiance
    df['ac_power'] = df['dc_power'] * inverter_efficiency
    df['scaled_power'] = df['ac_power'] * num_panels
    df['energy_kwh'] = df['scaled_power'] * (5 / 60) / 1000  # 5-min to hours, W to kWh

    energy_results[tilt] = df['energy_kwh']
    yearly_energy_kwh_results[tilt] = df['energy_kwh'].sum()

# === Plotting ===
plt.figure(figsize=(13.5, 11), facecolor='#f9f9f9')
ax = plt.gca()
ax.set_facecolor('#f9f9f9')

# ✅ Use colormap with correct syntax
cmap = plt.colormaps.get_cmap('tab20')
colors = [cmap(i / len(tilt_angles)) for i in range(len(tilt_angles))]

line_handles = []
for idx, (tilt, energy) in enumerate(energy_results.items()):
    color = colors[idx]
    line, = ax.plot(
        energy.index,
        energy,
        linewidth=1.8,
        color=color,
        label=f"Tilt {tilt}°"
    )
    line_handles.append((line, f"Tilt {tilt}°: {yearly_energy_kwh_results[tilt]:,.2f} kWh/year"))


# === Axis labels ===
plt.xlabel("Time", fontsize=20, fontweight='bold')
plt.ylabel("Energy (kWh per 5 minutes)", fontsize=20, fontweight='bold')

# === Legend ===
custom_lines = [l for (l, _) in line_handles]
custom_labels = [txt for (_, txt) in line_handles]
plt.legend(custom_lines, custom_labels,
           loc='upper center',
           bbox_to_anchor=(0.5, -0.11),
           ncol=3,
           fontsize=17,
           frameon=False)

# === Grid, layout, export ===
plt.grid(True, linestyle='--', alpha=0.4)
plt.xticks(fontsize=17)
plt.yticks(fontsize=17)
plt.tight_layout(rect=[0, 0.18, 1, 1])  # Leave space for legend
plt.savefig("VARIOUS-TILT-FIXED-AZIMUTH-180.pdf",
            format="pdf", dpi=1000, bbox_inches="tight", pad_inches=0.5)
plt.show()

#--------------------------------------------------------------
#OLD-CODE


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Set Garamond font and font size
plt.rcParams['font.family'] = 'Garamond'
plt.rcParams.update({'font.size': 14})  # Set default font size for all text elements

# Load the CSV data
file_path = 'csv_-1.11665_36.92927_fixed_23_0_PT5M_2024.csv'
df = pd.read_csv(file_path)

# Convert 'period_end' to datetime and set as index
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

# Ensure all required columns exist
required_columns = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth']
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Column '{col}' is missing. Using default value 0.")
        df[col] = 0

# System Design Parameters
panel_power_max = 350  # Watts
panel_area = 1.6  # m^2
total_area = 40  # m^2
num_panels = int(total_area / panel_area)

# Define tilt angles to analyze
tilt_angles = [0, 3, 22.5, 30, 45, 60, 80, 90]
surface_azimuth = 180  # South-facing panels

# Initialize dictionary to store results
energy_results = {}
yearly_energy_kwh_results = {}

for tilt in tilt_angles:
    tilt_rad = np.radians(tilt)
    azimuth_rad = np.radians(df['azimuth'])
    zenith_rad = np.radians(df['zenith'])
    surface_azimuth_rad = np.radians(surface_azimuth)
    
    # Angle of incidence
    aoi = np.degrees(np.arccos(np.cos(zenith_rad) * np.cos(tilt_rad) +
                                np.sin(zenith_rad) * np.sin(tilt_rad) *
                                np.cos(azimuth_rad - surface_azimuth_rad)))
    aoi = np.clip(aoi, 0, 90)
    
    # Irradiance components
    df['poa_direct'] = df['dni'] * np.cos(np.radians(aoi))
    df['poa_direct'] = df['poa_direct'].clip(lower=0)
    df['poa_diffuse'] = df['dhi'] * (1 + np.cos(tilt_rad)) / 2
    df['poa_sky_diffuse'] = df['ghi'] * df['albedo'] * (1 - np.cos(tilt_rad)) / 2
    df['poa_total'] = df['poa_direct'] + df['poa_diffuse'] + df['poa_sky_diffuse']
    
    # Module temperature
    nominal_operating_cell_temp = 45
    df['module_temp'] = nominal_operating_cell_temp + df['poa_total'] / 800 * (28 - df['air_temp'])
    
    # Power output
    temp_coeff = -0.0045
    df['panel_power'] = panel_power_max * (1 + temp_coeff * (df['module_temp'] - nominal_operating_cell_temp))
    stc_irradiance = 1000
    df['dc_power'] = df['panel_power'] * df['poa_total'] / stc_irradiance
    
    # Inverter efficiency
    inverter_efficiency = 0.85
    df['ac_power'] = df['dc_power'] * inverter_efficiency
    df['scaled_power'] = df['ac_power'] * num_panels  # Power in W

    # Convert 5-Minute Power to Energy (kWh)
    df['energy_kwh'] = df['scaled_power'] * (5 / 60) / 1000  # Energy in kWh (5 minutes = 5/60 hour)

    # Store full-resolution energy for plotting
    energy_results[tilt] = df['energy_kwh']
    
    # Calculate total yearly energy in kWh for each tilt
    yearly_energy_kwh = df['energy_kwh'].sum()
    yearly_energy_kwh_results[tilt] = yearly_energy_kwh

# Plot results at 5-minute resolution with default font
plt.figure(figsize=(12, 6))

# Plot each tilt energy production
for tilt, energy in energy_results.items():
    linestyle = '--' if tilt in [22.5, 45, 60, 80] else '-'  # Different styles for different tilts
    plt.plot(energy.index, energy, linestyle, label=f"Tilt {tilt}°")

# Set labels and title
plt.xlabel("Time", fontsize=16)
plt.ylabel("Energy (kWh per 5 minute resolution)", fontsize=16)
plt.title("Energy Production: Year 2024 at Different Tilt Angles (Azimuth 180°) Njagu-Mhasibu-Ruiru Estate", fontsize=16)
plt.grid(True)

# Adjust legend position
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)

# Add yearly energy output below the legend (smaller font size)
text_x_position = 1.05
text_y_position = 0.4  # Adjust this based on your graph's height
for tilt, yearly_energy_kwh in yearly_energy_kwh_results.items():
    plt.text(text_x_position, text_y_position, f"Tilt {tilt}°: {yearly_energy_kwh:.2f} kWh", 
             transform=plt.gca().transAxes, fontsize=10, verticalalignment='bottom')
    text_y_position -= 0.05  # Slightly adjust y-position for next text

plt.subplots_adjust(right=0.8)

# Save and show the plot
plt.savefig("ENERGY_NJAGU_5min_resolution_with_yearly_output.pdf", format="pdf", bbox_inches="tight")
plt.show()
