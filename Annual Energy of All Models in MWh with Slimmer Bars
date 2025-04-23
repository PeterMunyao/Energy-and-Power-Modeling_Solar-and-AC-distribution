# === Plot Total Annual Energy of All Models in MWh  Bars ===
total_pvlib = daily_energy_pvlib.sum() / 1000
total_epsm = daily_energy_epsm.sum() / 1000
total_pvoutput = pvoutput_actual['Generated_kWh'].sum() / 1000
total_gsa = gsa_df['Total_Monthly_kWh'].sum() / 1000

models = ['PVLIB Model', 'OSM-MEPS Model', 'Serres-C PV \n Power Plant \n Measured Output', 'GSA Energy Estimate']
totals = [total_pvlib, total_epsm, total_pvoutput, total_gsa]
colors = ['orange', 'green', 'blue', 'maroon']

plt.figure(figsize=(12, 6))
bars = plt.bar(models, totals, width=0.5, color=colors)  # Slimmer bars

# Annotate bar values in MWh
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 10, f'{yval:,.0f} MWh', ha='center', va='bottom', fontsize=17, fontweight='bold')

plt.title("Annual Solar Energy (MWh) for Serres-C PV Power Plant", fontsize=16, fontweight='bold')
plt.ylabel("Total Energy (MWh)", fontsize=18, fontweight='bold')
plt.xticks(fontsize=18, fontweight='bold')
plt.yticks(fontsize=18, fontweight='bold')
plt.grid(axis='y', linestyle='--', alpha=0.94)
plt.tight_layout()
plt.savefig("Total_Final_Annual_Energy_Comparison_Barplot_MWh.pdf", format='pdf')
plt.show()
