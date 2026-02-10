# Validation Reports

Automated test results from IONIS model evaluations.

## Mode-Aware Validation

IONIS predicts signal-to-noise ratio (SNR) — a physical quantity. The operational
question **"Can I work this path right now, on my mode?"** is answered by applying
mode-specific thresholds to that prediction:

| Mode Family | Threshold | Recall (V16) | Interpretation |
|-------------|-----------|--------------|----------------|
| WSPR | -28 dB | ~97% | Model sees nearly all beacon paths |
| FT8/FT4 | -20 dB | 93.29% | Digital modes decode deep in the noise |
| CW | -10 dB | 93.77% | Most CW-viable paths detected |
| RTTY | -5 dB | 99.37% | Contest anchoring taught RTTY ceiling |
| SSB | +5 dB | **98.40%** | Contest anchoring taught voice ceiling |

V16's curriculum learning: WSPR taught the floor (-28 dB), contest logs taught
the ceiling (+10 dB). The model now knows the full dynamic range.

### VOACAP Comparison Context

VOACAP (ITS/NTIA) was designed for **SSB voice circuits** using 1960s-era ionosonde
coefficients. It has no concept of digital mode decode thresholds.

- **SSB is the only fair head-to-head comparison** — both models target voice-viable paths
- **For digital modes (FT8, FT4, WSPR) and CW/RTTY**, IONIS provides predictions where no comparable reference model exists
- When FT8 operators use VOACAP and find "closed" paths that are wide open at -20 dB, that's not a VOACAP failure — it was never designed for that world

## Step I: IONIS vs VOACAP (2026-02-11)

!!! success "IONIS V16 96.38% vs VOACAP 75.82% — 1M Contest QSOs"
    Head-to-head comparison on 1,000,000 real contest QSO paths.
    IONIS V16 Contest outperforms VOACAP by **+20.56 percentage points**.

    | Model | Overall Recall | vs VOACAP |
    |-------|----------------|-----------|
    | **IONIS V16** | **96.38%** | **+20.56 pp** |
    | IONIS V15 | 86.89% | +11.07 pp |
    | VOACAP | 75.82% | — |

    See [Step I: IONIS vs VOACAP](step_i_voacap_comparison.md) for
    full results by mode, band, and methodology.

## Step K: Quality of Prediction (2026-02-09)

!!! success "IONIS Pearson r=+0.3675 vs VOACAP r=+0.0218"
    100K high-confidence signatures (spot_count > 50), per-band Pearson correlation.
    IONIS wins 9 of 10 bands. VOACAP anti-correlated on low bands (160/80/60/40/30m).

    See [Step K: Quality Test](step_k_quality_test.md) for full band-by-band results.

## Current Status: V16 Contest

!!! success "96.38% Recall — 35/35 Tests Pass"
    IONIS V16 Contest — trained on:

    - WSPR signatures (93.3M) — floor physics
    - RBN DXpedition (91K × 50x) — rare path coverage
    - Contest anchors (6.34M) — ceiling proof (+10 dB SSB, 0 dB RTTY)

| Metric | Value |
|--------|-------|
| **Step I Recall** | 96.38% (VOACAP: 75.82%, +20.56 pp) |
| **SSB Recall** | 98.40% (V15: 81.01%, +17.4 pp) |
| **Pearson** | +0.4873 |
| **Physics Tests** | 4/4 PASS |
| **Oracle Tests** | 35/35 PASS |

**Recall by Mode (V16 vs V15):**

| Mode | V16 | V15 | Delta |
|------|-----|-----|-------|
| SSB | **98.40%** | 81.01% | **+17.4 pp** |
| RTTY | 99.37% | 83.79% | +15.6 pp |
| CW | 93.77% | 91.64% | +2.1 pp |
| Digital | 93.29% | 96.83% | -3.5 pp |

## Curriculum Learning

V16's success comes from teaching sequence:

1. **WSPR (floor)**: 10.8B observations at -28 dB — "what barely possible looks like"
2. **RBN DXpedition (rare)**: 91K from 152 DXCC — "unusual paths exist"
3. **Contest (ceiling)**: 6.34M proven QSOs at +10 dB — "strong signals exist"

The model learned the full dynamic range. WSPR alone only taught "marginal."

## V16 Test Suite

!!! note "35/35 Tests Pass"
    V16 uses the same oracle test suite as V12, updated for V16 baselines.

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
