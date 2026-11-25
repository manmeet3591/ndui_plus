# NDUI+ regional SwinIR weights and water masks

**Record:** doi:10.5281/zenodo.13953525
**Code:** https://github.com/manmeet3591/ndui_plus
**Paper:** Singh, Ghosh, et al., "NDUI+: A fused DMSP–VIIRS global normalized difference urban
index dataset for annual 30 m urban monitoring"

## What this deposit is

NDUI+ is an annual, 30 m Normalized Difference Urban Index that runs past the end of DMSP-OLS
(2013). To do this, VIIRS night lights are translated into DMSP-OLS-equivalent values with a
SwinIR model trained separately for each 5°×5° region on the 2012 overlap year.

This deposit holds **everything needed to regenerate NDUI+ for any location and year from public
Google Earth Engine inputs without retraining**:

| File | Size | md5 | Contents |
|---|---|---|---|
| `weights.tar.gz` | 3.37 GB | `bbf7efb8a0cca62a89dc6aeada03d0e9` | 1,011 trained SwinIR models, one per 5°×5° cell |
| `water.tar.gz` | 5.13 GB | `fede9f42118f28ef0221d84ab465b5f9` | 1,023 Dynamic World water-probability rasters, one per cell |
| `README.md` | — | — | this file |

The 30 m NDUI+ maps themselves are not stored here. A global 30 m annual stack for 1999–2024 is
far too large to deposit. They are produced from these files with the code in the GitHub
repository (§5).

## 1. Grid and file naming

The globe is divided into 5°×5° cells with centres at latitude −87.5, −82.5, …, 87.5 and
longitude −177.5, −172.5, …, 177.5. Each file name encodes its cell bounds in decimal degrees
(WGS84):

```
weights/best_model_lats_<S>_late_<N>_lons_<W>_lone_<E>.pth
water/water_dw_2017_<S>_late_<N>_lons_<W>_lone_<E>.nc
```

`S`, `N` = south and north latitude; `W`, `E` = west and east longitude. For example,
`best_model_lats_40.0_late_45.0_lons_-90.0_lone_-85.0.pth` covers 40–45° N, 90–85° W (Chicago).

To find the cell for a point (lat, lon):

```python
import math
S = math.floor(lat / 5) * 5;  W = math.floor(lon / 5) * 5
name = f"best_model_lats_{float(S)}_late_{float(S+5)}_lons_{float(W)}_lone_{float(W+5)}.pth"
```

**Coverage.** There are 1,011 cells between 60° S and 70° N. Cells with no 2012 DMSP/VIIRS night
lights, mostly open ocean and areas outside DMSP-OLS coverage, have no model.

## 2. `weights.tar.gz`

Unpacks to `weights/` (1,011 files, about 4.9 MB each). Each file is a PyTorch `state_dict`
for the **original, unmodified SwinIR** network (Liang et al., 2021) with this configuration:

| Parameter | Value |
|---|---|
| `in_chans` | 1 |
| `upscale` | 1 |
| `img_size` | (30, 30) |
| `patch_size` | 1 |
| `window_size` | 5 |
| `embed_dim` | 60 |
| `depths` | [6, 6, 6, 6] |
| `num_heads` | [6, 6, 6, 6] |
| `mlp_ratio` | 2 |
| `drop_path_rate` | 0.1 |
| `img_range` | 1.0 |
| `upsampler` | `pixelshuffledirect` |
| `resi_connection` | `1conv` |

```python
# from the GitHub repository root
from model import load_cell_model
net = load_cell_model("weights/best_model_lats_40.0_late_45.0_lons_-90.0_lone_-85.0.pth")
```

**Input:** 1 × 30 × 30 patches of 2012-normalised VIIRS radiance on the DMSP grid (927.67 m).
**Output:** DMSP-OLS-equivalent `stable_lights` on the same grid, also normalised.

**Training** (identical for every cell):
* Data: VIIRS `NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG` `avg_rad` (2012 mean of monthly composites),
  cubic-interpolated to the grid of DMSP-OLS F18 2012 `stable_lights`.
* Normalisation: each layer divided by its maximum within the cell.
* Patches: 600 × 600 px → 400 patches of 30 × 30; 200 train / 100 validation / 100 held out.
* Adam (lr 1e-3), MSE loss, batch 20, ≤ 1000 epochs, early stopping with patience 500; the
  checkpoint with the lowest validation loss is saved.

The per-cell normalisation maxima are not stored. Recompute them from the 2012 VIIRS and DMSP
images of the cell, as `generate_dmsp.ipynb` does.

## 3. `water.tar.gz`

Unpacks to `water/` (1,023 NetCDF files, about 10 MB each).

| Item | Value |
|---|---|
| Variable | `water` (float64), Dynamic World V1 water probability, 0–1 |
| Source / period | `GOOGLE/DYNAMICWORLD/V1`, mean of all 2017 observations |
| Grid | WGS84 (EPSG:4326), about 0.0045° (500 m), about 1114 × 1116 px per cell |
| Dimensions | `time` (1, placeholder 1970-01-01), `y`, `x` |
| Missing | `NaN` where Dynamic World has no 2017 observation (e.g. open ocean) |

Use: mask NDUI+ pixels with water probability ≥ 0.3. Water bodies have negative NDVI and would
otherwise produce falsely high NDUI values. Every weight cell has a matching water file. The 12
extra files are off-grid boxes left over from test runs (8 at 180–175° W and 4 at 20.5–25.5° N whose bounds do not
fall on the 5° grid). They have no corresponding model
and can be ignored.

```python
import xarray as xr
w = xr.open_dataset("water/water_dw_2017_40.0_late_45.0_lons_-90.0_lone_-85.0.nc")["water"][0]
```

## 4. Regenerating NDUI+ (summary)

1. **1992–2012:** DMSP-OLS `stable_lights`, intercalibrated with second-order polynomial
   coefficients (listed in the code).
2. **2013–2024:** annual VIIRS → (scale by the cell's 2012 VIIRS max) → SwinIR → (× the cell's
   2012 DMSP max) → DMSP-equivalent night lights.
3. Landsat 7 annual NDVI composite at 30 m: median, with the annual max where max > 0.4 and the
   annual min where min < −0.2.
4. `NDUI+ = (NTL/63 − NDVI) / (NTL/63 + NDVI)`, clipped to [−1, 1]; optionally water-masked.

Step-by-step code: `generate_dmsp.ipynb`, then `generate_ndui_plus.ipynb` in the GitHub
repository. The weights here can be retrained with `pipeline/train_all_cells.py`.

## 5. Licence and citation

Licence: as set on this Zenodo record. Please cite:

Singh, M., Ghosh, S., Kamath, H., Saxena, S., SB, V., Mitra, C., Sudharsan, N., Rao, S., Dashtian,
H., Magruder, L., Shepherd, M., & Niyogi, D. (2024). NDUI+: A fused DMSP-VIIRS based multidecadal,
high-resolution global normalized difference urban index (NDUI) dataset [Data set]. Zenodo.
https://doi.org/10.5281/zenodo.13953525
