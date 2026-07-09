# ==========================================================
# Assuming horizontal array
# ==========================================================
# Garamond IEEE Publication Style
# ==========================================================
plt.rcParams.update({
    "font.family": "Garamond",
    "font.size": 19,
    "axes.labelsize": 22,
    "axes.titlesize": 20,
    "xtick.labelsize": 19,
    "ytick.labelsize": 19,
    "legend.fontsize": 17,
    "axes.linewidth": 1.4,
    "lines.linewidth": 2.8,
    "figure.dpi": 300,
    "savefig.dpi": 600
})

from io import StringIO
import pandas as pd

data = """air_temp,wind_speed_10m,ghi,relative_humidity,cloud_opacity
4,1.1,9,93.0,38.1
4,1.1,12,92.9,44.9
4,1.1,12,92.8,58.5
4,1.1,27,92.7,24.7
4,1.0,33,92.6,26.3
4,1.0,36,92.5,32.3
4,1.0,41,92.4,33.8
4,1.0,42,92.3,42.2
4,1.0,45,92.2,45.3
4,0.9,68,92.1,26.3
4,0.9,76,91.9,25.5
4,0.9,74,91.9,34.7
4,0.9,96,92.1,22.6
5,0.9,122,92.2,9.8
5,0.9,135,92.3,7.7
5,0.9,157,92.4,0.0
5,0.9,168,92.5,0.0
5,0.9,179,92.7,0.0
5,0.9,190,92.8,0.0
5,0.9,202,92.9,0.0
6,0.9,213,93.0,0.0
6,0.9,224,93.1,0.0
6,0.9,234,93.2,0.0
6,0.9,245,93.3,0.0
6,0.9,255,93.2,0.0
7,1.0,266,93.2,0.0
7,1.0,276,93.1,0.0
7,1.0,285,93.1,0.0
7,1.0,295,93.1,0.0
7,1.0,305,93.0,0.0
7,1.1,315,93.0,0.0
8,1.1,324,92.9,0.0
8,1.1,334,92.9,0.0
8,1.1,343,92.8,0.0
8,1.1,351,92.8,0.0
8,1.2,360,92.3,0.0
9,1.2,368,91.4,0.0
9,1.2,376,90.5,0.0
9,1.3,383,89.6,0.0
9,1.3,390,88.7,0.0
9,1.3,397,87.8,0.0
10,1.4,402,86.9,0.0
10,1.4,406,86.0,0.0
10,1.4,408,85.2,0.4
10,1.5,411,84.3,0.6
10,1.5,416,83.5,0.0
11,1.6,419,82.7,0.0
11,1.6,417,82.1,1.0
11,1.6,423,81.7,0.0
11,1.6,424,81.3,0.0
11,1.6,426,80.9,0.0
11,1.7,421,80.5,1.2
11,1.7,427,80.1,0.0
11,1.7,415,79.7,2.7
12,1.7,402,79.3,5.6
12,1.7,401,78.9,5.5
12,1.8,400,78.5,5.5
12,1.8,369,78.1,12.6
12,1.8,327,77.8,22.2
12,1.8,330,77.4,20.8
12,1.8,387,77.1,6.6
12,1.8,410,76.8,0.4
12,1.8,394,76.5,3.3
12,1.8,377,76.3,6.5
12,1.9,390,76.0,2.2
13,1.9,394,75.7,0.0
13,1.9,355,75.4,8.6
13,1.9,300,75.1,21.7
13,1.9,300,74.8,20.5
13,1.9,299,74.5,19.4
13,1.9,323,74.3,11.1
13,1.9,332,74.1,6.9
13,1.9,308,73.9,11.7
13,1.9,300,73.8,12.0
13,1.9,241,73.7,27.5
13,1.9,234,73.6,27.8
13,1.9,275,73.5,13.0
13,1.9,275,73.3,10.4
13,1.9,240,73.2,19.3
13,1.9,236,73.1,18.3
13,1.9,243,73.0,13.1
13,1.9,218,72.9,19.1
13,1.9,223,72.8,13.9
13,1.9,213,72.8,14.3
13,1.8,210,72.9,11.9
13,1.8,216,73.0,5.1
13,1.7,205,73.1,5.6
13,1.6,193,73.3,6.2
13,1.6,195,73.4,0.0
13,1.5,183,73.5,0.0
13,1.5,172,73.6,0.0
13,1.4,160,73.7,0.0
13,1.3,149,73.9,0.0
13,1.3,137,74.0,0.0
13,1.2,125,74.1,0.0
13,1.2,113,74.2,0.0
13,1.3,102,74.4,0.0
13,1.4,90,74.5,0.0
13,1.4,79,74.6,0.0
13,1.5,68,74.7,0.0
13,1.6,57,74.8,0.0
13,1.6,46,74.9,0.0
13,1.7,36,75.0,0.0
13,1.8,27,75.2,0.0
13,1.8,18,75.3,0.0
13,1.9,10,75.4,0.0
12,2.0,3,75.5,0.0
"""

df = pd.read_csv(StringIO(data))

df["poa_total"] = df["ghi"]

# ==========================================================
# SAPM Temperature
# ==========================================================
a = -3.47
b = -0.0594

df["temp_module_sapm"] = (
    df["air_temp"]
    + df["poa_total"]
    * np.exp(a + b * df["wind_speed_10m"])
)

# SAPM Cell Temperature
df["temp_cell_sapm"] = (
    df["temp_module_sapm"]
    + 3 * df["poa_total"] / 1000
)

# ==========================================================
# PVLIB Power (Single Panel)
# ==========================================================

df["dc_power_pvlib"] = (
    panel_power_max
    * (df["poa_total"] / stc_irradiance)
    * (1 + temp_coeff * (df["temp_cell_sapm"] - 25))
)

df["ac_power_pvlib"] = (
    df["dc_power_pvlib"]
    * inverter_efficiency
)

# ==========================================================
# OSM-MEPS Temperature
# ==========================================================

df["module_temp"] = (
    45
    + (df["poa_total"] / 800)
    * (28 - df["air_temp"])
)

# ==========================================================
# OSM-MEPS Power (Single Panel)
# ==========================================================

df["dc_power_osm"] = (
    panel_power_max
    * (1 + temp_coeff * (df["module_temp"] - 45))
)

df["dc_power_osm"] *= (
    df["poa_total"] / stc_irradiance
)

df["dc_power_osm"] *= (
    1 - 0.002 * df["relative_humidity"]
)

df["ac_power_osm"] = (
    df["dc_power_osm"]
    * inverter_efficiency
    * 0.9
    * 1
)

# ==========================================================
# Energy (5-minute interval)
# ==========================================================

dt = 5 / 60      # hours

df["pvlib_energy_kWh"] = (
    df["ac_power_pvlib"]
    * dt
    / 1000
)

df["osm_meps_energy_kWh"] = (
    df["ac_power_osm"]
    * dt
    / 1000
)

# ==========================================================
# Cumulative Energy
# ==========================================================

df["PVLIB"] = df["pvlib_energy_kWh"].cumsum()

df["OSM-MEPS"] = df["osm_meps_energy_kWh"].cumsum()

# ==========================================================
# Totals
# ==========================================================

print(f"PVLIB panel energy: {df['pvlib_energy_kWh'].sum():.3f} kWh")
print(f"OSM-MEPS panel energy: {df['osm_meps_energy_kWh'].sum():.3f} kWh")
# ==========================================================
# Cumulative Energy
# ==========================================================

fig, ax = plt.subplots(figsize=(10,6))

time = np.arange(len(df)) * 5 / 60      # hours

ax.plot(
    time,
    df["PVLIB"],
    color="tab:orange",
    linewidth=2.8,
    label="PVLIB (SAPM)"
)

ax.plot(
    time,
    df["OSM-MEPS"],
    color="tab:blue",
    linewidth=2.8,
    label="OSM-MEPS"
)

ax.set_xlabel("Time (hours)")
ax.set_ylabel("Cumulative Energy (kWh)")

ax.grid(True, alpha=0.3)

ax.legend(frameon=False)

plt.tight_layout()

plt.savefig(
    "Energy_Comparison.pdf",
    bbox_inches="tight"
)

plt.show()


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# Garamond IEEE Publication Style
# ==========================================================
plt.rcParams.update({
    "font.family": "Garamond",
    "font.size": 18,
    "axes.labelsize": 19,
    "axes.titlesize": 20,
    "xtick.labelsize": 17,
    "ytick.labelsize": 17,
    "legend.fontsize": 17,
    "axes.linewidth": 1.4,
    "lines.linewidth": 2.8,
    "figure.dpi": 300,
    "savefig.dpi": 600
})

# ==========================================================
# Paste your data below
# ==========================================================
from io import StringIO

data = """air_temp,wind_speed_10m,ghi
4,1.1,9
4,1.1,12
4,1.1,12
4,1.1,27
4,1.0,33
4,1.0,36
4,1.0,41
4,1.0,42
4,1.0,45
4,0.9,68
4,0.9,76
4,0.9,74
4,0.9,96
5,0.9,122
5,0.9,135
5,0.9,157
5,0.9,168
5,0.9,179
5,0.9,190
5,0.9,202
6,0.9,213
6,0.9,224
6,0.9,234
6,0.9,245
6,0.9,255
7,1.0,266
7,1.0,276
7,1.0,285
7,1.0,295
7,1.0,305
7,1.1,315
8,1.1,324
8,1.1,334
8,1.1,343
8,1.1,351
8,1.2,360
9,1.2,368
9,1.2,376
9,1.3,383
9,1.3,390
9,1.3,397
10,1.4,402
10,1.4,406
10,1.4,408
10,1.5,411
10,1.5,416
11,1.6,419
11,1.6,417
11,1.6,423
11,1.6,424
11,1.6,426
11,1.7,421
11,1.7,427
11,1.7,415
12,1.7,402
12,1.7,401
12,1.8,400
12,1.8,369
12,1.8,327
12,1.8,330
12,1.8,387
12,1.8,410
12,1.8,394
12,1.8,377
12,1.9,390
13,1.9,394
13,1.9,355
13,1.9,300
13,1.9,300
13,1.9,299
13,1.9,323
13,1.9,332
13,1.9,308
13,1.9,300
13,1.9,241
13,1.9,234
13,1.9,275
13,1.9,275
13,1.9,240
13,1.9,236
13,1.9,243
13,1.9,218
13,1.9,223
13,1.9,213
13,1.8,210
13,1.8,216
13,1.7,205
13,1.6,193
13,1.6,195
13,1.5,183
13,1.5,172
13,1.4,160
13,1.3,149
13,1.3,137
13,1.2,125
13,1.2,113
13,1.3,102
13,1.4,90
13,1.4,79
13,1.5,68
13,1.6,57
13,1.6,46
13,1.7,36
13,1.8,27
13,1.8,18
13,1.9,10
12,2.0,3
"""

df = pd.read_csv(StringIO(data))

# ==========================================================
# Model parameters
# ==========================================================
POA = 1000.0           # W/m²
NOCT = 45.0            # °C

# SAPM coefficients (Open Rack Glass/Glass)
a = -3.47
b = -0.0594

# ==========================================================
# Temperature Models (Assuming Horizontal PV: POA ≈ GHI)
# ==========================================================

# SAPM
df["SAPM"] = (
    df["air_temp"]
    + df["ghi"] * np.exp(a + b * df["wind_speed_10m"])
)

# Standard NOCT
df["Standard NOCT"] = (
    df["air_temp"]
    + (df["ghi"] / 800.0) * (NOCT - 20.0)
)

# Modified NOCT
df["Modified NOCT"] = (
    45.0
    + (df["ghi"] / 1000.0)
    * (28.0 - df["air_temp"])
)

# ==========================================================
# Plot
# ==========================================================
fig, ax = plt.subplots(figsize=(10,6))

x = np.arange(len(df))

ax.plot(
    x,
    df["SAPM"],
    label="SAPM",
    marker='o',
    markersize=3
)

ax.plot(
    x,
    df["Standard NOCT"],
    label="Standard NOCT",
    marker='s',
    markersize=3
)

ax.plot(
    x,
    df["Modified NOCT"],
    label="Modified NOCT",
    marker='^',
    markersize=3
)

# Ambient temperature
ax.plot(
    x,
    df["air_temp"],
    label="Ambient Temperature",
    linestyle='--',
    linewidth=2.5
)

ax.set_xlabel("Sample")
ax.set_ylabel(r"Temperature ($^\circ$C)")

ax.grid(True, alpha=0.3)
ax.legend(frameon=False)

plt.tight_layout()

plt.savefig(
    "SAPM_vs_NOCT_Comparison.pdf",
    format="pdf",
    bbox_inches="tight"
)

plt.show()


# ==========================================================
# Temperature Coefficient Comparison
# ==========================================================

gamma = -0.005       # 1/°C

# PVLIB (SAPM)
df["PVLIB Factor"] = (
    1 + gamma * (df["SAPM"] + 3*df["ghi"]/1000 - 25)
)

# OSM-MEPS
df["OSM-MEPS Factor"] = (
    1 + gamma * (df["Modified NOCT"] - 45)
)

fig, ax = plt.subplots(figsize=(10,6))

x = np.arange(len(df))

ax.plot(
    x,
    df["PVLIB Factor"],
    color="tab:orange",
    label=r"PVLIB ($T_{cell}-25^\circ$C)"
)

ax.plot(
    x,
    df["OSM-MEPS Factor"],
    color="tab:blue",
    label=r"OSM-MEPS ($T_{mod}-45^\circ$C)"
)

ax.axhline(
    1.0,
    color="black",
    linestyle="--",
    linewidth=1.5
)

ax.set_xlabel("Sample")
ax.set_ylabel("Temperature Correction Factor")

ax.grid(True, alpha=0.3)
ax.legend(frameon=False)

plt.tight_layout()

plt.savefig(
    "Gamma_Temperature_Correction.pdf",
    bbox_inches="tight"
)

plt.show()
