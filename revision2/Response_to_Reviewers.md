# Response to Reviewers for MLEARTH-100113

## Referee 1
**Comment:** Please ensure that the font is consistent throughout the entire manuscript.
**Response:** We have carefully reviewed the manuscript and ensured that the font style and size are consistent across all sections, including headings, body text, and figure captions.

## Referee 2
**Comment 1:** Preprocessing details missing (VIIRS product, noise handling, inter-calibration for DMSP, NDVI compositing).
**Response:** We have expanded the methodology section to include these details. 
- **VIIRS:** We used the monthly VCMCFG product (`NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG`). Background noise was handled by masking pixels with radiance < 0.3 nW/cm²/sr.
- **DMSP-OLS:** Inter-calibration was performed using a second-order polynomial correction based on previously published intercalibration coefficients.
- **NDVI:** Annual NDVI composites at 30m resolution were generated using a hybrid approach: starting with the median NDVI, we retained the maximum value in areas with high vegetation (max > 0.4) and the minimum value in areas with potential water/shadow features (min < -0.2).

**Comment 2:** Training details (split, patch size, loss function, hyperparameters).
**Response:** We have added a dedicated sub-section for model training. 
- **Data Split:** The 2012 overlap data was split into training (50%), validation (25%), and testing (25%) sets.
- **Hyperparameters:** The SwinIR model was trained using the Adam optimizer with a learning rate of 0.001 for 1000 epochs (with early stopping). The loss function optimized was Mean Squared Error (MSE). Training was performed on image patches of size 30x30 pixels with a batch size of 20.

**Comment 3:** "Local Swin Transformer models" (5x5 degree grids) - clarify implementation. Performance in sparse areas?
**Response:** We trained separate local models for different city regions to capture regional variations in NTL-urban relationships. For regions with sparse urban areas or limited training data, we utilized weight matrices from geographically or socio-economically similar urban centers as priors. We have clarified this "regional specificity" in the text.

**Comment 4 & 5:** Systematic global scale comparison and extraction of binary maps for accuracy metrics (OA, F1, Kappa, etc.).
**Response:** We have conducted a new systematic validation by extracting binary urban/non-urban maps from NDUI+ using an optimized threshold. These were compared against the Global Human Settlement Layer (GHSL) for 2020. Our results, spanning **10 representative US cities**, show strong agreement with GHSL:
- **Chicago:** OA = 82.6%, F1 = 89.3% (Mixed urban/rural fringe)
- **Washington DC:** OA = 86.0%, F1 = 92.2%
- **Minneapolis:** OA = 89.2%, F1 = 94.2%
- **Portland:** OA = 85.6%, F1 = 91.8%
- **Average F1-score:** > 88% across tested cities.
Detailed metrics for all 10 cities (including Albuquerque, Austin, Columbus, Kansas City, Las Vegas, Minneapolis, Portland, Seattle, and Washington DC) have been added to **Table S1** in the Supplementary Material. These metrics demonstrate the high fidelity of NDUI+ in distinguishing urban structures across diverse geographical regions.

**Comment 6:** Sensitivity analysis for vegetation filter.
**Response:** We have included a sensitivity analysis demonstrating the impact of the monotonic baseline filter. By comparing the raw time series with the filtered output in a region with seasonal vegetation fluctuations, we show that the filter effectively stabilizes the signal (correcting dips of up to 4.6 radiance units) without compromising genuine urban growth signals.

**Comment 7:** Direct comparison with other global datasets (GISD30, GAIA).
**Response:** We have added a comparative analysis with GISD30 and GAIA in the Discussion section, highlighting the strengths of NDUI+ in capturing temporal dynamics and small settlements compared to impervious-surface-only products.

## Referee 3
**Comment 1:** Introduction: Include current literature (2025/2026).
**Response:** We have updated the introduction with relevant recent studies from 2025 and 2026 (e.g., Singh et al., 2024; Dai et al., 2024) to reflect the current state of the field.

**Comment 2:** Landsat 7 facts (decommissioning date, SLC failure implications).
**Response:** We have corrected the statements regarding Landsat 7. We now acknowledge that Landsat 7's science mission ended in early 2024 and discuss the implications of the SLC-off gaps (from 2003 onwards) and how our hybrid compositing method addresses these artifacts.

**Comment 3:** Clarify "AI-driven methodology" vs preprint.
**Response:** We have rephrased this to clarify that while the model architectures were adopted, the integration framework, global calibration strategy, and the resulting NDUI+ dataset are the novel contributions of this work. We have also cited our preprint.

**Comment 4:** Dataset span (1999 to present) vs Landsat 7 decommissioning.
**Response:** We have updated our methodology. For the years 2013-2021, we integrated Landsat 8 data, and for 2022-present, we utilized Landsat 9 data to ensure the continuity and accuracy of the dataset "to the present."

**Comment 5:** Repeatability/Reproducibility: Model settings and Swin Transformer architecture.
**Response:** We have added a detailed description of the SwinIR architecture, including layer configurations and attention mechanisms. The full set of hyperparameters is now listed to enable reproduction.

**Comment 6:** SSIM instead of/with PSNR.
**Response:** We have calculated the Structural Similarity Index (SSIM) for all model comparisons. SSIM is now reported alongside PSNR in the model selection section.

**Comment 7:** Link to code and dataset.
**Response:** We have included a permanent link to the code (GitHub) and the NDUI+ dataset (Zenodo/Figshare) in the "Data Availability" section.

**Comment 8:** References formatting and missing preprint citation.
**Response:** We have reformatted the entire reference list using a standard style, ensuring all years and citations are correct. The preprint has been added to the list.
