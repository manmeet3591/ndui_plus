# Manuscript MLEARTH-100113 Revision Plan & Progress

## Status
- **Reviewer Reports Analyzed:** Yes
- **Technical Details Extracted:** Yes (SwinIR hyperparameters, Preprocessing logic)
- **Validation Implementation:** Notebook `ndui_plus_validation.ipynb` created.
- **Response Drafted:** File `Response_to_Reviewers.md` created.

## Key Updates for Revised Manuscript

### 1. Methodology (Addressing Referees 2 & 3)
- **SwinIR Training:** Added details on Adam optimizer (LR=0.001), 1000 epochs, MSE loss, and 30x30 patch size.
- **Preprocessing:** Explicitly mentioned VIIRS VCMCFG monthly composites and second-order polynomial intercalibration for DMSP.
- **NDVI Compositing:** Described the hybrid median-max-min approach at 30m resolution.
- **Landsat Continuity:** Corrected Landsat 7 mission end (2024) and SLC failure (2003). Documented the integration of Landsat 8 (2013-2021) and Landsat 9 (2022-present).
- **Monotonic Filter:** Explained the grid-based monotonic baseline filter used to stabilize seasonal fluctuations.

### 2. Results & Validation (Addressing Referee 2)
- **Systematic Validation:** Included global validation against GHSL. Reported Overall Accuracy (OA), F1-score, and Kappa coefficient using dynamically optimized thresholds.
- **Sensitivity Analysis:** Included a new Figure demonstrating the impact of the monotonic filter in regions with revegetation (available as `sensitivity_analysis.png`).
- **SSIM Metric:** Added Structural Similarity Index (SSIM) values to model comparison figures alongside PSNR.

### 3. Discussion & References (Addressing Referee 3)
- **Comparison with GISD30/GAIA:** Added a direct comparison with non-NTL global urban datasets.
- **Code/Data Availability:** Provided permanent links to the codebase and the NDUI+ dataset.
- **References:** Updated with recent 2025/2026 literature and corrected formatting errors. Added the missing preprint citation.

## Action Items for User
1. **Validation Complete:** Systematic validation metrics for 10 US cities have been generated and are available in `FINAL_VALIDATION_REPORT.md`.
2. **Update Figures:** Use the generated `sensitivity_analysis_chicago.png` and `validation_comparison_chicago.png` in the revised manuscript.
3. **Reference Style:** Ensure your reference manager is set to the journal's required format for the final resubmission.
