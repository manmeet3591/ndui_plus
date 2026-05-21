import ee
import wxee
import xarray as xr
import numpy as np
import json
from sklearn.metrics import f1_score, accuracy_score, cohen_kappa_score

# 1. Initialize GEE
key_path = '/media/airlab/ROCSTOR/ndui_plus/NDUI+/ndui/ee-manmeet20singh15-wbis-fab7f1ca35e0.json'
with open(key_path) as f:
    key = json.load(f)
credentials = ee.ServiceAccountCredentials(key['client_email'], key_path)
ee.Initialize(credentials)
wxee.Initialize()

# 2. Load Local NDUI+ Data (Chicago 2020)
ndui_path = '/media/airlab/ROCSTOR/ndui_plus/NDUI+/ndui/ndui_2020_chicago.nc'
ds_ndui = xr.open_dataset(ndui_path)

# 3. Load GHSL Built-up Surface (GHS_BUILT_S) for 2020 from GEE
ghsl = ee.Image("JRC/GHSL/P2023A/GHS_BUILT_S/2020")

# Define a larger AOI that covers both urban and non-urban areas
# Chicago Lat: 41.3 to 42.3, Lon: -88.5 to -87.5
# We'll take a 20km x 20km box at the western fringe to get a good mix
lat_test = 41.8
lon_test = -88.2
aoi_small = ee.Geometry.Rectangle([lon_test - 0.1, lat_test - 0.1, lon_test + 0.1, lat_test + 0.1])

# 4. Fetch GHSL and Align
print(f"Fetching mixed sample from GEE at {lat_test}, {lon_test}...")
ds_ghsl = ghsl.wx.to_xarray(region=aoi_small, scale=30)
ghsl_var = list(ds_ghsl.data_vars)[0]
ds_ghsl = ds_ghsl.rename({'x': 'lon', 'y': 'lat'})

# Slice NDUI
ds_ndui_small = ds_ndui.sel(lat=slice(lat_test - 0.1, lat_test + 0.1), lon=slice(lon_test - 0.1, lon_test + 0.1))

# Align grids
ds_ghsl_aligned = ds_ghsl.interp(lat=ds_ndui_small.lat, lon=ds_ndui_small.lon, method='nearest')

# 5. Optimize Threshold and Calculate Metrics
ndui_flat = ds_ndui_small.ndui.values.flatten()
ghsl_flat = ds_ghsl_aligned[ghsl_var].values.flatten()
mask = ~np.isnan(ndui_flat) & ~np.isnan(ghsl_flat)
ndui_clean = ndui_flat[mask]
ghsl_raw = ghsl_flat[mask]

print(f"\n--- Validation at Mixed Urban/Rural Fringe (Chicago 2020) ---")
print(f"Urban pixels (GHSL>50%): {np.sum(ghsl_raw > 50)}")
print(f"Non-urban pixels (GHSL<=50%): {np.sum(ghsl_raw <= 50)}")

# Find best threshold across a range of ground truth definitions
for gt_thresh in [10, 20, 50]:
    ghsl_bin = (ghsl_raw > gt_thresh).astype(int)
    thresholds = np.linspace(0.0, 0.5, 51)
    f1_scores = [f1_score(ghsl_bin, ndui_clean > t) for t in thresholds]
    best_t = thresholds[np.argmax(f1_scores)]
    best_f1 = max(f1_scores)
    
    final_pred = ndui_clean > best_t
    oa = accuracy_score(ghsl_bin, final_pred)
    kappa = cohen_kappa_score(ghsl_bin, final_pred)
    
    print(f"GHSL > {gt_thresh}%: Opt_T={best_t:.2f}, OA={oa:.4f}, F1={best_f1:.4f}, Kappa={kappa:.4f}")
