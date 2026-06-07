import ee
import wxee
import json
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import osmnx as ox
import os
import matplotlib.patches as patches

# 1. Initialize GEE
key_path = '/media/airlab/ROCSTOR/ndui_plus/NDUI+/ndui/ee-manmeet20singh15-wbis-fab7f1ca35e0.json'
with open(key_path) as f:
    key = json.load(f)
credentials = ee.ServiceAccountCredentials(key['client_email'], key_path)
ee.Initialize(credentials)
wxee.Initialize()
print("GEE and wxee initialized successfully!")

# 2. Define coordinates and bounds
latitude_center = 30.2850
longitude_center = -97.7335

# Zoomed-in bounds (0.01 degree radius)
lat_min_small, lat_max_small = latitude_center - 0.01, latitude_center + 0.01
lon_min_small, lon_max_small = longitude_center - 0.01, longitude_center + 0.01

# Larger domain bounds (0.025 degree radius)
lat_min_large, lat_max_large = latitude_center - 0.025, latitude_center + 0.025
lon_min_large, lon_max_large = longitude_center - 0.025, longitude_center + 0.025

aoi_small = ee.Geometry.Rectangle([lon_min_small, lat_min_small, lon_max_small, lat_max_small])

# 3. Fetch Dynamic World Built-up mean (2015-2024) from GEE
print("Fetching Dynamic World Built-up from GEE...")
start_date = '2015-01-01'
end_date = '2024-12-31'
dw_collection = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1') \
                  .filterDate(start_date, end_date) \
                  .select('built') \
                  .mean()
dw_collection = dw_collection.set('system:time_start', 0)
ds_built = dw_collection.wx.to_xarray(region=aoi_small, scale=30)
dw_var = list(ds_built.data_vars)[0]

# Rename coordinates if necessary
if 'x' in ds_built.coords:
    ds_built = ds_built.rename({'x': 'lon', 'y': 'lat'})

# 4. Load local NDUI+ data for Austin
print("Loading local NDUI+ data...")
ndui_path = '/media/airlab/ROCSTOR/ndui_plus/long_ndui/austin/ndui_austin_1999_2022.nc'
ds_ndui = xr.open_dataset(ndui_path)
ds_ndui_mean = ds_ndui.ndui.mean(dim='time')

# Slice NDUI+ for small and large domains
ds_ndui_small = ds_ndui_mean.sel(
    lat=slice(lat_max_small, lat_min_small) if ds_ndui_mean.lat[0] > ds_ndui_mean.lat[-1] else slice(lat_min_small, lat_max_small),
    lon=slice(lon_min_small, lon_max_small)
)

ds_ndui_large = ds_ndui_mean.sel(
    lat=slice(lat_max_large, lat_min_large) if ds_ndui_mean.lat[0] > ds_ndui_mean.lat[-1] else slice(lat_min_large, lat_max_large),
    lon=slice(lon_min_large, lon_max_large)
)

# 5. Fetch OSM street network
print("Fetching OSM street network using osmnx...")
bbox_large = (lon_min_large, lat_min_large, lon_max_large, lat_max_large)
G_large = ox.graph_from_bbox(bbox_large, network_type='drive')
edges_large = ox.graph_to_gdfs(G_large, nodes=False, edges=True)

# 6. Plotting the 3-panel figure
print("Generating plot...")
fig, axes = plt.subplots(1, 3, figsize=(24, 8), dpi=300)

# Panel 1: Larger Domain NDUI+ Map with OSM streets
ds_ndui_large.plot(ax=axes[0], cmap='YlOrRd', add_colorbar=True, cbar_kwargs={'label': 'NDUI+ Value', 'shrink': 0.8})
edges_large.plot(ax=axes[0], edgecolor='black', linewidth=0.5, alpha=0.5)

# Add a rectangle showing the inset boundary
rect = patches.Rectangle(
    (lon_min_small, lat_min_small),
    lon_max_small - lon_min_small,
    lat_max_small - lat_min_small,
    linewidth=2, edgecolor='blue', facecolor='none', linestyle='--'
)
axes[0].add_patch(rect)
axes[0].set_title('Larger Domain (Austin, TX) - NDUI+\nwith Inset Boundary (Blue)', fontsize=16)
axes[0].set_xlabel('Longitude', fontsize=12)
axes[0].set_ylabel('Latitude', fontsize=12)
axes[0].set_xlim([lon_min_large, lon_max_large])
axes[0].set_ylim([lat_min_large, lat_max_large])

# Panel 2: Zoomed-in Dynamic World Built-up Map with OSM streets (no dots)
ds_built_small = ds_built[dw_var]
ds_built_small.plot(ax=axes[1], cmap='YlOrRd', add_colorbar=True, cbar_kwargs={'label': 'Built-up Probability', 'shrink': 0.8})
edges_large.plot(ax=axes[1], edgecolor='black', linewidth=0.8, alpha=0.6)
axes[1].set_title('Dynamic World Built-up Area\n(Zoomed-in Inset)', fontsize=16)
axes[1].set_xlabel('Longitude', fontsize=12)
axes[1].set_ylabel('Latitude', fontsize=12)
axes[1].set_xlim([lon_min_small, lon_max_small])
axes[1].set_ylim([lat_min_small, lat_max_small])

# Panel 3: Zoomed-in NDUI+ Map with OSM streets (no dots)
ds_ndui_small.plot(ax=axes[2], cmap='YlOrRd', add_colorbar=True, cbar_kwargs={'label': 'NDUI+ Value', 'shrink': 0.8})
edges_large.plot(ax=axes[2], edgecolor='black', linewidth=0.8, alpha=0.6)
axes[2].set_title('NDUI+ Data\n(Zoomed-in Inset)', fontsize=16)
axes[2].set_xlabel('Longitude', fontsize=12)
axes[2].set_ylabel('Latitude', fontsize=12)
axes[2].set_xlim([lon_min_small, lon_max_small])
axes[2].set_ylim([lat_min_small, lat_max_small])

# plt.suptitle('Figure 9: Spatial Validation of NDUI+ against Dynamic World built-up reference (UT Austin)', fontsize=20, y=0.98)
plt.tight_layout()

# Save figure
os.makedirs('/media/airlab/ROCSTOR/ndui_plus/figures', exist_ok=True)
save_path = '/media/airlab/ROCSTOR/ndui_plus/figures/Figure_9_UT_Austin.png'
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Updated Figure 9 saved successfully to {save_path}!")
