---
description: >-
  IONIS model validation results: VOACAP comparison on 1M paths, link budget
  battery, Pearson correlation analysis, and physics constraint verification.
---

# Validation Reports

Automated test results from IONIS model evaluations.

## Current Status: IONIS V22-gamma + PhysicsOverrideLayer (Phase 4.0)

!!! success "V22-gamma Production — Best Physics Model"
    V22-gamma extends V20 with solar depression features and a deterministic
    PhysicsOverrideLayer for high-band night closure.

    | Metric | V22-gamma | V20 Baseline |
    |--------|-----------|--------------|
    | Pearson | **+0.492** | +0.4879 |
    | RMSE | **0.821σ** | 0.862σ |
    | KI7MT operator tests | **17/17** | 16/17 |
    | TST-900 band x time | **9/11** | — |
    | Parameters | **205,621** | 203,573 |

    Checkpoint: `ionis_v22_gamma.safetensors` (805 KB)
    PhysicsOverrideLayer: deterministic clamp for freq >= 21 MHz night paths.

## Mode-Aware Validation

IONIS predicts signal-to-noise ratio (SNR) — a physical quantity. The operational
question **"Can I work this path right now, on my mode?"** is answered by applying
mode-specific thresholds to that prediction:

| Mode Family | Threshold | Recall | Interpretation |
|-------------|-----------|--------|----------------|
| WSPR | -28 dB | ~97% | Model sees nearly all beacon paths |
| FT8/FT4 | -20 dB | 93.29% | Digital modes decode deep in the noise |
| CW | -10 dB | 93.77% | Most CW-viable paths detected |
| RTTY | -5 dB | 99.37% | Contest anchoring taught RTTY ceiling |
| SSB | +5 dB | **98.40%** | Contest anchoring taught voice ceiling |

Curriculum learning: WSPR taught the floor (-28 dB), contest logs taught
the ceiling (+10 dB). The model now knows the full dynamic range.

### VOACAP Comparison Context

[VOACAP](https://www.voacap.com/) ([ITS/NTIA](https://www.its.bldrdoc.gov/)) was designed for **SSB voice circuits** using 1960s-era ionosonde
coefficients. It has no concept of digital mode decode thresholds.

- **SSB is the only direct comparison** — both models target voice-viable paths
- **For digital modes (FT8, FT4, WSPR) and CW/RTTY**, IONIS provides predictions where no comparable reference model exists
- When FT8 operators use VOACAP and find "closed" paths that are wide open at -20 dB, that's not a VOACAP failure — it was never designed for that world

## [PSK Reporter](https://pskreporter.info) Acid Test (2026-02-10)

!!! success "84.14% Recall on Independent Data — Model Generalizes"
    Validated against 100K spots from 16.5M PSK Reporter observations.
    Real solar conditions (SFI=140, Kp=1.6). Data the model has never seen.

    | Test | Recall | Notes |
    |------|--------|-------|
    | IONIS vs VOACAP (training domain) | 96.38% | Contest paths |
    | **PSK Reporter (independent)** | **84.14%** | Acid test |

    **By Mode:**

    | Mode | Recall | Spots |
    |------|--------|-------|
    | FT8 | 83.61% | 91,682 |
    | WSPR | 100% | 4,729 |
    | FT4 | 82.30% | 2,729 |
    | CW | 59.33% | 804 |

    **By Band:**

    | Band | Recall | Notes |
    |------|--------|-------|
    | 15m-10m | 94-96% | F2 mastery |
    | 20m-17m | 81-89% | Solid |
    | 160m-80m | 45-69% | NVIS gap |

    Key insight: -3 pp drop with real SFI (140 vs 150 default) proves model
    responds to solar conditions — physics, not memorization.

## IONIS vs VOACAP (2026-02-11)

!!! success "IONIS 96.38% vs VOACAP 75.82% — 1M Contest QSOs"
    Comparison on 1,000,000 real contest QSO paths.
    IONIS showed **+20.56 percentage point** improvement over VOACAP.

    | Model | Overall Recall | vs VOACAP |
    |-------|----------------|-----------|
    | **IONIS** | **96.38%** | **+20.56 pp** |
    | VOACAP | 75.82% | — |

    See [IONIS vs VOACAP](step_i_voacap_comparison.md) for
    full results by mode, band, and methodology.

## Prediction Quality (2026-02-09)

!!! success "IONIS Pearson r=+0.3675 vs VOACAP r=+0.0218"
    100K high-confidence signatures (spot_count > 50), per-band Pearson correlation.
    IONIS showed higher correlation on 9 of 10 bands. VOACAP anti-correlated on low bands (160/80/60/40/30m).

    **Note:** IONIS V20 achieves Pearson **+0.4879**
    — a substantial improvement from the original +0.3675 measurement.

    See [Prediction Quality](step_k_quality_test.md) for full band-by-band results.

## Link Budget Battery (2026-02-11)

!!! success "24 Profiles Tested — Full Discrimination Curve Mapped"
    Validated V20 model predictions across 24 station profiles from
    WSPR baseline (0 dB) to EME (+70.8 dB) against 3 ground truth sources.

    **Discrimination Curve (RBN, 56.7M paths):**

    | Profile | Advantage | Recall | Tier |
    |---------|-----------|--------|------|
    | wspr | +0.0 dB | 15.61% | baseline |
    | qrp_portable | +11.0 dB | 91.86% | **GOLDILOCKS** |
    | home_station | +31.0 dB | 100.00% | saturated |
    | contest_cw | +53.0 dB | 100.00% | saturated |

    **Key insight**: The model predicts ionospheric propagation correctly.
    Station profiles provide the "gearbox" for operational predictions.
    The ~92% QRP recall confirms the model discriminates between
    easy and hard paths — exactly what operators need.

    See [Link Budget Battery](v20_link_budget_battery.md) for
    full 24-profile results, per-band analysis, and solar breakdowns.

## Curriculum Learning

Training success comes from teaching sequence:

1. **WSPR (floor)**: 10.8B observations at -28 dB — "what barely possible looks like"
2. **RBN DXpedition (rare)**: 91K from 152 DXCC — "unusual paths exist"
3. **Contest (ceiling)**: 6.34M proven QSOs at +10 dB — "strong signals exist"

The model learned the full dynamic range. WSPR alone only taught "marginal."

## Test Suite

!!! note "V22-gamma: KI7MT 18/18, TST-900 9/11 (29 tests)"
    The V22-gamma test suite validates operator-grounded physics and band x time
    discrimination. Replaces the V20 62-test battery with focused physics gates.

| Group | Tests | Purpose |
|-------|-------|---------|
| KI7MT Operator Tests | 18 | Operator-grounded paths from 49K QSOs + 5.7M contest signatures |
| TST-900 Band x Time | 11 | Band discrimination across day/night/twilight periods |

The KI7MT tests include 4 gates: raw model (16/17), PhysicsOverrideLayer (17/17),
zero regressions, and acid test verification.

## Documentation

- [Link Budget Battery](v20_link_budget_battery.md) — 24-profile station discrimination test
- [IONIS vs VOACAP](step_i_voacap_comparison.md) — 1M path comparison
- [Prediction Quality](step_k_quality_test.md) — 100K path Pearson correlation comparison
- [Test Specification](test_specification.md) — TST-100 through TST-800 test suite
