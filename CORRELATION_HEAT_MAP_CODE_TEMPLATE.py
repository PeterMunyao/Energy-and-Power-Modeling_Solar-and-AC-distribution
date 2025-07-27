
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np  # ← Add this line


# 1. Load data (parse 'period_end' as datetime)
df = pd.read_csv(
    'csv_-0.085477_34.718851_fixed_23_0_PT5M.csv', #replace with your file
    parse_dates=['period_end']
)
# === Parse time column ===
df['period_end'] = pd.to_datetime(df['period_end'])
df.set_index('period_end', inplace=True)

# Extract numeric columns (exclude datetime)
numeric_df = df.select_dtypes(include=['float64', 'int64'])

# Compute correlations
corr_matrix = numeric_df.corr()

# Plot heatmap with Garamond and glossy style
fig, ax = plt.subplots(figsize=(12, 8), facecolor='#f9f9f9')  # figure background
ax.set_facecolor('#f9f9f9')  # axes background
sns.set(font='Garamond', font_scale=1.2, style='white')

# Mask strictly upper triangle, keep diagonal visible
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)

sns.heatmap(
    corr_matrix,
    annot=True,
    cmap='coolwarm',
    vmin=-1,
    vmax=1,
    linewidths=0.5,
    fmt=".2f",
    ax=ax,
    mask=mask,
    annot_kws={"size": 13.5, "weight": "bold", "ha": "center", "va": "center", "color": "black"}
)

plt.xticks(fontsize=13.5, rotation=45, ha='right')
plt.yticks(fontsize=13.5, rotation=0)
plt.tight_layout()
# Save with high quality
plt.savefig("Correlation_Heatmap_VictoriaViews_Kisumu_Kenya.pdf", format="pdf", dpi=900, bbox_inches='tight')
plt.show()
