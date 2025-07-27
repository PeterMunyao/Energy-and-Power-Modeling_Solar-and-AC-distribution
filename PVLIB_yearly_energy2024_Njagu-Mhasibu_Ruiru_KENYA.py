import pandas as pd
import numpy as np
import pvlib
import matplotlib.pyplot as plt
from pvlib.irradiance import get_total_irradiance
from pvlib.temperature import sapm_cell

# 1. Load the CSV data
file_path = 'csv_-1.11665_36.92927_fixed_23_0_PT5M_2024.csv'  # Path to the CSV file
df = pd.read_csv(file_path)  # Read the CSV data into a DataFrame

# 2. Data Preprocessing
# Convert 'period_end' to datetime objects and set as index
df['period_end'] = pd.to_datetime(df['period_end'])  # Convert the 'period_end' column to datetime
df.set_index('period_end', inplace=True)  # Set 'period_end' as the DataFrame index

# 3. Extract necessary weather data
ghi = df["ghi"]  # Global Horizontal Irradiance (W/m²)
dni = df["dni"]  # Direct Normal Irradiance (W/m²)
dhi = df["dhi"]  # Diffuse Horizontal Irradiance (W/m²)
temp_amb = df["air_temp"]  # Ambient Temperature (°C)
wind_speed = df["wind_speed_10m"]  # Wind Speed (m/s)

# 4. System Parameters
tilt = 25  # Panel tilt angle (degrees)
azimuth = 90  # South-facing panels
panel_power_max = 350  # W per panel
system_capacity_kw = 8.75  # System capacity in kW
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)
efficiency_stc = 0.25  # Assuming the panel has 24% efficiency at STC
temp_coeff = -0.004  # Power temperature coefficient (%/°C)
inverter_efficiency = 0.975  # Inverter efficiency (87%)
losses = 1  # Total losses factor (soiling, mismatch, wiring, etc.)

# 5. Calculate POA irradiance using `pvlib`
latitude = 36.92927  # Latitude of the location
longitude = -1.11665  # Longitude of the location
solar_position = pvlib.solarposition.get_solarposition(df.index, latitude, longitude)

poa = get_total_irradiance(
    surface_tilt=tilt,
    surface_azimuth=azimuth,
    dni=dni,
    ghi=ghi,
    dhi=dhi,
    solar_zenith=solar_position["apparent_zenith"],
    solar_azimuth=solar_position["azimuth"],
)
poa_irradiance = poa["poa_global"]

# 6. Cell Temperature Calculation using `pvlib`
temp_cell = sapm_cell(poa_irradiance, temp_amb, wind_speed, -3.47, -0.0594, 3)

# 7. DC Power Output Calculation
dc_power = poa_irradiance * num_panels * efficiency_stc * (1 + temp_coeff * (temp_cell - 25))

# 8. AC Power Output with Losses
ac_power = dc_power * inverter_efficiency * losses

df["AC_Power_kW"] = ac_power / 1000  # Convert to kW

# 9. Energy Calculation (5-minute intervals to hourly energy)
df["Energy_kWh"] = df["AC_Power_kW"].resample('H').mean()  # Hourly energy in kWh

# 10. Calculate Daily Energy Output
df["Daily_Energy_kWh"] = df["Energy_kWh"].resample('D').sum()  # Sum of hourly energy for each day

# 11. Total Energy Output for 2024
total_energy_2024_kWh = df["Energy_kWh"].sum()  # Total energy for 2024 in kWh

print(f"Total Energy Output for 2024: {total_energy_2024_kWh:.2f} kWh")

# 12. Capacity Factor Calculation
cf = df["AC_Power_kW"].sum() / (system_capacity_kw * len(df) * 5 / 60)  # 5-minute intervals

print(f"Capacity Factor: {cf:.2%}")

# 13. Set Garamond font for plotting
plt.rcParams["font.family"] = "Garamond"

# 14. Plot Daily Energy Output for 2024 as a line graph and save as PDF
plt.figure(figsize=(12, 5))
plt.plot(df["Daily_Energy_kWh"].dropna().index, df["Daily_Energy_kWh"].dropna(), label="Daily Energy (kWh)", linestyle='-', color='orange')
plt.xlabel("Date", fontsize=16)
plt.ylabel("Energy (kWh)", fontsize=16)
plt.title("Daily Energy Production for Location (-1.11665, 36.92927) using pvlib (2024)", fontsize=16)
plt.legend()
plt.grid()
plt.savefig("daily_energy_2024.pdf", format="pdf")
plt.show()

# 15. Save results
df.to_csv("solar_power_output_2024_location.csv")
