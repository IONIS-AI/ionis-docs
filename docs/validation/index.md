# Validation Reports

Automated test results from IONIS model evaluations.

## Mode-Aware Validation

IONIS predicts signal-to-noise ratio (SNR) — a physical quantity. The operational
question **"Can I work this path right now, on my mode?"** is answered by applying
mode-specific thresholds to that prediction:

| Mode Family | Threshold | Recall (V15) | Interpretation |
|-------------|-----------|--------------|----------------|
| WSPR | -28 dB | ~97% | Model sees nearly all beacon paths |
| FT8/FT4 | -20 dB | 96.83% | Digital modes decode deep in the noise |
| CW | -10 dB | 91.64% | Most CW-viable paths detected |
| RTTY | -5 dB | 83.79% | Marginal paths begin to drop |
| SSB | +5 dB | 81.01% | Only strong paths survive for voice |

The model isn't "worse" at SSB — it correctly predicts marginal paths that clear the
digital thresholds but fail for voice. The physics is right; the bar is just higher.

### VOACAP Comparison Context

VOACAP (ITS/NTIA) was designed for **SSB voice circuits** using 1960s-era ionosonde
coefficients. It has no concept of digital mode decode thresholds.

- **SSB is the only fair head-to-head comparison** — both models target voice-viable paths
- **For digital modes (FT8, FT4, WSPR) and CW/RTTY**, IONIS provides predictions where no comparable reference model exists
- When FT8 operators use VOACAP and find "closed" paths that are wide open at -20 dB, that's not a VOACAP failure — it was never designed for that world

## Step I: IONIS vs VOACAP (2026-02-09)

!!! success "IONIS V15 86.89% vs VOACAP 75.82% — 1M Contest QSOs"
    Head-to-head comparison on 1,000,000 real contest QSO paths.
    IONIS V15 Diamond outperforms VOACAP by **+11.07 percentage points**.

    See [Step I: IONIS vs VOACAP](step_i_voacap_comparison.md) for
    full results by mode, band, and methodology.

## Step K: Quality of Prediction (2026-02-09)

!!! success "IONIS Pearson r=+0.3675 vs VOACAP r=+0.0218"
    100K high-confidence signatures (spot_count > 50), per-band Pearson correlation.
    IONIS wins 9 of 10 bands. VOACAP anti-correlated on low bands (160/80/60/40/30m).

    See [Step K: Quality Test](step_k_quality_test.md) for full band-by-band results.

## Current Status: V15 Diamond

!!! success "Physics Validated"
    IONIS V15 Diamond — trained on balloon-filtered WSPR signatures (93.3M) +
    RBN DXpedition synthesis (91K × 50x upsampled) covering 152 rare DXCC entities.

| Metric | Value |
|--------|-------|
| **Step I Recall** | 86.89% (VOACAP: 75.82%, +11 pp) |
| **Step K Pearson** | +0.3675 (VOACAP: +0.0218) |
| **SSB Recall** | 81.01% (+2 pp vs V13) |
| **Physics Tests** | 4/4 PASS |

**Recall by Mode (V15):**

| Mode | Recall | vs VOACAP |
|------|--------|-----------|
| Digital | 96.83% | No comparison (VOACAP doesn't model digital) |
| CW | 91.64% | No comparison |
| RTTY | 83.79% | No comparison |
| SSB | 81.01% | Fair fight — IONIS wins |

## V12 Test Suite (Historical Reference)

!!! note "V12 Archived"
    The V12 35-test automated suite is preserved as a reference baseline.
    V13 validation uses Step I (recall) and Step K (quality) instead.

    **Physics Score**: 74.2/100 (Grade C — targeted for improvement in V14+)

| Group | ID Range | Tests | Purpose |
|-------|----------|-------|---------|
| Canonical Paths | TST-100 | 10 | Known HF paths |
| Physics Constraints | TST-200 | 6 | Monotonicity, sidecars |
| Input Validation | TST-300 | 9 | Boundary checks |
| Robustness | TST-500 | 9 | Determinism, stability |
| Regression | TST-800 | 1 | Catch silent degradation |

## Documentation

- [Step I: IONIS vs VOACAP](step_i_voacap_comparison.md) — 1M path head-to-head comparison
- [Step K: Quality Test](step_k_quality_test.md) — 100K path Pearson correlation comparison
- [V12 Test Specification](v12_test_specification.md) — NASA-style test documentation (historical)
