---
description: >-
  IONIS prediction quality measured by Pearson correlation against observed SNR.
  V20 achieves +0.4879 on the validation set — 22x stronger correlation than
  VOACAP's +0.0218 on the same paths.
---

# Prediction Quality (Pearson Correlation)

**Date**: 2026-02-09
**Status**: COMPLETE
**Result**: IONIS showed +0.35 correlation improvement over reference model

!!! note "V20 Production"
    IONIS V20 achieves Pearson **+0.4879** — a substantial improvement
    from the +0.3675 measured in this initial test.

---

## Objective

The IONIS vs VOACAP comparison proved IONIS correctly identifies **if** a band is open (Recall). This test proves IONIS tracks the **quality** of the opening (Correlation).

If IONIS has higher Pearson r than VOACAP against ground truth SNR, it doesn't just know the band is open—it knows how strong the signal will be.

---

## Methodology

### Test Dataset

- **Source**: `validation.quality_test_paths` — 100K signatures from `wspr.signatures_v2_terrestrial`
- **Stratification**: 10K per band (160m through 10m)
- **Quality filter**: `spot_count > 50` (high-confidence ground truth)
- **Ground truth**: `median_snr` from signature bucket

### Dual Prediction

| Model | Method |
|-------|--------|
| **IONIS** | `oracle_v13.py` inference on M3 Ultra |
| **VOACAP** | Method 30 (SNRxx) via `voacapl` on 9975WX |

### Metrics

- **Pearson r**: Correlation between predicted SNR and actual `median_snr`
- **RMSE**: Root mean squared error (IONIS only; VOACAP has unit incompatibility)

---

## Results

### Overall Correlation

| Metric | IONIS | VOACAP | Delta |
|--------|-----------|--------|-------|
| **Pearson r** | **+0.3675** | +0.0218 | **+0.3456** |
| RMSE | 5.00 dB | — | — |
| Bias | -2.00 dB | — | — |

IONIS Pearson r = +0.3675 vs VOACAP r = +0.0218 (delta: +0.3456).

### Per-Band Breakdown

| Band | N | IONIS r | VOACAP r | Delta |
|------|---|---------|----------|-------|
| 160m | 10,000 | +0.2948 | -0.1950 | +0.4898 |
| 80m | 10,000 | +0.2664 | -0.2100 | +0.4764 |
| 60m | 10,000 | +0.2449 | -0.1817 | +0.4265 |
| 40m | 10,000 | +0.4214 | -0.1717 | +0.5932 |
| 30m | 10,000 | +0.2997 | -0.0892 | +0.3889 |
| 20m | 10,000 | +0.3850 | -0.0205 | +0.4054 |
| 17m | 10,000 | +0.4993 | -0.0258 | +0.5251 |
| 15m | 10,000 | +0.4979 | +0.0468 | +0.4511 |
| 12m | 10,000 | +0.3391 | +0.2691 | +0.0700 |
| 10m | 10,000 | +0.1244 | +0.1826 | -0.0583 |

**IONIS showed higher correlation on 9 of 10 bands.**

### Low-Band Analysis (160m-40m)

VOACAP shows **negative correlation** on low bands—when it predicts stronger signal, actual WSPR SNR is lower.

| Model | Pearson r |
|-------|-----------|
| IONIS | +0.3204 |
| VOACAP | -0.1963 |
| **Delta** | **+0.5167** |

---

## Physics Interpretation

### Why VOACAP is Anti-Correlated on Low Bands

When VOACAP was developed (1960s-70s), the "noise floor" was defined by human operators with headphones. A signal at -28 dB SNR wasn't "weak"—it was **non-existent**.

VOACAP was calibrated for **Information Throughput**: when is a signal strong enough for 60 WPM Teletype or clear SSB voice? It effectively ignores the "Sub-Audit Floor."

**On low bands**, VOACAP overcompensates for D-layer absorption. It assumes high absorption = "dead" path.

**The WSPR reality**: Paths stay open deep into the noise floor. Digital modes like WSPR and FT8 decode signals that were invisible to 1970s technology.

### The Resolution Difference

| Model | What it models |
|-------|----------------|
| **VOACAP** | The **Mirror** — can it reflect a high-power beam? |
| **IONIS** | The **Medium** — can any energy get through? |

IONIS learned the "Deep-Tissue Physics" of the ionosphere from 10.8B observations. It knows that absorption is a **dimmer switch**, not an **off switch**.

---

## Files

| File | Location |
|------|----------|
| Test script | `ionis-training/scripts/quality_test_ionis.py` |
| Test paths | `validation.quality_test_paths` (ClickHouse) |
| VOACAP results | `validation.quality_test_voacap` (ClickHouse) |

---

*Generated: 2026-02-09*
*IONIS — Ionospheric Neural Inference System (V20 Production)*
