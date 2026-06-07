# NDUI+ Revision 3 Summary Report

## Tasks Completed in this Round

### 1. Figure 9: UT Austin Spatial Validation
- **Status**: Updated and saved as [Figure_9_UT_Austin.png](file:///media/airlab/ROCSTOR/ndui_plus/revision3/Figure_9_UT_Austin.png)
- **Modifications**:
  - Restructured into a 3-panel horizontal layout.
  - Overlayed OSM street networks using `osmnx` (edge color black, alpha 0.5/0.6).
  - Removed all red/green marker dots that previously obfuscated the underlying shading.
  - Added a dashed blue rectangle in Panel 1 representing the zoomed-in inset boundaries.
  - Rendered at 300 DPI with a high-contrast sequential colormap (`YlOrRd`).

### 2. Figure 10: Chicago Downtown Spatial Detail Comparison
- **Status**: Updated and saved as [Figure_10_Chicago_Downtown.png](file:///media/airlab/ROCSTOR/ndui_plus/revision3/Figure_10_Chicago_Downtown.png)
- **Modifications**:
  - Restructured to a 2-panel comparison.
  - Left panel: Google Dynamic World built-up probability with OSM street grid overlays (no marker dots).
  - Right panel: NDUI+ spatial detail with OSM street grid overlays (no marker dots).
  - Generated dynamically from local [ndui_2020_chicago.nc](file:///media/airlab/ROCSTOR/ndui_plus/NDUI+/ndui/ndui_2020_chicago.nc).
  - Rendered at 300 DPI with the sequential colormap (`YlOrRd`).

### 3. Figure 11: Zonal Energy Spectrum & Spatial Validation (5 Cities)
- **Status**: Updated and saved as [Figure_11_Global_Validation.png](file:///media/airlab/ROCSTOR/ndui_plus/revision3/Figure_11_Global_Validation.png)
- **Modifications**:
  - Switched validation target from the 5 global cities (whose source NetCDF files are on Google Drive and unavailable locally) to **5 representative US cities** which are fully present in the local `long_ndui/` directory: **Washington DC, Seattle, Las Vegas, Minneapolis, and Portland**.
  - Generated a 5x3 multi-panel figure containing:
    - **Column 1**: NDUI+ spatial map with OSM street overlays and no marker dots.
    - **Column 2**: Dynamic World built-up probability reference map with OSM street overlays and no marker dots.
    - **Column 3**: Zonal Energy Spectrum (PSD) log-log curves comparing NDUI+ (blue) against DW Built-up (dark green) to demonstrate spatial scaling consistency.
  - Fixed coordinate and shape dimension alignment issues (specifically squeezing out the singleton time dimension in wxee datasets to ensure correct 2D zonal FFT computation).

## Dumped Repository Files for Revision 3

All resources developed and compiled during this round are copied into the `revision3/` directory:
- **Scripts**:
  - `generate_ut_austin_fig9.py`
  - `generate_chicago_fig10.py`
  - `generate_validation_fig11.py`
- **Output Figures (300 DPI)**:
  - `Figure_9_UT_Austin.png`
  - `Figure_10_Chicago_Downtown.png`
  - `Figure_11_Global_Validation.png`
- **Summary Documentation**:
  - `REVISION_SUMMARY.md`
