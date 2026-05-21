# NDUI+ Revision Summary Report

## Tasks Completed

### 1. Systematic Validation (Chicago)
- **Status:** Verified.
- **Metrics (GHSL > 20%):**
  - **Overall Accuracy (OA):** 82.56% (Draft response: 82.5%)
  - **F1-score:** 89.28% (Draft response: 89.3%)
  - **Optimal Threshold:** 0.10
- **Verification Script:** `verify_all_cities.py` successfully reproduces these metrics using the local `ndui_2020_chicago.nc` file and GEE-fetched GHSL data.

### 2. Sensitivity Analysis (Monotonic Filter)
- **Status:** Verified.
- **Max Correction:** 4.6402 radiance units (Draft response: 4.6).
- **Figure:** `sensitivity_analysis_chicago.png` generated and ready for manuscript insertion.
- **Logic:** Confirmed that the monotonic baseline filter effectively stabilizes seasonal fluctuations without compromising growth signals.

### 3. Methodology & References
- **Status:** Documented in `REVISION_PROGRESS.md` and `Response_to_Reviewers.md`.
- **Key Updates:** Corrected Landsat 7 facts, added SwinIR hyperparameters, and included 2025/2026 literature citations.

## Pending Items

### 1. Validation for 9 Additional US Cities
- **Cities:** Albuquerque, Austin, Columbus, Kansas City, Las Vegas, Minneapolis, Portland, Seattle, Washington DC.
- **Issue:** 30m NDUI+ datasets for these cities were not found in the local workspace. Intermediate 1km SwinIR outputs exist for Baltimore and Beaumont, but these are not suitable for high-resolution comparison with GHSL.
- **Action Required:** Ensure the 30m `.nc` files for these cities are uploaded to the `NDUI+/ndui/` directory, then run `verify_all_cities.py` (updated to include these cities if data is available).

### 2. Final Manuscript Formatting
- **Status:** The draft responses are complete, but they need to be integrated into the final `.docx` or `.tex` manuscript.
- **Reference Style:** Ensure the reference list matches the journal's (IEEE GRSS) specific style.

## Recommended Next Steps
1. Locate or generate the 30m NDUI+ files for the 9 additional cities.
2. Update Table S1 in the Supplementary Material with the verified metrics.
3. Finalize the `Response_to_Reviewers.md` and submit.
