# NDUI+: fused DMSP–VIIRS Normalized Difference Urban Index (30 m, annual)

Code for **"NDUI+: A fused DMSP–VIIRS global normalized difference urban index dataset for
annual 30 m urban monitoring"** (Singh, Ghosh, et al.).

NDUI+ extends the Normalized Difference Urban Index (Zhang et al., 2015) beyond the end of the
DMSP-OLS record. A SwinIR model is trained per region to translate VIIRS night lights into
DMSP-OLS-equivalent ("calibrated VIIRS") night lights for 2013 onward. These are fused with
annual 30 m Landsat NDVI to give a continuous annual NDUI series.

* **Trained weights and water masks:** Zenodo, doi:[10.5281/zenodo.24545916](https://doi.org/10.5281/zenodo.24545916)
  (`weights.tar.gz`, `water.tar.gz`). See [Data on Zenodo](#data-on-zenodo).
* **NDUI+ maps** are generated on demand from these weights with the code here, because a
  30 m annual global product (1999–2024) is too large to deposit as files.

---

## 1. Repository contents

| Path | Purpose |
|---|---|
| `SwinIR_train_function.py` | SwinIR network (unmodified upstream code, see §3) and the per-epoch `train()` loop |
| `model.py` | The exact SwinIR configuration used, plus helpers to load a Zenodo weight file for any lat/lon |
| `pipeline/train_cell_weights.py` | Trains one 5°×5° cell model and writes its weight file and water mask (produced the Zenodo deposit) |
| `pipeline/train_all_cells.py` | Runs the above for every cell on the global 5° grid |
| `long_dmsp_train_v3.ipynb` | Step 1 (city version): train city-centred 5°×5° models |
| `generate_dmsp.ipynb` | Step 2: DMSP-OLS 1992–2012 + calibrated VIIRS 2013–2024 → continuous "DMSP+" series |
| `generate_ndui_plus.ipynb` | Step 3: fuse DMSP+ with Landsat NDVI → annual 30 m NDUI+ (1999–2024) |
| `generate_ndui_v1.ipynb` | Single city, single year version of Step 3 |
| `generate_ndui_plus_without_dmsp_flag.ipynb` | Step 3 using a 5°×5° grid weight file instead of a city model |
| `revision/long_landsat_final.ipynb` | Model selection: the 15 candidate networks compared in Figure 1 |
| `plots/`, `revision2/`, `revision3/` | Scripts for the manuscript figures, GHSL/Dynamic World validation and sensitivity analysis |

The notebooks were developed on Google Colab (they mount Google Drive at `drive/MyDrive/...`);
change those paths to local folders when running elsewhere.

## 2. Installation

```bash
conda create -n ndui python=3.10 -y && conda activate ndui
pip install -r requirements.txt
earthengine authenticate          # Google Earth Engine account required
export EE_PROJECT=<your-gee-cloud-project>
```

A CUDA GPU is recommended for training; inference runs on CPU.

## 3. Model architecture: unmodified SwinIR

The network is the **original SwinIR implementation** (Liang et al., 2021,
`models/network_swinir.py` from https://github.com/JingyunLiang/SwinIR). **No layers were added,
removed or changed.** SwinIR was used in its image-restoration mode (no upsampling), with one
input and one output channel. The only differences from the upstream file are two constructor
defaults (`in_chans` 3→1, `upscale` 2→1). Both are also passed explicitly.

| Hyperparameter | Value |
|---|---|
| Input → output | 1 band (VIIRS `avg_rad`, regridded) → 1 band (DMSP-OLS `stable_lights`) |
| `upscale` | 1 (input and output on the same 927.67 m DMSP grid) |
| `img_size` / `patch_size` | 30 × 30 / 1 |
| `window_size` | 5 (shifted windows in alternate layers) |
| `embed_dim` | 60 |
| `depths` / `num_heads` | [6, 6, 6, 6] / [6, 6, 6, 6] (4 RSTB blocks × 6 Swin layers) |
| `mlp_ratio` | 2 |
| `drop_path_rate` | 0.1 |
| `img_range` | 1.0 |
| `upsampler` | `pixelshuffledirect` (with `upscale=1` this is a single 3×3 conv to 1 channel) |
| `resi_connection` | `1conv` |
| Trainable parameters | 882,385 |

This matches the "lightweight SwinIR" setting of Liang et al. (2021).

```python
from model import load_cell_model, cell_center, cell_weight_name
fname = cell_weight_name(*cell_center(41.88, -87.63))   # Chicago
net = load_cell_model("weights/" + fname)
```

## 4. Training details

One model is trained per 5°×5° region, using 2012, the year both sensors overlap.

1. **Inputs (Google Earth Engine).**
   * VIIRS: `NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG`, band `avg_rad`, mean of the 12 monthly
     composites of 2012, exported at 463.83 m. No additional thresholding is applied.
   * DMSP-OLS: `NOAA/DMSP-OLS/NIGHTTIME_LIGHTS`, band `stable_lights`, F18 2012, exported at
     927.67 m.
2. **Regridding.** VIIRS is interpolated (cubic) onto the DMSP grid.
3. **Normalisation.** VIIRS and DMSP are each divided by their maximum within the 5°×5° box.
   The two maxima are kept and reused at inference.
4. **Patches.** The top-left 600 × 600 pixels of the box are cut into 400 non-overlapping
   30 × 30 patches, in row-major order.
5. **Split.** Patches 0–199 train (50 %), 200–299 validation (25 %), 300–399 held out (25 %).
   *Note:* the scripts build `test_dataset` from the validation patches, so the held-out patches
   are not used and reported scores are validation scores.
6. **Optimisation.** Adam, learning rate 1e-3, MSE loss, batch size 20, at most 1000 epochs.
   Early stopping uses patience 500 epochs on validation loss. The checkpoint with the lowest
   validation loss is saved.

A separate model is trained for every 5°×5° cell (global grid) or city-centred 5°×5° box
(city notebooks). No weights are shared or transferred between regions. Cells with no 2012
night-light data (open ocean, polar regions outside DMSP-OLS coverage) have no model.

## 5. Generating NDUI+

**DMSP-OLS intercalibration (1992–2012).** Each annual composite is corrected with a
second-order polynomial, `DN' = a·DN + b·DN² + c`, applied to pixels with DN ≥ 5. The
coefficients for all 33 satellite-years are listed in the code; the reference is F15 2000
(a = 1, b = c = 0). One satellite is used per year: F10 1992–93, F12 1994–96, F14 1997–99,
F15 2000–03, F16 2004–09, F18 2010–12.

**Calibrated VIIRS (2013–2024).** The year's VIIRS composite is processed as in §4, scaled by the
2012 VIIRS maximum of the box, passed through the box's model, and multiplied by the 2012 DMSP
maximum. Negative outputs are set to 0.

**NDVI (30 m).** Landsat 7 Collection 2 Tier 1 TOA (`LANDSAT/LE07/C02/T1_TOA`) scenes in the
calendar year, excluding pixels where any of bands 1–5 or 7 is 0 (this removes SLC-off gaps
and fill). NDVI = (B4 − B3)/(B4 + B3). The annual composite is the per-pixel median, replaced by
the annual maximum where max > 0.4 and by the annual minimum where min < −0.2.

**NDUI+.** The DMSP+ value is interpolated (bilinear) to the 30 m NDVI grid and scaled to
[0, 1] by dividing by 63:

```
NDUI+ = (NTL − NDVI) / (NTL + NDVI),   clipped to [−1, 1]
```

**Water mask (optional, used for the manuscript figures).** Pixels with Dynamic World water
probability ≥ 0.3 are masked. `water.tar.gz` on Zenodo provides the 2017 mean water probability
per cell at 500 m. The figure scripts (`plots/generate_*`) use Dynamic World at 30 m for the
figure year.

## 6. Data on Zenodo

doi:[10.5281/zenodo.24545916](https://doi.org/10.5281/zenodo.24545916). The deposit has its own
README describing both archives. In brief:

* `weights.tar.gz` (3.4 GB) → `weights/best_model_lats_<S>_late_<N>_lons_<W>_lone_<E>.pth`:
  1,011 PyTorch `state_dict`s, one per 5°×5° cell between 60°S and 70°N. Load them with
  `model.load_cell_model()`.
* `water.tar.gz` (5.1 GB) → `water/water_dw_2017_<S>_late_<N>_lons_<W>_lone_<E>.nc`: 1,023
  NetCDF files (WGS84) holding the variable `water`, the 2017 mean Dynamic World water
  probability (0–1) at about 500 m. Every weight cell has a matching water file.

## 7. Citation

Singh, M., Ghosh, S., Kamath, H., Saxena, S., SB, V., Mitra, C., Sudharsan, N., Rao, S., Dashtian,
H., Magruder, L., Shepherd, M., & Niyogi, D. (2026). *NDUI+: A fused DMSP–VIIRS global normalized difference urban index
dataset for annual 30 m urban monitoring* [Data set]. Zenodo.
https://doi.org/10.5281/zenodo.24545916

Please also cite SwinIR: Liang, J. et al. (2021). SwinIR: Image restoration using Swin
Transformer. *ICCV Workshops*, 1833–1844.
