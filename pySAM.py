import PySAM.Pvwattsv8 as pv
import matplotlib.pyplot as plt
import numpy as np

# Set global plotting style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Garamond']
plt.rcParams['font.size'] = 18
plt.rcParams['axes.facecolor'] = 'lightgrey'
plt.rcParams['figure.facecolor'] = 'lightgrey'

# === Path to SAM-compatible CSV ===
sam_file = r"imperial_ca_32.835205_-115.572398_psmv3_60_tmy.csv"

# === Load PVWatts model ===
system = pv.default("PVWattsCommercial")

# === Assign the weather CSV ===
system.SolarResource.solar_resource_file = sam_file

print("=" * 60)
print("PV SYSTEM DESIGN CONFIGURATION")
print("=" * 60)

# === SYSTEM DESIGN PARAMETERS ===
print("\nSYSTEM DESIGN PARAMETERS:")
print("-" * 30)

# System capacity
while True:
    try:
        system_capacity = input(f"System Capacity (kW) [115]: ").strip()
        if system_capacity == '':
            system_capacity = 115
        else:
            system_capacity = float(system_capacity)
        if system_capacity > 0:
            break
        else:
            print("   Please enter a positive number")
    except ValueError:
        print("   Please enter a valid number")

system.SystemDesign.system_capacity = system_capacity

# DC-AC Ratio
while True:
    try:
        dc_ac_ratio = input(f"DC-AC Ratio [1.1]: ").strip()
        if dc_ac_ratio == '':
            dc_ac_ratio = 1.1
        else:
            dc_ac_ratio = float(dc_ac_ratio)
        if dc_ac_ratio > 0:
            break
        else:
            print("   Please enter a positive number")
    except ValueError:
        print("   Please enter a valid number")

system.SystemDesign.dc_ac_ratio = dc_ac_ratio

# Array Type
print("\nArray Type Options:")
print("  0 - Fixed Open Rack")
print("  1 - Fixed Roof Mount")
print("  2 - 1-Axis Tracking")
print("  3 - Backtracking")
print("  4 - 2-Axis Tracking")

while True:
    try:
        array_type = input(f"Array Type [1]: ").strip()
        if array_type == '':
            array_type = 1
        else:
            array_type = int(array_type)
        if 0 <= array_type <= 4:
            break
        else:
            print("   Please enter 0-4")
    except ValueError:
        print("   Please enter a valid number (0-4)")

system.SystemDesign.array_type = array_type

# Module type
print("\nModule Type Options:")
print("  0 - Standard")
print("  1 - Premium")
print("  2 - Thin Film")

while True:
    try:
        module_type = input(f"Module Type [0]: ").strip()
        if module_type == '':
            module_type = 0
        else:
            module_type = int(module_type)
        if 0 <= module_type <= 2:
            break
        else:
            print("   Please enter 0-2")
    except ValueError:
        print("   Please enter a valid number (0-2)")

system.SystemDesign.module_type = module_type

# Inverter efficiency
while True:
    try:
        inv_eff = input(f"Inverter Efficiency (%) [96.0]: ").strip()
        if inv_eff == '':
            inv_eff = 96.0
        else:
            inv_eff = float(inv_eff)
        if 80 <= inv_eff <= 99:
            break
        else:
            print("   Please enter 80-99%")
    except ValueError:
        print("   Please enter a valid number")

system.SystemDesign.inv_eff = inv_eff

# === SUBARRAY CONFIGURATION ===
print("\n" + "=" * 50)
print("SUBARRAY CONFIGURATION")
print("=" * 50)

while True:
    try:
        num_subarrays = input(f"Number of Subarrays [1]: ").strip()
        if num_subarrays == '':
            num_subarrays = 1
        else:
            num_subarrays = int(num_subarrays)
        if 1 <= num_subarrays <= 10:
            break
        else:
            print("   Please enter 1-10 subarrays")
    except ValueError:
        print("   Please enter a valid number")

# Store subarray configurations for reporting
subarray_configs = []

# For PVWatts, we'll use average parameters since it doesn't support multiple subarrays directly
if num_subarrays > 1:
    print(f"\nConfiguring {num_subarrays} subarrays (using average parameters for PVWatts):")
    
    total_capacity = system_capacity
    remaining_capacity = total_capacity
    tilt_sum = 0
    azimuth_sum = 0
    gcr_sum = 0
    
    for i in range(num_subarrays):
        print(f"\n--- Subarray {i+1} ---")
        
        # Subarray capacity
        while True:
            try:
                if i == num_subarrays - 1:
                    # Last subarray gets remaining capacity
                    sub_capacity = remaining_capacity
                    print(f"  Capacity (kW): {sub_capacity:.1f} (remaining)")
                else:
                    sub_capacity_input = input(f"  Capacity (kW) [{remaining_capacity/(num_subarrays-i):.1f}]: ").strip()
                    if sub_capacity_input == '':
                        sub_capacity = remaining_capacity / (num_subarrays - i)
                    else:
                        sub_capacity = float(sub_capacity_input)
                
                if 0 < sub_capacity <= remaining_capacity:
                    remaining_capacity -= sub_capacity
                    break
                else:
                    print(f"     Please enter between 0 and {remaining_capacity:.1f} kW")
            except ValueError:
                print("     Please enter a valid number")
        
        # Subarray tilt
        while True:
            try:
                sub_tilt = input(f"  Tilt (degrees) [25]: ").strip()
                if sub_tilt == '':
                    sub_tilt = 25
                else:
                    sub_tilt = float(sub_tilt)
                if 0 <= sub_tilt <= 90:
                    tilt_sum += sub_tilt * sub_capacity  # Weight by capacity
                    break
                else:
                    print("     Please enter 0-90 degrees")
            except ValueError:
                print("     Please enter a valid number")
        
        # Subarray azimuth
        while True:
            try:
                sub_azimuth = input(f"  Azimuth (degrees, 180=S) [180]: ").strip()
                if sub_azimuth == '':
                    sub_azimuth = 180
                else:
                    sub_azimuth = float(sub_azimuth)
                if 0 <= sub_azimuth <= 360:
                    azimuth_sum += sub_azimuth * sub_capacity  # Weight by capacity
                    break
                else:
                    print("     Please enter 0-360 degrees")
            except ValueError:
                print("     Please enter a valid number")
        
        # Subarray GCR (only for tracking systems)
        sub_gcr = 0.4  # default
        if array_type in [2, 3, 4]:  # Tracking systems
            while True:
                try:
                    gcr_input = input(f"  Ground Coverage Ratio [0.4]: ").strip()
                    if gcr_input == '':
                        sub_gcr = 0.4
                    else:
                        sub_gcr = float(gcr_input)
                    if 0.1 <= sub_gcr <= 0.9:
                        gcr_sum += sub_gcr * sub_capacity  # Weight by capacity
                        break
                    else:
                        print("     Please enter 0.1-0.9")
                except ValueError:
                    print("     Please enter a valid number")
        
        # Store subarray configuration
        subarray_configs.append({
            'capacity': sub_capacity,
            'tilt': sub_tilt,
            'azimuth': sub_azimuth,
            'gcr': sub_gcr
        })
        
        print(f"  → Configured: {sub_capacity:.1f} kW, {sub_tilt}° tilt, {sub_azimuth}° azimuth" + 
              (f", GCR: {sub_gcr}" if array_type in [2, 3, 4] else ""))
    
    # Calculate weighted averages for PVWatts (since it doesn't support multiple subarrays)
    avg_tilt = tilt_sum / total_capacity
    avg_azimuth = azimuth_sum / total_capacity
    if array_type in [2, 3, 4]:
        avg_gcr = gcr_sum / total_capacity
    
    print(f"\nUsing weighted averages for PVWatts simulation:")
    print(f"  Average Tilt: {avg_tilt:.1f}°")
    print(f"  Average Azimuth: {avg_azimuth:.1f}°")
    if array_type in [2, 3, 4]:
        print(f"  Average GCR: {avg_gcr:.3f}")
    
    system.SystemDesign.tilt = avg_tilt
    system.SystemDesign.azimuth = avg_azimuth
    if array_type in [2, 3, 4]:
        system.SystemDesign.gcr = avg_gcr
    
else:
    # Single subarray - get parameters
    print("\nConfiguring single subarray:")
    
    # Tilt
    while True:
        try:
            tilt = input(f"Tilt Angle (degrees) [30]: ").strip()
            if tilt == '':
                tilt = 30
            else:
                tilt = float(tilt)
            if 0 <= tilt <= 90:
                break
            else:
                print("   Please enter 0-90 degrees")
        except ValueError:
            print("   Please enter a valid number")
    
    # Azimuth
    while True:
        try:
            azimuth = input(f"Azimuth Angle (degrees, 180=S) [180]: ").strip()
            if azimuth == '':
                azimuth = 180
            else:
                azimuth = float(azimuth)
            if 0 <= azimuth <= 360:
                break
            else:
                print("   Please enter 0-360 degrees")
        except ValueError:
            print("   Please enter a valid number")
    
    # GCR for tracking systems
    gcr = 0.4
    if array_type in [2, 3, 4]:
        while True:
            try:
                gcr_input = input(f"Ground Coverage Ratio [0.4]: ").strip()
                if gcr_input == '':
                    gcr = 0.4
                else:
                    gcr = float(gcr_input)
                if 0.1 <= gcr <= 0.9:
                    break
                else:
                    print("   Please enter 0.1-0.9")
            except ValueError:
                print("   Please enter a valid number")
    
    system.SystemDesign.tilt = tilt
    system.SystemDesign.azimuth = azimuth
    if array_type in [2, 3, 4]:
        system.SystemDesign.gcr = gcr
    
    subarray_configs.append({
        'capacity': system_capacity,
        'tilt': tilt,
        'azimuth': azimuth,
        'gcr': gcr
    })

# === LOSS FACTORS ===
print("\n" + "=" * 50)
print("SYSTEM LOSS FACTORS (as percentages)")
print("Press Enter to use default values")
print("=" * 50)

# PVWatts uses a single loss percentage that combines all losses
print("Note: PVWatts uses a single combined loss percentage")
print("We'll calculate this from individual loss factors")

loss_factors = {
    'soiling': {'default': 2.0, 'desc': 'Soiling Loss (dirt/dust on panels)'},
    'shading': {'default': 3.0, 'desc': 'Shading Loss (from obstructions)'},
    'snow': {'default': 0.0, 'desc': 'Snow Loss (snow coverage)'},
    'mismatch': {'default': 2.0, 'desc': 'Mismatch Loss (panel variations)'},
    'wiring': {'default': 2.0, 'desc': 'Wiring Loss (DC losses)'},
    'connections': {'default': 0.5, 'desc': 'Connections Loss'},
    'lid': {'default': 1.5, 'desc': 'Light-induced Degradation'},
    'nameplate': {'default': 1.0, 'desc': 'Nameplate Rating Tolerance'},
    'availability': {'default': 3.0, 'desc': 'System Availability'}
}

user_losses = {}
for loss_name, loss_info in loss_factors.items():
    while True:
        try:
            user_input = input(f"{loss_info['desc']} [{loss_info['default']}%]: ")
            if user_input.strip() == '':
                user_losses[loss_name] = loss_info['default']
                break
            else:
                value = float(user_input)
                if 0 <= value <= 100:
                    user_losses[loss_name] = value
                    break
                else:
                    print("   Please enter 0-100")
        except ValueError:
            print("   Please enter a valid number")

# Calculate total losses for PVWatts (it uses a single loss percentage)
total_loss_percentage = sum(user_losses.values())
print(f"\nTotal system losses: {total_loss_percentage:.1f}%")

# Apply the combined loss percentage to PVWatts
system.SystemDesign.losses = total_loss_percentage

print("\n" + "=" * 60)

# === Run the simulation ===
print("Running simulation...")
system.execute()

# === FIXED CAPACITY FACTOR HANDLING ===
def get_correct_capacity_factor(system):
    """
    Handle PySAM capacity factor compatibility across versions
    Some versions return decimal (0.20), others return percentage (20.0)
    """
    raw_cf = system.Outputs.capacity_factor
    
    # Manual verification
    annual_energy = system.Outputs.annual_energy
    system_capacity = system.SystemDesign.system_capacity
    hours_per_year = 8760
    manual_cf = (annual_energy / (system_capacity * hours_per_year)) * 100
    
    print(f"🔍 CAPACITY FACTOR DEBUG:")
    print(f"   Raw PySAM CF: {raw_cf}")
    print(f"   Manual Calc CF: {manual_cf:.2f}%")
    
    # Determine which one is correct
    if abs(raw_cf - manual_cf) < 1:  # They match closely
        return raw_cf
    elif abs(raw_cf/100 - manual_cf) < 1:  # Raw needs division by 100
        return raw_cf / 100
    else:  # Use manual calculation as fallback
        print(f"   ⚠️  Using manual calculation: {manual_cf:.2f}%")
        return manual_cf

# Get corrected capacity factor
corrected_cf = get_correct_capacity_factor(system)

# === PRINT RESULTS WITH FIXED CAPACITY FACTOR ===
print("\n" + "=" * 60)
print("PV SYSTEM PERFORMANCE RESULTS")
print("=" * 60)

# System configuration summary
print(f"\nSYSTEM CONFIGURATION:")
print(f"  System Capacity: {system.SystemDesign.system_capacity} kW")
print(f"  DC-AC Ratio: {system.SystemDesign.dc_ac_ratio}")

# FIX: Convert float values to integers for array indexing
array_type_names = ['Fixed Open Rack', 'Fixed Roof Mount', '1-Axis', 'Backtracking', '2-Axis']
module_type_names = ['Standard', 'Premium', 'Thin Film']

try:
    array_type_int = int(system.SystemDesign.array_type)
    module_type_int = int(system.SystemDesign.module_type)
    
    print(f"  Array Type: {array_type_names[array_type_int]}")
    print(f"  Module Type: {module_type_names[module_type_int]}")
except (ValueError, IndexError) as e:
    print(f"  Array Type: {system.SystemDesign.array_type} (raw value)")
    print(f"  Module Type: {system.SystemDesign.module_type} (raw value)")

print(f"  Inverter Efficiency: {system.SystemDesign.inv_eff}%")
print(f"  System Losses: {system.SystemDesign.losses}%")
print(f"  Number of Subarrays: {num_subarrays}")

# Subarray details
print(f"\nSUBARRAY CONFIGURATIONS:")
for i, config in enumerate(subarray_configs, 1):
    print(f"  Subarray {i}: {config['capacity']:.1f} kW, {config['tilt']}° tilt, {config['azimuth']}° azimuth" + 
          (f", GCR: {config['gcr']}" if array_type in [2, 3, 4] else ""))

# Individual loss factors (for reporting)
print(f"\nDETAILED LOSS FACTORS:")
for loss_name, value in user_losses.items():
    desc = loss_factors[loss_name]['desc']
    print(f"  {desc}: {value}%")

# Energy production with FIXED capacity factor
print(f"\nANNUAL ENERGY PRODUCTION:")
print(f"  Annual Energy: {system.Outputs.annual_energy:,.0f} kWh")
print(f"  Capacity Factor: {corrected_cf:.1f}%")  # FIXED

# Monthly breakdown
print(f"\nMONTHLY ENERGY (kWh):")
monthly_energy = system.Outputs.monthly_energy
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

for i, (month, energy) in enumerate(zip(months, monthly_energy)):
    print(f"  {month}: {energy:,.0f} kWh")

# Performance metrics with FIXED capacity factor
print(f"\nSYSTEM PERFORMANCE SUMMARY:")
print(f"  Total Applied Losses: {total_loss_percentage:.1f}%")
print(f"  System Efficiency: {100 - total_loss_percentage:.1f}%")
print(f"  Capacity Factor: {corrected_cf:.1f}%")  # FIXED

# === PLOT ENERGY OUTPUT WITH FIXED CAPACITY FACTOR ===
print("\nGenerating plots...")

# Create figure with light grey background
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
fig.patch.set_facecolor('lightgrey')

# Monthly energy bar plot
try:
    bars = ax1.bar(months, monthly_energy, color='steelblue', alpha=0.8, edgecolor='navy', linewidth=1.2)
    ax1.set_ylabel('Energy Production (kWh)', fontweight='bold', fontsize=18)
    ax1.set_title('Monthly Energy Production', fontweight='bold', fontsize=20, pad=20)
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(monthly_energy)*0.01,
                 f'{height:,.0f}', ha='center', va='bottom', fontsize=14, fontweight='bold')

    # Cumulative energy line plot
    cumulative_energy = np.cumsum(monthly_energy)
    ax2.plot(months, cumulative_energy, color='darkred', linewidth=3, marker='o', markersize=8, markerfacecolor='gold', markeredgecolor='darkred', markeredgewidth=2)
    ax2.fill_between(months, cumulative_energy, alpha=0.3, color='salmon')
    ax2.set_ylabel('Cumulative Energy (kWh)', fontweight='bold', fontsize=18)
    ax2.set_xlabel('Month', fontweight='bold', fontsize=18)
    ax2.set_title('Cumulative Annual Energy Production', fontweight='bold', fontsize=20, pad=20)
    ax2.grid(True, alpha=0.3, linestyle='--')

    # Add value labels for cumulative
    for i, (month, value) in enumerate(zip(months, cumulative_energy)):
        ax2.text(i, value + max(cumulative_energy)*0.02, f'{value:,.0f}', 
                 ha='center', va='bottom', fontsize=12, fontweight='bold', 
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

    plt.tight_layout(pad=3.0)

    # Add overall title with FIXED capacity factor
    fig.suptitle(f'PV System Performance: {system.Outputs.annual_energy:,.0f} kWh Annual Production\n'
                 f'Capacity Factor: {corrected_cf:.1f}% | System: {system_capacity} kW | {num_subarrays} Subarray(s)',  # FIXED
                 fontsize=16, fontweight='bold', y=0.98)

    plt.show()
    
except Exception as e:
    print(f"  ERROR generating plots: {e}")

print("\n" + "=" * 60)
print("SIMULATION COMPLETE")
print("=" * 60)
