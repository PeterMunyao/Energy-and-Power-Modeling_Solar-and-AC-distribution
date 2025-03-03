import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set the font to Garamond
plt.rcParams['font.family'] = 'Garamond'

# Set default font size for better visibility
plt.rcParams.update({'font.size': 14})  # Set default font size for all text elements

# 1. Load the CSV data
file_path = 'csv_-1.11665_36.92927_fixed_23_0_PT5M_2024.csv'  # Path to the CSV file
df = pd.read_csv(file_path)  # Read the CSV data into a DataFrame

# 2. Data Preprocessing
# Convert 'period_end' to datetime objects and set as index
df['period_end'] = pd.to_datetime(df['period_end'])  # Convert the 'period_end' column to datetime
df.set_index('period_end', inplace=True)  # Set 'period_end' as the DataFrame index

# Ensure all required columns are present. Fill missing with 0.
required_columns = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth']  # Required columns for the calculations
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Column '{col}' is missing in CSV. Calculations may be inaccurate.")
        df[col] = 0  # Use 0 as default for missing columns

# 3. System Design Parameters (Example Values - Adjust as needed)
panel_power_max = 350  # Maximum panel power (in Watts)
panel_area = 1.6  # Area of each panel (in m^2)
total_area = 40  # Total available area for solar panels in m^2

# 4. Calculate number of panels based on available area
num_panels = total_area / panel_area  # Total number of panels
num_panels = int(num_panels)  # Round to the nearest whole number

# 5. Calculate system capacity (in Watts and kW)
system_capacity_watts = num_panels * panel_power_max  # Total system capacity in Watts
system_capacity_kw = system_capacity_watts / 1000  # Convert to kW

# Display the system capacity and number of panels
print(f"Number of panels: {num_panels}")
print(f"System capacity: {system_capacity_kw:.2f} kW")

# 6. Filter data for the whole year (January to December)
year_data = df.copy()  # Copy the entire dataset

# 7. Solar Geometry (Simplified - Assumes Fixed Tilt)
surface_tilt = 22.5  # Tilt of the solar panels (in degrees)
surface_azimuth = 90  # Azimuth of the solar panels (in degrees, South-facing)

# Convert angles to radians for calculations
surface_tilt_rad = np.radians(surface_tilt)
surface_azimuth_rad = np.radians(surface_azimuth)
azimuth_rad = np.radians(year_data['azimuth'])
zenith_rad = np.radians(year_data['zenith'])

# Angle of incidence calculation
aoi = np.degrees(np.arccos(np.cos(zenith_rad) * np.cos(surface_tilt_rad) +
                                  np.sin(zenith_rad) * np.sin(surface_tilt_rad) *
                                  np.cos(azimuth_rad - surface_azimuth_rad)))

aoi = np.clip(aoi, 0, 90)  # Clip results as after 90 degrees, power is cut off

# 8. Irradiance Calculations
# Calculate beam irradiance on the tilted surface
year_data['poa_direct'] = year_data['dni'] * np.cos(np.radians(aoi))  # Direct component of irradiance
year_data['poa_direct'] = year_data['poa_direct'].clip(lower=0)  # Ensure values are positive

# Calculate diffuse irradiance on the tilted surface
year_data['poa_diffuse'] = year_data['dhi'] * (1 + np.cos(surface_tilt_rad)) / 2

# Calculate reflected irradiance from the ground on the tilted surface
year_data['poa_sky_diffuse'] = year_data['ghi'] * year_data['albedo'] * (1 - np.cos(surface_tilt_rad)) / 2

# Total irradiance on the tilted surface (sum of all components)
year_data['poa_total'] = year_data['poa_direct'] + year_data['poa_diffuse'] + year_data['poa_sky_diffuse']

# 9. Module Temperature (Simplified)
# Estimate module temperature based on the irradiance and air temperature
nominal_operating_cell_temp = 45  # Nominal operating cell temperature (°C)
year_data['module_temp'] = nominal_operating_cell_temp + year_data['poa_total'] / 800 * (28 - year_data['air_temp'])

# 10. Power Output
# Calculate panel power considering temperature effects
temp_coeff = -0.0045  # Temperature coefficient (%/°C)
year_data['panel_power'] = panel_power_max * (1 + temp_coeff * (year_data['module_temp'] - nominal_operating_cell_temp))
stc_irradiance = 1000  # Standard Test Conditions irradiance (in W/m^2)
year_data['dc_power'] = year_data['panel_power'] * year_data['poa_total'] / stc_irradiance  # DC output

# 11. Inverter
# Calculate AC power using inverter efficiency
inverter_efficiency = 0.85  # Efficiency of the inverter
year_data['ac_power'] = year_data['dc_power'] * inverter_efficiency

# Scale up the power based on the number of panels
year_data['scaled_power'] = year_data['ac_power'] * num_panels

# 12. Calculate 5-minute energy (scaled power * 5 minutes)
year_data['five_min_energy_kwh'] = year_data['scaled_power'] * (5 / 60) / 1000  # Convert from Watts to kW and multiply by 5 minutes

# 13. Calculate the 24-hour energy
# Sum the energy for each 24-hour period
twenty_four_hour_energy = year_data['five_min_energy_kwh'].resample('D').sum()  # Daily energy total (24-hour energy)

# 14. Plotting (Plot 24-hour energy production for the entire year)
plt.figure(figsize=(12, 6))  # Set figure size
plt.plot(twenty_four_hour_energy.index, twenty_four_hour_energy, label="24-Hour Resolution Energy Production (kWh) for 2024")

# Add vertical lines to mark the beginning of each month
for month in range(1, 13):
    plt.axvline(pd.Timestamp(f'2024-{month:02d}-01'), color='gray', linestyle='--', linewidth=1)  # Vertical line at the start of each month

# Labels and title with increased font size
plt.xlabel("Date", fontsize=16)
plt.ylabel("Energy (kWh)", fontsize=16)
plt.title("Njagu_Mhasibu_Estate PV System 24-Hour Resolution Energy Production for 2024", fontsize=18)

# Grid and ticks with improved visibility
plt.grid(True)  # Show grid
plt.legend(fontsize=14)  # Increase legend font size
plt.xticks(fontsize=12, rotation=45)  # Rotate x-tick labels for better visibility and increase font size
plt.yticks(fontsize=12)  # Increase font size for y-ticks

# Tight layout to avoid overlapping elements
plt.tight_layout()

# Save the plot as a PDF file
plt.savefig("NJAGU-MHASIBU_estate_2024_24_hour_energy_with_months.pdf", format="pdf")

# Show the plot
plt.show()

# Display total 24-hour energy produced
total_yearly_energy_kwh = twenty_four_hour_energy.sum()  # Total energy in kWh for the entire year
print(f"Total Yearly Energy (calculated from 5-minute data, summed to 24-hour periods): {total_yearly_energy_kwh:.2f} kWh")
