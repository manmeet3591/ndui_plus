import ee
import wxee
import xarray as xr
import numpy as np
import json
import os
from sklearn.metrics import f1_score, accuracy_score, cohen_kappa_score
import pandas as pd

# 1. Initialize GEE
key_path = '/media/airlab/ROCSTOR/ndui_plus/NDUI+/ndui/ee-manmeet20singh15-wbis-fab7f1ca35e0.json'
with open(key_path) as f:
    key = json.load(f)
credentials = ee.ServiceAccountCredentials(key['client_email'], key_path)
ee.Initialize(credentials)
wxee.Initialize()

# 2. Define Cities and Paths
cities = {
    'Chicago': '/media/airlab/ROCSTOR/ndui_plus/NDUI+/ndui/ndui_2020_chicago.nc',
    'Albuquerque': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/albuquerque/ndui_albuquerque_1999_2022.nc',
    'Austin': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/austin/ndui_austin_1999_2022.nc',
    'Columbus': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/columbus/ndui_columbus_1999_2022.nc',
    'Kansas City': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/kansas_city/ndui_kansas_city_1999_2022.nc',
    'Las Vegas': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/Las_Vegas/ndui_Las_Vegas_1999_2022.nc',
    'Minneapolis': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/minneapolis/ndui_minneapolis_1999_2022.nc',
    'Portland': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/portland/ndui_portland_1999_2022.nc',
    'Seattle': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/seattle/ndui_seattle_1999_2022.nc',
    'Washington DC': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/washington_DC/ndui_washington_DC_1999_2022.nc'
}

# Load GHSL Built-up Surface for 2020 from GEE
ghsl = ee.Image("JRC/GHSL/P2023A/GHS_BUILT_S/2020")

def validate_city(city_name, city_path):
    print(f"\n--- Validating {city_name} ---")
    ds_ndui = xr.open_dataset(city_path)
    
    # Extract 2020 if time dimension exists
    if 'time' in ds_ndui.dims:
        try:
            ds_ndui = ds_ndui.sel(time='2020-01-01', method='nearest')
        except:
            # Fallback if 2020 is not exactly available
            ds_ndui = ds_ndui.isel(time=-1)
    
    # Variable name check
    ndui_var = 'ndui' if 'ndui' in ds_ndui.data_vars else list(ds_ndui.data_vars)[0]
    
    # Define AOI (Center of the dataset)
    lon_min, lat_min = ds_ndui.lon.min().item(), ds_ndui.lat.min().item()
    lon_max, lat_max = ds_ndui.lon.max().item(), ds_ndui.lat.max().item()
    
    lon_mid = (lon_min + lon_max) / 2
    lat_mid = (lat_min + lat_max) / 2
    
    # For systematic validation, we take a 0.2 x 0.2 degree sample
    # For smaller datasets (like the 9 cities), we might take the whole thing if it's small enough
    # but GEE to_xarray has limits, so 0.2 is safe.
    aoi = ee.Geometry.Rectangle([lon_mid - 0.1, lat_mid - 0.1, lon_mid + 0.1, lat_mid + 0.1])
    
    print(f"Fetching GHSL for {city_name}...")
    ds_ghsl = ghsl.wx.to_xarray(region=aoi, scale=30)
    ghsl_var = list(ds_ghsl.data_vars)[0]
    ds_ghsl = ds_ghsl.rename({'x': 'lon', 'y': 'lat'})
    
    # Slice NDUI to match sample area
    lat_range = slice(lat_mid + 0.1, lat_mid - 0.1) if ds_ndui.lat[0] > ds_ndui.lat[-1] else slice(lat_mid - 0.1, lat_mid + 0.1)
    ds_ndui_small = ds_ndui.sel(lat=lat_range, lon=slice(lon_mid - 0.1, lon_mid + 0.1))

    # Align grids
    # Drop time from coords if present to avoid interp issues
    if 'time' in ds_ndui_small.coords:
        ds_ndui_small = ds_ndui_small.drop_vars('time')
    if 'time' in ds_ghsl.coords:
        ds_ghsl = ds_ghsl.drop_vars('time')

    ds_ghsl_aligned = ds_ghsl.interp(lat=ds_ndui_small.lat, lon=ds_ndui_small.lon, method='nearest')
    
    # Metrics
    ndui_flat = ds_ndui_small[ndui_var].values.flatten()
    ghsl_flat = ds_ghsl_aligned[ghsl_var].values.flatten()
    
    mask = ~np.isnan(ndui_flat) & ~np.isnan(ghsl_flat)
    ndui_clean = ndui_flat[mask]
    ghsl_raw = ghsl_flat[mask]
    
    if len(ndui_clean) == 0:
        raise ValueError("No valid pixels found in sample area.")
        
    # GHSL > 20% validation
    ghsl_bin = (ghsl_raw > 20).astype(int)
    thresholds = np.linspace(0.0, 0.5, 51)
    f1_scores = [f1_score(ghsl_bin, ndui_clean > t) for t in thresholds]
    best_t = thresholds[np.argmax(f1_scores)]
    best_f1 = max(f1_scores)
    
    final_pred = ndui_clean > best_t
    oa = accuracy_score(ghsl_bin, final_pred)
    kappa = cohen_kappa_score(ghsl_bin, final_pred)
    
    print(f"Results for {city_name}: Opt_T={best_t:.2f}, OA={oa:.4f}, F1={best_f1:.4f}, Kappa={kappa:.4f}")
    return {'city': city_name, 'oa': oa, 'f1': best_f1, 'kappa': kappa, 'opt_t': best_t}

results = []
for city, path in cities.items():
    try:
        res = validate_city(city, path)
        results.append(res)
    except Exception as e:
        print(f"Failed to validate {city}: {e}")

print("\n--- Final Systematic Validation Summary ---")
df_results = pd.DataFrame(results)
print(df_results.to_string(index=False))
df_results.to_csv('systematic_validation_results.csv', index=False)
