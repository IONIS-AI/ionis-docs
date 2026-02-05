# IONIS-TEST-[ID]: [Test Name]

- **Timestamp**: YYYY-MM-DD HH:MM
- **Model Checkpoint**: `models/ionis_v10_final.pth`
- **Test Objective**: (e.g., Verify SNR degradation on trans-auroral paths during high Kp.)

## 1. Methodology

- **Data Source**: (e.g., 50,000 holdout rows from Polar Regions)
- **Conditions**: (e.g., SFI=150, Kp range 0-9)
- **Metric Focus**: Pearson Correlation vs. RMSE

## 2. Physical Verification (Ionis Integrity Check)

- **SFI Monotonicity**: [PASS/FAIL]
- **Kp Monotonicity**: [PASS/FAIL]
- **Expected Sensitivity**: (e.g., Did SNR drop by at least 1.0 dB at Kp 9?)

## 3. Quantitative Results

| Metric | Expected | Actual | Delta |
|--------|----------|--------|-------|
| RMSE | < 2.50 | — | — |
| Pearson | > 0.20 | — | — |

## 4. Visual Evidence

(Links to heatmap images, scatter plots, response curves)

## 5. Analysis & Conclusion

(Summary of findings, physics interpretation, any anomalies detected)
