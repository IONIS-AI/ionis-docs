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

- **SSB is the only direct comparison** — both models target voice-viable paths
- **For digital modes (FT8, FT4, WSPR) and CW/RTTY**, IONIS provides predictions where no comparable reference model exists
- When FT8 operators use VOACAP and find "closed" paths that are wide open at -20 dB, that's not a VOACAP failure — it was never designed for that world

## PSK Reporter Acid Test (2026-02-10)

!!! success "84.14% Recall on Independent Data — Model Generalizes"
    Validated against 100K spots from 16.5M PSK Reporter observations.
    Real solar conditions (SFI=140, Kp=1.6). Data the model has never seen.

    | Test | Recall | Notes |
    |------|--------|-------|
    | Step I (training domain) | 96.38% | Contest paths |
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

## Step I: IONIS vs VOACAP (2026-02-11)

!!! success "IONIS V16 96.38% vs VOACAP 75.82% — 1M Contest QSOs"
    Comparison on 1,000,000 real contest QSO paths.
    IONIS V16 showed **+20.56 percentage point** improvement over VOACAP.

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
    IONIS showed higher correlation on 9 of 10 bands. VOACAP anti-correlated on low bands (160/80/60/40/30m).

    **Note:** Step K was measured with V13. V20 Golden Master achieves Pearson **+0.4879**
    — a substantial improvement from V13's +0.3675.

    See [Step K: Quality Test](step_k_quality_test.md) for full band-by-band results.

## Current Status: V20 Golden Master (2026-02-11)

!!! success "V20 Production Locked — All Criteria Met"
    IONIS V20 Golden Master validates V16 physics in clean, config-driven codebase.

    | Metric | Target | V20 Final | V16 Reference | Status |
    |--------|--------|-----------|---------------|--------|
    | Pearson | > +0.48 | **+0.4879** | +0.4873 | **PASS** |
    | Kp sidecar | > +3.0σ | **+3.487σ** | +3.445σ | **PASS** |
    | SFI sidecar | > +0.4σ | **+0.482σ** | +0.478σ | **PASS** |
    | RMSE | — | **0.862σ** | 0.860σ | Matched |

    Training: 100 epochs in 4h 16m on Mac Studio M3 Ultra (MPS backend).
    Checkpoint: `versions/v20/ionis_v20.pth`

### V17-V19 Post-Mortem

!!! warning "Failed Refactoring Series — Architectural Root Cause"
    V17-V19 failed due to missing constraints in the `IonisModel` refactoring:

    - **V19.4 Decisive Experiment**: Pure V16 data + IonisModel → sidecars died
    - **Conclusion**: Architecture was the problem, not data poisoning
    - **Recovery**: V20 uses original `IonisV12Gate` with all V16 Physics Laws

    See [IONIS-THESIS.md](https://github.com/KI7MT/ki7mt-ai-lab-devel/blob/main/IONIS-THESIS.md) for full autopsy.

### V16 Reference Metrics

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

## V20 Link Budget Battery (2026-02-11)

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

    See [V20 Link Budget Battery](v20_link_budget_battery.md) for
    full 24-profile results, per-band analysis, and solar breakdowns.

## Documentation

- [V20 Link Budget Battery](v20_link_budget_battery.md) — 24-profile station discrimination test
- [Step I: IONIS vs VOACAP](step_i_voacap_comparison.md) — 1M path comparison
- [Step K: Quality Test](step_k_quality_test.md) — 100K path Pearson correlation comparison
- [V12 Test Specification](v12_test_specification.md) — NASA-style test documentation (historical)
