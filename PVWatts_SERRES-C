import requests
import pandas as pd
import matplotlib.pyplot as plt

# Your API key
API_KEY = "ywiB7gx2tpgb6aVZVDxId6YGwwdhpQThFbW3s53Q"

# PVWatts API endpoint
url = "https://developer.nrel.gov/api/pvwatts/v6.json"

# Parameters for Serres-C
params = {
    "api_key": API_KEY,
    "lat": 40.886273,
    "lon": 23.912687,
    "system_capacity": 1010.880,         # kW
    "azimuth": 0,                # Facing south
    "tilt": 25,                    # Optimal tilt angle
    "array_type": 1,               # Fixed open rack
    "module_type": 0,              # Standard
    "losses": 1,                  # Default total system losses (%)
    "dataset": "intl",             # International TMY dataset
    "timeframe": "monthly"         # Monthly output
}

# Make the API request
response = requests.get(url, params=params)

# Check for successful response
if response.status_code == 200:
    data = response.json()
    ac_monthly = data["outputs"]["ac_monthly"]
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    df = pd.DataFrame({
        'Month': months,
        'AC Output (kWh)': ac_monthly
    })

    print(df)

    # Plotting
    plt.figure(figsize=(10,6))
    plt.bar(df['Month'], df['AC Output (kWh)'], color='orange')
    plt.title('Monthly AC Energy Output for Serres-C (1010.880kW System)')
    plt.ylabel('Energy (kWh)')
    plt.xlabel('Month')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
else:
    print("API Request failed. Status Code:", response.status_code)
    print(response.text)
