import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Load your three datasets (replace with actual loading if not already loaded)
# daily_energy_pvlib = pd.read_csv("pvlib_output.csv", index_col=0, parse_dates=True)
# daily_energy_epsm = pd.read_csv("epsm_output.csv", index_col=0, parse_dates=True)
# pvoutput_actual = pd.read_csv("pvoutput_actual.csv", index_col=0, parse_dates=True)

# 1. Ensure datetime indices and remove timezone
daily_energy_pvlib.index = pd.to_datetime(daily_energy_pvlib.index).tz_localize(None).date
daily_energy_epsm.index = pd.to_datetime(daily_energy_epsm.index).tz_localize(None).date
pvoutput_actual.index = pd.to_datetime(pvoutput_actual.index).date

# 2. Ensure Series (optional, if your data is DataFrame with single column)
daily_energy_pvlib = pd.Series(daily_energy_pvlib.values.flatten(), index=daily_energy_pvlib.index)
daily_energy_epsm = pd.Series(daily_energy_epsm.values.flatten(), index=daily_energy_epsm.index)
pvoutput_actual = pd.Series(pvoutput_actual.values.flatten(), index=pvoutput_actual.index)

# 3. Find common dates
common_dates = daily_energy_pvlib.index.intersection(pvoutput_actual.index)

# 4. Extract aligned values
y_true = pvoutput_actual.loc[common_dates]
y_pred_pvlib = daily_energy_pvlib.loc[common_dates]
y_pred_epsm = daily_energy_epsm.loc[common_dates]

# 5. Define error metric printer
def print_metrics(name, y_pred):
    print(f"\n{name} Model:")
    print("MAE :", mean_absolute_error(y_true, y_pred))
    print("RMSE:", np.sqrt(mean_squared_error(y_true, y_pred)))
    print("R²  :", r2_score(y_true, y_pred))

# 6. Show metrics
print_metrics("PVLIB", y_pred_pvlib)
print_metrics("OSM-MEPS", y_pred_epsm)
