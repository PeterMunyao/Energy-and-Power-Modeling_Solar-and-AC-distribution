import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# === STYLE CONFIG ===
plt.rcParams['font.family'] = 'Garamond'
plt.rcParams.update({'font.size': 14})

# === FUNCTION TO LOAD AND PREPARE DATA ===
def load_and_process_data(filepath):
    df = pd.read_csv(filepath)
    df['period_end'] = pd.to_datetime(df['period_end'], utc=True).dt.tz_convert(None)
    df.set_index('period_end', inplace=True)

    required_cols = ['dni', 'ghi', 'dhi', 'air_temp', 'albedo', 'zenith', 'azimuth',
                     'cloud_opacity', 'relative_humidity']
    for col in required_cols:
        df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0)

    return df

# === FUNCTION TO CALCULATE ENERGY AND CONDITIONS ===
def compute_solar_output(df):
    panel_power_max = 390
    panel_area = 1.6
    total_area = 40
    num_panels = int(total_area / panel_area)

    tilt_rad = np.radians(22.5)
    azimuth_rad = np.radians(184)
    df['zenith_rad'] = np.radians(df['zenith'])
    df['azimuth_rad'] = np.radians(df['azimuth'])

    df['aoi'] = np.degrees(np.arccos(
        np.cos(df['zenith_rad']) * np.cos(tilt_rad) +
        np.sin(df['zenith_rad']) * np.sin(tilt_rad) *
        np.cos(df['azimuth_rad'] - azimuth_rad)
    )).clip(0, 90)

    df['poa_direct'] = (df['dni'] * np.cos(np.radians(df['aoi']))).clip(lower=0)
    df['poa_diffuse'] = df['dhi'] * (1 + np.cos(tilt_rad)) / 2
    df['poa_sky_diffuse'] = df['ghi'] * df['albedo'] * (1 - np.cos(tilt_rad)) / 2
    df['poa_total'] = df['poa_direct'] + df['poa_diffuse'] + df['poa_sky_diffuse']

    noct = 45
    temp_coeff = -0.0045
    df['module_temp'] = noct + df['poa_total'] / 800 * (28 - df['air_temp'])
    df['panel_power'] = panel_power_max * (1 + temp_coeff * (df['module_temp'] - noct))
    df['dc_power'] = df['panel_power'] * df['poa_total'] / 1000
    df['ac_power'] = df['dc_power'] * 0.88
    df['scaled_power'] = df['ac_power'] * num_panels

    df.dropna(subset=['scaled_power'], inplace=True)
    return df

# === FUNCTION TO RESAMPLE IN 12-HOUR INTERVALS ===
def resample_12hr(df):
    resampled = pd.DataFrame()
    resampled['energy_kWh'] = df['scaled_power'].resample('12H').sum() / 1000
    resampled['cloud_opacity'] = df['cloud_opacity'].resample('12H').mean()
    resampled['relative_humidity'] = df['relative_humidity'].resample('12H').mean()

    # Normalize
    resampled['cloud_opacity_norm'] = resampled['cloud_opacity'] / resampled['cloud_opacity'].max()
    resampled['humidity_norm'] = resampled['relative_humidity'] / 100
    return resampled

# === FUNCTION TO PLOT A GIVEN PERIOD ===
def plot_period(ax, resampled_df, title, start_date, end_date):
    data = resampled_df.loc[start_date:end_date]

    ax.plot(data.index, data['energy_kWh'], color='darkorange', linewidth=1.6, label='Energy Output (kWh)')
    ax2 = ax.twinx()
    ax2.plot(data.index, data['cloud_opacity_norm'], color='gray', linestyle='--', label='Cloud Opacity (normalized)')
    ax2.plot(data.index, data['humidity_norm'], color='royalblue', linestyle='--', label='Humidity (normalized)')

    # Style with black y-labels
    ax.set_ylabel('Energy (kWh) - 12 hour resolution', fontsize=18, fontweight='bold', color='black')
    ax2.set_ylabel('Normalized Opacity / Humidity', fontsize=18, fontweight='bold', color='black')
    ax.set_title(title, fontsize=18, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.6)

    # ... inside your plotting function or loop where ax and ax2 are defined

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.tick_params(axis='x', labelrotation=0)
    ax.tick_params(axis='y', labelcolor='black')
    ax2.tick_params(axis='y', labelcolor='black')

# Adjust font size and weight for x-axis tick labels
    for label in ax.get_xticklabels():
     label.set_fontsize(16)
     label.set_fontweight('bold')

# Adjust font size and weight for y-axis tick labels (left y-axis)
    for label in ax.get_yticklabels():
     label.set_fontsize(16)
     label.set_fontweight('bold')
     label.set_color('black')  # just in case

# Adjust font size and weight for y-axis tick labels (right y-axis)
    for label in ax2.get_yticklabels():
     label.set_fontsize(16)
     label.set_fontweight('bold')
     label.set_color('black')
    # Return lines and labels for combined legend
     lines1, labels1 = ax.get_legend_handles_labels()
     lines2, labels2 = ax2.get_legend_handles_labels()
     return lines1 + lines2, labels1 + labels2

# === MAIN SCRIPT ===
csv_file = 'csv_-1.11665_36.92927_fixed_23_0_PT5M_2024.csv'
df = load_and_process_data(csv_file)
df = compute_solar_output(df)
resampled = resample_12hr(df)

fig, axes = plt.subplots(3, 1, figsize=(15, 20), sharex=False, facecolor='#f9f9f9')

# Plot each period and collect legend handles and labels
all_lines = []
all_labels = []

lines, labels = plot_period(axes[0], resampled, "January – April 2024", '2024-01-01', '2024-04-30')
all_lines.extend(lines)
all_labels.extend(labels)

lines, labels = plot_period(axes[1], resampled, "May – August 2024", '2024-05-01', '2024-08-31')
all_lines.extend(lines)
all_labels.extend(labels)

lines, labels = plot_period(axes[2], resampled, "September – December 2024", '2024-09-01', '2024-12-31')
all_lines.extend(lines)
all_labels.extend(labels)

#axes[2].set_xlabel(" Month ", fontsize=16, fontweight='bold')

plt.tight_layout(rect=[0, 0.05, 1, 0.95])


# Use only legend handles from the first subplot
# Add combined legend below all plots, centered
fig.legend(lines, labels, loc='lower center', ncol=1, fontsize=17, frameon=False, bbox_to_anchor=(0.5, -0.02))

# Save and show
pdf_path = "POWER_solar_energy_opacity_humidity_2024_3part_with_legend.pdf"
plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
plt.show()

print(f"✅ PDF saved at: {pdf_path}")
