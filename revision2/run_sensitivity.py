import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# Load Chicago time series
ds = xr.open_dataset('/media/airlab/ROCSTOR/ndui_plus/NDUI+/ndui/Chicago/dmsp_swinIR_1992_2022_Chicago.nc')

# Extract a spatial mean time series (representing city-scale trends)
# We use the DMSP variable as a proxy for the urban index logic
data = ds.dmsp.mean(dim=['lat', 'lon']).values

# Apply monotonic baseline filter
def apply_monotonic_filter(ts):
    filtered = ts.copy()
    for t in range(1, len(filtered)):
        filtered[t] = np.maximum(filtered[t], filtered[t-1])
    return filtered

filtered_data = apply_monotonic_filter(data)
years = ds.time.dt.year.values

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(years, data, 'o--', label='Raw DMSP (with fluctuations)', alpha=0.6)
plt.plot(years, filtered_data, 'r-', linewidth=2, label='Filtered (Monotonic Baseline)')
plt.title('Sensitivity Analysis: Impact of Monotonic Filter (Chicago)')
plt.xlabel('Year')
plt.ylabel('Mean Radiance / Urban Index Proxy')
plt.legend()
plt.grid(True)
plt.savefig('/media/airlab/ROCSTOR/ndui_plus/sensitivity_analysis_chicago.png', dpi=300)

print(f"Sensitivity analysis completed. Plot saved to /media/airlab/ROCSTOR/ndui_plus/sensitivity_analysis_chicago.png")
print(f"Max difference between raw and filtered: {np.max(filtered_data - data):.4f}")
