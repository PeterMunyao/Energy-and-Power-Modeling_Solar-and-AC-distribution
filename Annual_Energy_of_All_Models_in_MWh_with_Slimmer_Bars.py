import matplotlib.pyplot as plt
import matplotlib as mpl

# === Global Styling ===
mpl.rcParams['font.family'] = 'Garamond'

# === Example Data: Replace these with your actual data sources ===
# These lines assume you already have the following data loaded:
# - daily_energy_pvlib
# - daily_energy_epsm
# - pvoutput_actual
# - gsa_df

total_pvlib = daily_energy_pvlib.sum() / 1000  # convert kWh to MWh
total_epsm = daily_energy_epsm.sum() / 1000
total_pvoutput = pvoutput_actual['Generated_kWh'].sum() / 1000
total_gsa = gsa_df['Total_Monthly_MWh'].sum()
total_sam = 1064.008  # SAM estimate (MWh)

# === Data for Plot ===
models = [
    'PVLIB Model',
    'OSM-MEPS Model',
    'Serres-C Solar \n PV Energy',
    'GSA Model \n Energy Estimate',
    'SAM Model'
]
totals = [total_pvlib, total_epsm, total_pvoutput, total_gsa, total_sam]
colors = ['orange', 'green', 'blue', 'gold', 'darkcyan']

# === Create Plot ===
fig, ax = plt.subplots(figsize=(11, 7), facecolor='#f0f0f0')
ax.set_facecolor('#f0f0f0')

# Draw grid lines first
ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)

# Draw bars *above* the grid
bars = ax.bar(models, totals, width=0.250, color=colors, zorder=3)

# Annotate each bar
for bar in bars:
    yval = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        yval + 10,
        f'{yval:,.3f} MWh',
        ha='center',
        va='bottom',
        fontsize=14.5,
        fontweight='bold'
    )

# Axis labels and ticks
ax.set_ylabel("Total Energy (MWh)", fontsize=18, fontweight='bold')
ax.tick_params(axis='x', labelsize=17)
ax.tick_params(axis='y', labelsize=17)

# === Save as PDF ===
plt.tight_layout()
plt.savefig("SAM_Garamond_Annual_Energy_Comparison_Barplot_MWh.pdf", format='pdf', bbox_inches='tight', facecolor=fig.get_facecolor())
plt.show()
