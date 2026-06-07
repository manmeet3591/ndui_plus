import ee
import wxee
import json
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import osmnx as ox
import os

# 1. Initialize GEE
key_path = '/media/airlab/ROCSTOR/ndui_plus/NDUI+/ndui/ee-manmeet20singh15-wbis-fab7f1ca35e0.json'
with open(key_path) as f:
    key = json.load(f)
credentials = ee.ServiceAccountCredentials(key['client_email'], key_path)
ee.Initialize(credentials)
wxee.Initialize()
print("GEE and wxee initialized successfully!")

# 2. Define Chicago downtown coordinates
latitude_center = 41.8820
longitude_center = -87.6250
lat_min, lat_max = latitude_center - 0.01, latitude_center + 0.01
lon_min, lon_max = longitude_center - 0.01, longitude_center + 0.01

aoi = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])

# 3. Fetch Dynamic World Built-up for 2020 from GEE
print("Fetching Dynamic World Built-up from GEE...")
start_date = '2020-01-01'
end_date = '2020-12-31'
dw_collection = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1') \
                  .filterDate(start_date, end_date) \
                  .select('built') \
                  .mean()
dw_collection = dw_collection.set('system:time_start', 0)
ds_built = dw_collection.wx.to_xarray(region=aoi, scale=30)
dw_var = list(ds_built.data_vars)[0]

# Rename coordinates if necessary
if 'x' in ds_built.coords:
    ds_built = ds_built.rename({'x': 'lon', 'y': 'lat'})

# 4. Load local Chicago NDUI+ data
print("Loading local Chicago NDUI+ data...")
ndui_path = '/media/airlab/ROCSTOR/ndui_plus/NDUI+/ndui/ndui_2020_chicago.nc'
ds_ndui = xr.open_dataset(ndui_path)

# Slice NDUI+ for Chicago downtown
ds_ndui_selected = ds_ndui.ndui.sel(
    lat=slice(lat_max, lat_min) if ds_ndui.lat[0] > ds_ndui.lat[-1] else slice(lat_min, lat_max),
    lon=slice(lon_min, lon_max)
)

# 5. Fetch OSM street network
print("Fetching OSM street network using osmnx...")
bbox = (lon_min, lat_min, lon_max, lat_max)
G = ox.graph_from_bbox(bbox, network_type='drive')
edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

# 6. Plotting
print("Generating plot...")
fig, axes = plt.subplots(1, 2, figsize=(18, 8), dpi=300)

# Panel 1: Dynamic World Built-up Map with OSM streets
ds_built_small = ds_built[dw_var]
ds_built_small.plot(ax=axes[0], cmap='YlOrRd', add_colorbar=True, cbar_kwargs={'label': 'Built-up Probability', 'shrink': 0.8})
edges.plot(ax=axes[0], edgecolor='black', linewidth=0.8, alpha=0.6)
axes[0].set_title('Dynamic World Built-up Area\n(Chicago Downtown)', fontsize=16)
axes[0].set_xlabel('Longitude', fontsize=12)
axes[0].set_ylabel('Latitude', fontsize=12)
axes[0].set_xlim([lon_min, lon_max])
axes[0].set_ylim([lat_min, lat_max])

# Panel 2: NDUI+ Map with OSM streets
ds_ndui_selected.plot(ax=axes[1], cmap='YlOrRd', add_colorbar=True, cbar_kwargs={'label': 'NDUI+ Value', 'shrink': 0.8})
edges.plot(ax=axes[1], edgecolor='black', linewidth=0.8, alpha=0.6)
axes[1].set_title('NDUI+ Data\n(Chicago Downtown)', fontsize=16)
axes[1].set_xlabel('Longitude', fontsize=12)
axes[1].set_ylabel('Latitude', fontsize=12)
axes[1].set_xlim([lon_min, lon_max])
axes[1].set_ylim([lat_min, lat_max])

plt.suptitle('Figure 10: Spatial detail comparison of NDUI+ and Dynamic World (Chicago Downtown)', fontsize=18, y=0.98)
plt.tight_layout()

# Save figure
os.makedirs('/media/airlab/ROCSTOR/ndui_plus/figures', exist_ok=True)
save_path = '/media/airlab/ROCSTOR/ndui_plus/figures/Figure_10_Chicago_Downtown.png'
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Updated Figure 10 saved successfully to {save_path}!")
