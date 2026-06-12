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

# 2. Define Cities and Paths (5 Representative US Cities)
cities = {
    'Washington DC': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/washington_DC/ndui_washington_DC_1999_2022.nc',
    'Seattle': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/seattle/ndui_seattle_1999_2022.nc',
    'Las Vegas': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/Las_Vegas/ndui_Las_Vegas_1999_2022.nc',
    'Minneapolis': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/minneapolis/ndui_minneapolis_1999_2022.nc',
    'Portland': '/media/airlab/ROCSTOR/ndui_plus/long_ndui/portland/ndui_portland_1999_2022.nc'
}

# Load GDW Built-up and Water layers from GEE (Image Collection)
gdw_image = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1') \
              .filterDate('2015-01-01', '2024-12-31') \
              .select(['built', 'water']) \
              .mean()
gdw_image = gdw_image.set('system:time_start', 0)

# 3. Zonal Energy Spectrum function (PSD)
def compute_zonal_energy_spectrum(da):
    da_filled = da.fillna(0)
    lon_spacing = 360 / da_filled.sizes["lon"]
    circumference = 2 * np.pi * 6371e3 * np.cos(np.radians(da_filled["lat"]))
    
    # Zonal DFT
    dft = np.fft.fft(da_filled, axis=1) / da_filled.sizes["lon"]
    dft_amplitude = np.abs(dft)
    
    energy_spectrum = 2 * (dft_amplitude ** 2)
    energy_spectrum[..., 0] /= 2
    energy_spectrum = energy_spectrum[..., : da_filled.sizes["lon"] // 2]
    
    circumference_da = xr.DataArray(
        circumference, dims=["lat"], coords={"lat": da_filled["lat"]}
    )
    circumference_da_expanded = circumference_da.broadcast_like(
        da_filled.isel(lon=slice(0, energy_spectrum.shape[1]))
    )
    
    scaled_spectrum = energy_spectrum * circumference_da_expanded
    psd_mean = scaled_spectrum.mean(dim="lat")
    return psd_mean

# 4. Generate plots for each city and combine
fig, axes = plt.subplots(5, 3, figsize=(20, 24), dpi=300)

for idx, (city_name, city_path) in enumerate(cities.items()):
    print(f"\n--- Processing {city_name} ---")
    ds_ndui = xr.open_dataset(city_path)
    
    # Extract 2020 or latest time slice
    if 'time' in ds_ndui.dims:
        try:
            ds_ndui_slice = ds_ndui.sel(time='2020-01-01', method='nearest')
        except:
            ds_ndui_slice = ds_ndui.isel(time=-1)
    else:
        ds_ndui_slice = ds_ndui
        
    ndui_var = 'ndui' if 'ndui' in ds_ndui_slice.data_vars else list(ds_ndui_slice.data_vars)[0]
    
    # Define AOI (Center of the dataset)
    lon_min, lat_min = ds_ndui_slice.lon.min().item(), ds_ndui_slice.lat.min().item()
    lon_max, lat_max = ds_ndui_slice.lon.max().item(), ds_ndui_slice.lat.max().item()
    
    lon_mid = (lon_min + lon_max) / 2
    lat_mid = (lat_min + lat_max) / 2
    
    # Bounding box for 0.2 x 0.2 degree sample
    aoi_bbox = (lon_mid - 0.1, lat_mid - 0.1, lon_mid + 0.1, lat_mid + 0.1)
    aoi_gee = ee.Geometry.Rectangle(list(aoi_bbox))
    
    # Fetch GDW Built-up layer from GEE
    print(f"Fetching GDW layers for {city_name}...")
    ds_gdw = gdw_image.wx.to_xarray(region=aoi_gee, scale=30)
    gdw_var = 'built'
    if 'x' in ds_gdw.coords:
        ds_gdw = ds_gdw.rename({'x': 'lon', 'y': 'lat'})
        
    # Slice NDUI+ to match the GEE region
    lat_range = slice(lat_mid + 0.1, lat_mid - 0.1) if ds_ndui_slice.lat[0] > ds_ndui_slice.lat[-1] else slice(lat_mid - 0.1, lat_mid + 0.1)
    ds_ndui_small = ds_ndui_slice.sel(lat=lat_range, lon=slice(lon_mid - 0.1, lon_mid + 0.1))
    
    # Clean coordinate dimensions (drop variables and squeeze dimensions if necessary) to avoid interpolation conflicts
    if 'time' in ds_ndui_small.dims:
        ds_ndui_small = ds_ndui_small.squeeze(dim='time')
    if 'time' in ds_ndui_small.coords:
        ds_ndui_small = ds_ndui_small.drop_vars('time')
        
    if 'time' in ds_gdw.dims:
        ds_gdw = ds_gdw.squeeze(dim='time')
    if 'time' in ds_gdw.coords:
        ds_gdw = ds_gdw.drop_vars('time')
        
    # Align grids
    ds_gdw_aligned = ds_gdw.interp(lat=ds_ndui_small.lat, lon=ds_ndui_small.lon, method='nearest')
    
    # Create water mask (water probability < 0.3) to prevent high NDUI artifacts on water bodies
    water_mask = ds_gdw_aligned['water'].fillna(0) < 0.3
    
    # Mask both NDUI+ and DW Built-up
    ndui_masked = ds_ndui_small[ndui_var] * water_mask
    gdw_masked = ds_gdw_aligned[gdw_var] * water_mask
        
    # Fetch OSM streets using osmnx
    print(f"Fetching OSM streets for {city_name}...")
    try:
        G = ox.graph_from_bbox(aoi_bbox, network_type='drive')
        edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    except Exception as e:
        print(f"Failed to fetch OSM streets for {city_name}: {e}")
        edges = None

    # Calculate PSD
    print(f"Calculating PSD for {city_name}...")
    psd_ndui = compute_zonal_energy_spectrum(ndui_masked)
    psd_gdw = compute_zonal_energy_spectrum(gdw_masked)
    
    # Plotting Panel 1: NDUI+ Map (Masked)
    ndui_masked.plot(ax=axes[idx, 0], cmap='YlOrRd', vmin=0, vmax=1, add_colorbar=True, cbar_kwargs={'shrink': 0.7, 'label': 'NDUI+ Value'})
    if edges is not None:
        edges.plot(ax=axes[idx, 0], edgecolor='black', linewidth=0.5, alpha=0.5)
    axes[idx, 0].set_title(f"NDUI+ Map ({city_name})", fontsize=12)
    axes[idx, 0].set_xlabel("Longitude")
    axes[idx, 0].set_ylabel("Latitude")
    axes[idx, 0].set_xlim([lon_mid - 0.1, lon_mid + 0.1])
    axes[idx, 0].set_ylim([lat_mid - 0.1, lat_mid + 0.1])
    
    # Plotting Panel 2: Google Dynamic World Map (Masked)
    gdw_masked.plot(ax=axes[idx, 1], cmap='YlOrRd', vmin=0, vmax=1, add_colorbar=True, cbar_kwargs={'shrink': 0.7, 'label': 'Built-up Probability'})
    if edges is not None:
        edges.plot(ax=axes[idx, 1], edgecolor='black', linewidth=0.5, alpha=0.5)
    axes[idx, 1].set_title(f"Dynamic World Built-up ({city_name})", fontsize=12)
    axes[idx, 1].set_xlabel("Longitude")
    axes[idx, 1].set_ylabel("Latitude")
    axes[idx, 1].set_xlim([lon_mid - 0.1, lon_mid + 0.1])
    axes[idx, 1].set_ylim([lat_mid - 0.1, lat_mid + 0.1])
    
    # Plotting Panel 3: Zonal Energy Spectrum Plot (PSD)
    wavenumbers = np.arange(psd_ndui.sizes["lon"])
    axes[idx, 2].loglog(wavenumbers, psd_ndui, label="NDUI+", linewidth=2.5, color="blue")
    axes[idx, 2].loglog(wavenumbers, psd_gdw, label="DW Built-up", linewidth=2.5, color="darkgreen")
    axes[idx, 2].set_xlabel("Zonal Wavenumber")
    axes[idx, 2].set_ylabel("Power Spectral Density")
    axes[idx, 2].set_title(f"Zonal Energy Spectrum ({city_name})", fontsize=12)
    axes[idx, 2].grid(True, which="both", linestyle="--", linewidth=0.6, alpha=0.8)
    axes[idx, 2].legend(loc="upper right")
    axes[idx, 2].set_xlim([1, psd_ndui.sizes["lon"] // 2])

# plt.suptitle('Figure 11: Representative Validation of NDUI+ across 5 US Cities with OSM Street Overlays and Zonal Energy Spectrum (PSD) comparison', fontsize=18, y=0.99)
plt.tight_layout()

# Save combined figure
os.makedirs('/media/airlab/ROCSTOR/ndui_plus/figures', exist_ok=True)
save_path = '/media/airlab/ROCSTOR/ndui_plus/figures/Figure_11_Global_Validation.png'
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"\nUpdated Figure 11 saved successfully to {save_path}!")
