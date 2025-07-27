import pandas as pd
import numpy as np
import pvlib
import matplotlib.pyplot as plt
from pvlib.irradiance import get_total_irradiance
from pvlib.temperature import sapm_cell

# Load CSV data
file_path = "csv_40.886273_23.912687_fixed_23_180_PT5M.csv"
df = pd.read_csv(file_path, parse_dates=["period_end"], index_col="period_end")

# Extract necessary weather data
ghi = df["ghi"]  # Global Horizontal Irradiance (W/m²)
dni = df["dni"]  # Direct Normal Irradiance (W/m²)
dhi = df["dhi"]  # Diffuse Horizontal Irradiance (W/m²)
temp_amb = df["air_temp"]  # Ambient Temperature (°C)
wind_speed = df["wind_speed_10m"]  # Wind Speed (m/s)

# System Parameters
tilt = 25  # Panel tilt angle (degrees)
azimuth = 180  # South-facing panels
panel_power_max = 390  # W per panel
system_capacity_kw = 1010.88  # System capacity in kW
system_capacity_w = system_capacity_kw * 1000
num_panels = int(system_capacity_w / panel_power_max)
efficiency_stc = 0.24  # Assuming 24% efficiency at STC
temp_coeff = -0.004  # Power temperature coefficient (%/°C)
inverter_efficiency = 0.99  # Inverter efficiency (99%)
losses = 1  # Total losses factor (soiling, mismatch, wiring, etc.)

# Calculate POA irradiance
solar_position = pvlib.solarposition.get_solarposition(df.index, 40.886273, 23.912687)
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

# Cell Temperature Calculation
temp_cell = sapm_cell(poa_irradiance, temp_amb, wind_speed, -3.47, -0.0594, 3)

# DC Power Output Calculation
dc_power = poa_irradiance * num_panels * efficiency_stc * (1 + temp_coeff * (temp_cell - 25))

# AC Power Output with Losses
ac_power = dc_power * inverter_efficiency * losses

df["AC_Power_kW"] = ac_power / 1000  # Convert to kW

# Energy Calculation (5-minute intervals to hourly energy)
df["Energy_kWh"] = df["AC_Power_kW"].resample('H').mean()  # Hourly energy in kWh

df["Daily_Energy_kWh"] = df["Energy_kWh"].resample('D').sum()  # Daily energy in kWh
df["Monthly_Energy_MWh"] = df["Daily_Energy_kWh"].resample('M').sum() / 1000  # Monthly energy in MWh

# Total Energy Output for the Year
total_energy_mwh = df["Daily_Energy_kWh"].sum() / 1000  # Convert to MWh
print(f"Total Energy Output for 2024: {total_energy_mwh:.2f} MWh")

# Capacity Factor Calculation
cf = df["AC_Power_kW"].sum() / (system_capacity_kw * len(df) * 5 / 60)  # 5-minute intervals
print(f"Capacity Factor: {cf:.2%}")

# Set Garamond font
plt.rcParams["font.family"] = "Garamond"

# Plot Monthly Energy Output
plt.figure(figsize=(12, 5))
df["Monthly_Energy_MWh"].dropna().plot(kind="bar", color="blue")
plt.xlabel("Month")
plt.ylabel("Energy (MWh)")
plt.title("Monthly Energy Production for Serres C using pvlib (2024)")
plt.grid(axis="y", linestyle="--", linewidth=0.5)
plt.xticks(rotation=45)
plt.savefig("PVLIB_NJAGU_monthly_energy_2024.pdf", format="pdf")
plt.show()

# Save results
df.to_csv("solar_power_output_2024.csv")
