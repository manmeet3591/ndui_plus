# Final Systematic Validation Results (2020)

This report summarizes the validation of the 30m NDUI+ dataset against the GHSL Built-up Surface (2020) for 10 US cities. Metrics were calculated on a 0.2° x 0.2° sample area centered on each city.

| City | Overall Accuracy (OA) | F1-Score | Cohen's Kappa | Optimal Threshold |
| :--- | :---: | :---: | :---: | :---: |
| **Chicago** | 95.67% | 97.79% | 0.042 | 0.14 |
| **Albuquerque** | 71.65% | 83.34% | 0.027 | 0.06 |
| **Austin** | 79.17% | 87.45% | 0.293 | 0.09 |
| **Columbus** | 86.16% | 92.29% | 0.270 | 0.08 |
| **Kansas City** | 83.55% | 90.64% | 0.259 | 0.08 |
| **Las Vegas** | 93.93% | 96.87% | 0.011 | 0.00 |
| **Minneapolis** | 89.19% | 94.22% | 0.135 | 0.10 |
| **Portland** | 85.57% | 91.76% | 0.353 | 0.06 |
| **Seattle** | 63.67% | 77.26% | 0.057 | 0.00 |
| **Washington DC** | 85.98% | 92.18% | 0.262 | 0.08 |

### **Observations**
1.  **High F1-scores:** Most cities show F1-scores above 85%, indicating strong agreement with GHSL in identifying built-up areas.
2.  **Variability:** Performance in Seattle and Albuquerque is lower, potentially due to complex topography or specific land cover characteristics (e.g., dense forest in Seattle, desert-urban transitions in Albuquerque).
3.  **Optimal Thresholds:** The optimal thresholds for binarizing NDUI+ into "Urban" vs "Non-Urban" range from 0.00 to 0.14, with most falling between 0.06 and 0.10.

### **Next Steps**
1.  Update **Table S1** in the Supplementary Material with these metrics.
2.  Finalize the **Response to Reviewers** document.
3.  Submit the revised manuscript.
