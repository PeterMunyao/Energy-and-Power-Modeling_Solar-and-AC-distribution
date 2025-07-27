import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === Set font to Garamond ===
plt.rcParams["font.family"] = "Garamond"

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

# System capacity
system_capacity_kw = (num_panels * panel_power_max) / 1000

# Define tilt and azimuth ranges to analyze
tilt_angles = np.arange(0, 91, 5)  # 0 to 90 degrees in steps of 5
azimuth_angles = np.arange(0, 360, 10)  # 90° (East) to 270° (West) in steps of 10

# Initialize dictionary to store energy production
energy_results = {}

# Iterate over tilt and azimuth angles
max_energy = -np.inf
min_energy = np.inf
optimal_tilt, optimal_azimuth = None, None
worst_tilt, worst_azimuth = None, None

for tilt in tilt_angles:
    for azimuth in azimuth_angles:
        tilt_rad = np.radians(tilt)
        azimuth_rad = np.radians(df['azimuth'])
        surface_azimuth_rad = np.radians(azimuth)
        zenith_rad = np.radians(df['zenith'])
        
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
        df['scaled_power'] = df['ac_power'] * num_panels
        
        # Convert to energy in kWh for every 5-minute interval
        energy_kwh = df['scaled_power'] * (5 / 60) / 1000  # Convert 5-minute intervals to hours and calculate energy in kWh
        
        # Store results
        energy_results[(tilt, azimuth)] = energy_kwh
        
        # Calculate total energy production over the whole period
        total_energy = energy_kwh.sum()
        
        # Update max and min energy configurations
        if total_energy > max_energy:
            max_energy = total_energy
            optimal_tilt, optimal_azimuth = tilt, azimuth
            best_energy_profile = energy_kwh
            
        if total_energy < min_energy:
            min_energy = total_energy
            worst_tilt, worst_azimuth = tilt, azimuth
            worst_energy_profile = energy_kwh

# Print optimal and worst configurations
print(f"Optimal Tilt: {optimal_tilt}°, Optimal Azimuth: {optimal_azimuth}°, Max Energy: {max_energy:.2f} kWh")
print(f"Worst Tilt: {worst_tilt}°, Worst Azimuth: {worst_azimuth}°, Min Energy: {min_energy:.2f} kWh")


# Assuming best_energy_profile and worst_energy_profile are already computed from your code

# === Plotting ===
plt.figure(figsize=(11, 6), facecolor='#f9f9f9')  # Set figure background
ax = plt.gca()
ax.set_facecolor('#f9f9f9')  # Set plot area background

# === Plot energy profiles ===
plt.plot(best_energy_profile.index, best_energy_profile, label=f"Max Energy: Tilt {optimal_tilt}°, Azimuth {optimal_azimuth}°",
         color='green', linewidth=2)
plt.plot(worst_energy_profile.index, worst_energy_profile, label=f"Min Energy: Tilt {worst_tilt}°, Azimuth {worst_azimuth}°",
         color='red', linewidth=2)

# === Axis labels ===
plt.xlabel("Date", fontsize=18, fontweight='bold')
plt.ylabel("Energy (kWh per 5 minutes)", fontsize=18, fontweight='bold')

# === Grid and ticks ===
plt.grid(True, linestyle='--', alpha=0.4)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# === Legend ===
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2,
           fontsize=14, framealpha=0.85, title_fontsize=14)

# === No title ===

# === Save and show ===
plt.tight_layout(rect=[1, 0.1, 1, 1])
plt.savefig("NJAGU_OPTIMAL_vs_worst_tilt_azimuth_5min_resolution.pdf",
            format="pdf", dpi=300, bbox_inches="tight", pad_inches=0.5)
plt.show()

#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
#OLD-CODE
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the CSV file containing solar irradiance data
file_path = 'csv_-1.11665_36.92927_fixed_23_0_PT5M_2024.csv'
df = pd.read_csv(file_path)

# Convert 'period_end' column to datetime format for proper time-based indexing
df['period_end'] = pd.to_datetime(df['period_end'], errors='coerce')
df = df.dropna(subset=['period_end'])  # Remove rows where conversion failed (NaT values)
df.set_index('period_end', inplace=True)  # Set 'period_end' as the DataFrame index

# Define the necessary columns for calculations
columns_needed = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth']
for col in columns_needed:
    if col not in df.columns:
        df[col] = 0  # If any column is missing, fill it with zeros
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)  # Convert to numeric and handle NaN values

# Solar panel system parameters
panel_power_max = 390  # Maximum power per panel in watts
panel_area = 1.6  # Area of a single panel in square meters
total_area = 40  # Total available area for panels in square meters
num_panels = total_area / panel_area  # Calculate the total number of panels
system_capacity_kw = (num_panels * panel_power_max) / 1000  # Convert total system power to kW

# Convert angles from degrees to radians for calculations
df['zenith_rad'] = np.radians(df['zenith'])
df['azimuth_rad'] = np.radians(df['azimuth'])

# Define panel orientation parameters
surface_tilt = np.radians(25)  # Panel tilt angle in radians
surface_azimuth = np.radians(180)  # Panel azimuth (facing due south)

# Calculate the Angle of Incidence (AOI) using the formula
df['aoi'] = np.degrees(np.arccos(
    np.cos(df['zenith_rad']) * np.cos(surface_tilt) +
    np.sin(df['zenith_rad']) * np.sin(surface_tilt) * np.cos(df['azimuth_rad'] - surface_azimuth)
))
df['aoi'] = np.clip(df['aoi'], 0, 90)  # Limit AOI to the range [0, 90] degrees

# Compute Plane of Array (POA) irradiance
# Direct irradiance component
df['poa_direct'] = df['dni'] * np.cos(np.radians(df['aoi']))
df['poa_direct'] = df['poa_direct'].clip(lower=0)  # Ensure no negative values

# Diffuse irradiance components
df['poa_diffuse'] = df['dhi'] * (1 + np.cos(surface_tilt)) / 2  # Sky diffuse
df['poa_sky_diffuse'] = df['ghi'] * df['albedo'] * (1 - np.cos(surface_tilt)) / 2  # Ground reflected

df['poa_total'] = df['poa_direct'] + df['poa_diffuse'] + df['poa_sky_diffuse']  # Total POA irradiance

# Estimate module temperature using the NOCT model
nominal_operating_cell_temp = 45  # Nominal Operating Cell Temperature (NOCT) in °C
df['module_temp'] = nominal_operating_cell_temp + df['poa_total'] / 800 * (28 - df['air_temp'])

# Calculate power output considering temperature effects
temp_coeff = -0.0045  # Power temperature coefficient per °C
df['panel_power'] = panel_power_max * (1 + temp_coeff * (df['module_temp'] - nominal_operating_cell_temp))
stc_irradiance = 1000  # Standard Test Conditions (STC) irradiance in W/m²
df['dc_power'] = df['panel_power'] * df['poa_total'] / stc_irradiance  # DC power output

# Convert to AC power using inverter efficiency
inverter_efficiency = 0.86  # Efficiency factor
df['ac_power'] = df['dc_power'] * inverter_efficiency

df['scaled_power'] = df['ac_power'] * num_panels  # Total system output power

# Ensure the DataFrame index is in datetime format
df.index = pd.to_datetime(df.index, errors='coerce')
df = df.dropna(subset=['scaled_power'])  # Remove rows where power calculation failed (NaN values)

# Remove January data (only plotting February to December)
df = df[df.index.month != 1]

# Create a figure with subplots for each month (2 months per row, 6 rows total)
fig, axes = plt.subplots(6, 2, figsize=(15, 20), sharey=True)
fig.suptitle("Monthly Power Output for February-December 2024 (kW), Location: -1.11665, 36.92927 at 5 Min Resolution", fontsize=14, fontweight="bold")

# Loop through months (February to December)
months_to_plot = list(range(2, 13))  # Months 2 to 12

# Initialize min and max values for y-axis scaling
min_value = float('inf')
max_value = float('-inf')

# First, loop through all months to find the overall min and max power values
for i, month in enumerate(months_to_plot):
    month_data = df[df.index.month == month]  # Filter data for the current month

    if not month_data.empty:
        # Calculate min and max scaled power for current month
        min_value = min(min_value, month_data['scaled_power'].min())
        max_value = max(max_value, month_data['scaled_power'].max())

# Now loop again to plot the data with the fixed y-axis scale
for i, month in enumerate(months_to_plot):
    ax = axes[i // 2, i % 2]  # Determine subplot position (2 months per row)
    month_data = df[df.index.month == month]  # Filter data for the current month

    if not month_data.empty:
        ax.plot(month_data.index, month_data['scaled_power'] / 1000, color='red', label=f'Month {month}')  # Plot power output
        ax.set_title(month_data.index[0].strftime('%B'), fontsize=12, fontweight="bold")  # Set subplot title to month name
    else:
        ax.set_title(pd.to_datetime(f'2024-{month}-01').strftime('%B'), fontsize=12, fontweight="bold")  # Set title if no data

    # Configure x-axis to show each day while maintaining 5-minute resolution
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Show each day
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))  # Display day numbers
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=89, fontsize=6)  # Rotate labels for better readability and adjust font size and weight

    ax.set_ylabel('Power Output (kW)', fontsize=11, fontweight='bold')  # Add y-axis label

    # Set the same y-axis limits for all subplots
    ax.set_ylim(min_value / 1000, max_value / 1000)  # Scale power in kW

    ax.grid(True, linestyle='--', alpha=0.9)  # Add grid lines for readability
    ax.legend(loc="lower left", fontsize=5)  # Add legend

# Hide any unused subplot (if necessary, based on the number of months)
axes[5, 1].axis("off")

plt.tight_layout(rect=[0, 0.03, 1, 0.94])  # Adjust layout to prevent overlapping

# Save the figure as a PDF
pdf_path = 'solar_power_output_2024.pdf'
plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
plt.close()  # Close the plot to avoid displaying it in interactive mode

print(f"PDF saved at {pdf_path}")
