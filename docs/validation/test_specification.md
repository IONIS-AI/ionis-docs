# IONIS Test Specification

**Document Version:** 2.0
**Model Version:** IonisGate V20 (Production)
**Checkpoint:** `versions/v20/ionis_v20.pth`
**Date:** 2026-02-16
**Author:** IONIS

!!! note "Implementation Status"
    This document specifies the full IONIS test suite. Currently implemented:

    - **verify_v20.py** — TST-200 (Physics Constraints): 4/6 tests automated
    - **test_v20.py** — Sensitivity analysis with geographic bias checks (TST-701)
    - **validate_v20_pskr.py** — Live PSK Reporter validation

    Test groups TST-100, TST-300, TST-400, TST-500, TST-600, TST-800 are specified but not yet automated.

---

## Overview

This document specifies the automated test suite for IONIS. Each test has:
- **ID**: Unique identifier (TST-XXX)
- **Purpose**: What physics or behavior is being validated
- **Method**: How the test works
- **Expected Result**: What constitutes PASS/FAIL
- **Failure Mode**: What a failure indicates
- **Hallucination Trap**: Tests designed to catch model overconfidence

The test suite runs via two scripts in `versions/v20/`:

```bash
cd /Users/gbeam/workspace/ionis-ai/ionis-training

# Physics verification (4 core tests)
.venv/bin/python versions/v20/verify_v20.py

# Sensitivity analysis (8 sweeps)
.venv/bin/python versions/v20/test_v20.py
```

**Implementation Status:** The scripts above implement TST-200 (Physics Constraints) and portions of TST-700 (Geographic Bias). The remaining test groups (TST-100, TST-300, TST-400, TST-500, TST-600, TST-800) are specified below but not yet automated.

---

## Test Groups

### Core Tests (Domain-Specific)

| Group | ID Range | Purpose |
|-------|----------|---------|
| Canonical Paths | TST-100 | Known HF paths with expected behavior |
| Physics Constraints | TST-200 | Monotonicity and sidecar validation |
| Input Validation | TST-300 | Boundary checks and invalid input rejection |
| Hallucination Traps | TST-400 | Inputs outside training domain |

### Extended Tests (Standard ML)

| Group | ID Range | Purpose |
|-------|----------|---------|
| Model Robustness | TST-500 | Determinism, stability, numerical safety |
| Adversarial/Security | TST-600 | Malicious input handling |
| Bias & Fairness | TST-700 | Systematic prediction biases |
| Regression | TST-800 | Catch silent degradation |

**Note:** Extended tests are standard ML model validation — they apply to any neural network regardless of domain. Core tests are specific to ionospheric propagation physics.

---

## Group 1: Canonical Paths (TST-100)

These tests verify the model produces reasonable predictions for well-known HF propagation paths.

### TST-101: US East Coast to Western Europe (20m Day)

| Field | Value |
|-------|-------|
| **Purpose** | Validate classic transatlantic 20m path during daylight |
| **TX Location** | W3 area: 39.14°N, 77.01°W (Maryland) |
| **RX Location** | G area: 51.50°N, 0.12°W (London) |
| **Frequency** | 14.0 MHz (20m) |
| **Conditions** | SFI 150, Kp 2, 14:00 UTC |
| **Distance** | ~5,900 km |
| **Expected Result** | SNR > -25 dB (path OPEN) |
| **Pass Criteria** | Model predicts usable WSPR signal |
| **Failure Mode** | If CLOSED: Model underestimating F2 skip on mid-latitude path |
| **Notes** | This is the most reliable transatlantic path; should always be open under these conditions |

### TST-102: US East Coast to Western Europe (20m Night)

| Field | Value |
|-------|-------|
| **Purpose** | Validate transatlantic path during darkness (grey line effects) |
| **TX Location** | W3 area: 39.14°N, 77.01°W |
| **RX Location** | G area: 51.50°N, 0.12°W |
| **Frequency** | 14.0 MHz (20m) |
| **Conditions** | SFI 150, Kp 2, 04:00 UTC |
| **Expected Result** | SNR > -25 dB (path OPEN, possibly marginal) |
| **Pass Criteria** | Model predicts path open (grey line propagation) |
| **Failure Mode** | If CLOSED: Model not capturing grey line enhancement |
| **Notes** | 20m can stay open on this path even at night due to grey line |

### TST-103: US West Coast to Japan (20m)

| Field | Value |
|-------|-------|
| **Purpose** | Validate long-path Pacific crossing |
| **TX Location** | W6 area: 34.05°N, 118.24°W (Los Angeles) |
| **RX Location** | JA area: 35.68°N, 139.69°E (Tokyo) |
| **Frequency** | 14.0 MHz (20m) |
| **Conditions** | SFI 150, Kp 2, 16:00 UTC |
| **Distance** | ~8,800 km |
| **Expected Result** | SNR > -25 dB (path OPEN) |
| **Pass Criteria** | Model predicts usable signal on trans-Pacific path |
| **Failure Mode** | If CLOSED: Model underestimating long-path propagation |
| **Notes** | Classic DX path; well-represented in WSPR data |

### TST-104: Greenland to Finland (Polar Path, Quiet)

| Field | Value |
|-------|-------|
| **Purpose** | Validate high-latitude path under quiet geomagnetic conditions |
| **TX Location** | OX area: 64.18°N, 51.72°W (Nuuk, Greenland) |
| **RX Location** | OH area: 60.17°N, 24.94°E (Helsinki) |
| **Frequency** | 14.0 MHz (20m) |
| **Conditions** | SFI 150, Kp 2, 12:00 UTC |
| **Distance** | ~3,200 km |
| **Expected Result** | SNR > -25 dB (path OPEN) |
| **Pass Criteria** | Model predicts open path when Kp is low |
| **Failure Mode** | If CLOSED: Model over-penalizing high-latitude paths |
| **Notes** | Polar paths are viable when geomagnetically quiet |

### TST-105: Greenland to Finland (Polar Path, Storm)

| Field | Value |
|-------|-------|
| **Purpose** | Validate storm degradation on high-latitude path |
| **TX Location** | OX area: 64.18°N, 51.72°W |
| **RX Location** | OH area: 60.17°N, 24.94°E |
| **Frequency** | 14.0 MHz (20m) |
| **Conditions** | SFI 150, Kp 8, 12:00 UTC |
| **Expected Result** | SNR degraded but > -25 dB (MARGINAL) |
| **Pass Criteria** | Model shows significant degradation vs TST-104 |
| **Failure Mode** | If no degradation: Storm sidecar not working |
| **Notes** | Kp 8 is severe; path should be heavily degraded but WSPR may still decode |

### TST-106: Brazil to India (Equatorial Path)

| Field | Value |
|-------|-------|
| **Purpose** | Validate equatorial/trans-equatorial propagation |
| **TX Location** | PY area: 23.55°S, 46.63°W (São Paulo) |
| **RX Location** | VU area: 12.97°N, 77.59°E (Bangalore) |
| **Frequency** | 14.0 MHz (20m) |
| **Conditions** | SFI 150, Kp 2, 14:00 UTC |
| **Distance** | ~14,000 km |
| **Expected Result** | SNR > -25 dB (path OPEN) |
| **Pass Criteria** | Model predicts long equatorial path viable |
| **Failure Mode** | If CLOSED: Model underestimating equatorial F2 |
| **Notes** | Equatorial paths less affected by Kp storms |

### TST-107: NVIS 80m (Short Path)

| Field | Value |
|-------|-------|
| **Purpose** | Validate Near Vertical Incidence Skywave on 80m |
| **TX Location** | 40.0°N, 100.0°W (Central US) |
| **RX Location** | 42.0°N, 98.0°W (~250 km away) |
| **Frequency** | 3.5 MHz (80m) |
| **Conditions** | SFI 100, Kp 2, 02:00 UTC (night) |
| **Distance** | ~250 km |
| **Expected Result** | SNR > -20 dB (strong NVIS) |
| **Pass Criteria** | Model predicts strong signal on short nighttime 80m path |
| **Failure Mode** | If weak: Model not capturing NVIS propagation |
| **Notes** | 80m NVIS is bread-and-butter regional communication |

### TST-108: US to Europe 10m (Low SFI)

| Field | Value |
|-------|-------|
| **Purpose** | Validate 10m behavior under marginal solar conditions |
| **TX Location** | W3 area: 39.14°N, 77.01°W |
| **RX Location** | G area: 51.50°N, 0.12°W |
| **Frequency** | 28.0 MHz (10m) |
| **Conditions** | SFI 80, Kp 2, 14:00 UTC |
| **Expected Result** | SNR > -25 dB (marginal but OPEN for WSPR) |
| **Pass Criteria** | Model predicts degraded but usable path |
| **Failure Mode** | N/A — test validates relative behavior vs TST-109 |
| **Notes** | Low SFI makes 10m difficult but not impossible |

### TST-109: US to Europe 10m (High SFI)

| Field | Value |
|-------|-------|
| **Purpose** | Validate 10m improvement with high solar flux |
| **TX Location** | W3 area: 39.14°N, 77.01°W |
| **RX Location** | G area: 51.50°N, 0.12°W |
| **Frequency** | 28.0 MHz (10m) |
| **Conditions** | SFI 200, Kp 2, 14:00 UTC |
| **Expected Result** | SNR better than TST-108, > -20 dB |
| **Pass Criteria** | Model shows SFI improvement on 10m |
| **Failure Mode** | If no improvement: Sun sidecar not affecting higher bands |
| **Notes** | High SFI should significantly improve 10m propagation |

---

## Group 2: Physics Constraints (TST-200)

These tests verify the model's learned physics matches ionospheric reality.

### Physics Scoring System

Each physics test is graded on a 0-100 scale based on how well the model matches expected ionospheric behavior.

| Grade | Score | Meaning |
|-------|-------|---------|
| **A** | 90-100 | Excellent — matches real-world physics closely |
| **B** | 75-89 | Good — correct direction, reasonable magnitude |
| **C** | 60-74 | Acceptable — correct direction, weak magnitude |
| **D** | 40-59 | Poor — barely correct or flat response |
| **F** | 0-39 | Fail — wrong direction or no response |

### Scoring Criteria by Test Type

**SFI Monotonicity (TST-201, TST-205)**
Expected: +1 to +4 dB improvement for SFI 70→200

| Delta (dB) | Score | Grade |
|------------|-------|-------|
| ≥ +3.0 | 100 | A |
| +2.0 to +2.9 | 85 | B |
| +1.0 to +1.9 | 70 | C |
| +0.1 to +0.9 | 50 | D |
| ≤ 0 | 0 | F |

**Kp Storm Cost (TST-202, TST-204)**
Expected: +2 to +6 dB degradation for Kp 0→9

| Cost (dB) | Score | Grade |
|-----------|-------|-------|
| ≥ +4.0 | 100 | A |
| +3.0 to +3.9 | 90 | A |
| +2.0 to +2.9 | 75 | B |
| +1.0 to +1.9 | 60 | C |
| +0.1 to +0.9 | 40 | D |
| ≤ 0 | 0 | F |

**D-Layer Absorption (TST-203)**
Expected: 20m better than 80m at noon by +1 to +5 dB

| Delta (dB) | Score | Grade |
|------------|-------|-------|
| ≥ +3.0 | 100 | A |
| +1.0 to +2.9 | 80 | B |
| 0 to +0.9 | 60 | C |
| -1.0 to -0.1 | 40 | D |
| < -1.0 | 0 | F |

**Polar Storm Sensitivity (TST-204)**
Expected: High-latitude paths more affected by Kp than mid-latitude

| Polar vs Mid-lat ratio | Score | Grade |
|------------------------|-------|-------|
| ≥ 1.2x | 100 | A |
| 1.1x to 1.19x | 80 | B |
| 1.0x to 1.09x | 60 | C |
| 0.9x to 0.99x | 40 | D |
| < 0.9x | 0 | F |

### Overall Physics Score

The model receives an aggregate physics score:

```
Physics Score = (TST-201 + TST-202 + TST-203 + TST-204 + TST-205 + TST-206) / 6
```

| Overall Score | Rating |
|---------------|--------|
| 90-100 | Production Ready |
| 75-89 | Research Quality |
| 60-74 | Needs Improvement |
| < 60 | Not Recommended |

### TST-201: SFI Monotonicity (70 vs 200)

| Field | Value |
|-------|-------|
| **Purpose** | Verify higher solar flux improves signal strength |
| **Method** | Compare SNR at SFI 70 vs SFI 200, all else equal |
| **Path** | W3 → G, 20m, Kp 2, 14:00 UTC |
| **Expected Result** | SNR(SFI 200) > SNR(SFI 70) by at least +1 dB |
| **Pass Criteria** | Delta is positive |
| **Failure Mode** | If negative or zero: Sun sidecar physics inverted or dead |
| **Actual** | +2.1 dB improvement |
| **Notes** | This is fundamental ionospheric physics — higher SFI = higher MUF = better HF |

### TST-202: Kp Monotonicity (0 vs 9)

| Field | Value |
|-------|-------|
| **Purpose** | Verify geomagnetic storms degrade signal strength |
| **Method** | Compare SNR at Kp 0 vs Kp 9, all else equal |
| **Path** | W3 → G, 20m, SFI 150, 14:00 UTC |
| **Expected Result** | SNR(Kp 9) < SNR(Kp 0) by at least -2 dB |
| **Pass Criteria** | Delta is negative (storm cost positive) |
| **Failure Mode** | If positive: Storm sidecar physics inverted (CRITICAL BUG) |
| **Actual** | +4.0 dB storm cost |
| **Notes** | This was the "Kp inversion problem" that plagued V1-V9 |

### TST-203: D-Layer Absorption (80m vs 20m at Noon)

| Field | Value |
|-------|-------|
| **Purpose** | Verify daytime D-layer absorption affects lower frequencies |
| **Method** | Compare 3.5 MHz vs 14.0 MHz at solar noon |
| **Path** | W3 → G, SFI 150, Kp 2, 12:00 UTC |
| **Expected Result** | SNR(20m) >= SNR(80m) at noon |
| **Pass Criteria** | Delta >= 0 dB |
| **Failure Mode** | If 80m better at noon: Model missing D-layer physics |
| **Actual** | +0.0 dB (equal) |
| **Notes** | Model shows equal; real physics expects 20m better. |

### TST-204: Polar Storm Degradation (Kp 2 vs 8)

| Field | Value |
|-------|-------|
| **Purpose** | Verify storms hit high-latitude paths harder |
| **Method** | Compare Kp 2 vs Kp 8 on polar path |
| **Path** | OX → OH, 20m, SFI 150, 12:00 UTC |
| **Expected Result** | Storm cost > 2 dB |
| **Pass Criteria** | Significant degradation observed |
| **Failure Mode** | If < 1 dB: Storm gate not modulating by latitude |
| **Actual** | +2.5 dB degradation |
| **Notes** | Validates latitude-dependent storm sensitivity |

### TST-205: 10m SFI Sensitivity

| Field | Value |
|-------|-------|
| **Purpose** | Verify higher bands more sensitive to SFI |
| **Method** | Compare SFI 80 vs 200 on 10m path |
| **Path** | W3 → G, 28 MHz, Kp 2, 14:00 UTC |
| **Expected Result** | Delta > +1.5 dB |
| **Pass Criteria** | 10m shows strong SFI dependence |
| **Failure Mode** | If < 1 dB: Sun sidecar not frequency-aware |
| **Actual** | +2.0 dB improvement |
| **Notes** | 10m needs high SFI; model should capture this |

### TST-206: Grey Line / Twilight Enhancement

| Field | Value |
|-------|-------|
| **Purpose** | Verify model captures grey line propagation enhancement |
| **Method** | Compare SNR at 14:00 UTC vs 18:00 UTC on E-W path |
| **Path** | W3 → G, 20m, SFI 150, Kp 2 |
| **Expected Result** | SNR(18 UTC) >= SNR(14 UTC) |
| **Pass Criteria** | Twilight hour shows equal or better propagation |
| **Failure Mode** | If negative: Model missing grey line physics |
| **Actual** | +0.2 dB enhancement |
| **Notes** | Grey line (twilight) often enhances E-W paths due to lower D-layer absorption |

**Grey Line Scoring Criteria**

| Delta (dB) | Score | Grade |
|------------|-------|-------|
| ≥ +1.0 | 100 | A |
| +0.5 to +0.9 | 85 | B |
| 0 to +0.4 | 70 | C |
| -0.5 to -0.1 | 50 | D |
| < -0.5 | 0 | F |

---

## Group 3: Input Validation (TST-300)

These tests verify the oracle rejects invalid inputs gracefully.

### TST-301: VHF Frequency Rejection (EME Trap)

| Field | Value |
|-------|-------|
| **Purpose** | Reject frequencies outside HF training domain |
| **Input** | freq_mhz = 144.0 (2m band) |
| **Expected Result** | ValueError raised |
| **Pass Criteria** | Oracle refuses to predict |
| **Failure Mode** | If prediction made: Model will hallucinate nonsense |
| **Notes** | EME at 144 MHz is lunar reflection, not ionospheric — completely different physics |

### TST-302: UHF Frequency Rejection

| Field | Value |
|-------|-------|
| **Purpose** | Reject UHF frequencies |
| **Input** | freq_mhz = 432.0 (70cm band) |
| **Expected Result** | ValueError raised |
| **Pass Criteria** | Oracle refuses to predict |
| **Failure Mode** | Model has no training data for UHF |
| **Notes** | UHF propagation is tropospheric scatter or satellite, not ionospheric |

### TST-303: Invalid Latitude Rejection

| Field | Value |
|-------|-------|
| **Purpose** | Reject impossible coordinates |
| **Input** | lat_tx = 95.0 (impossible) |
| **Expected Result** | ValueError raised |
| **Pass Criteria** | Oracle validates coordinate bounds |
| **Failure Mode** | Garbage coordinates produce garbage predictions |
| **Notes** | Latitude must be [-90, 90] |

### TST-304: Invalid Kp Rejection

| Field | Value |
|-------|-------|
| **Purpose** | Reject out-of-range geomagnetic index |
| **Input** | kp = 15 (impossible, max is 9) |
| **Expected Result** | ValueError raised |
| **Pass Criteria** | Oracle validates Kp bounds |
| **Failure Mode** | Extrapolation beyond training domain |
| **Notes** | Kp index is defined as 0-9 |

### TST-305: Valid Long Distance Path

| Field | Value |
|-------|-------|
| **Purpose** | Accept valid long-distance path |
| **Input** | ~12,000 km path (W3 → Asia) |
| **Expected Result** | Prediction returned (no error) |
| **Pass Criteria** | Oracle accepts valid input |
| **Failure Mode** | False rejection of valid path |
| **Notes** | Ensures validation isn't overly aggressive |

---

## Group 4: Hallucination Traps (TST-400)

These tests catch cases where the model might produce confident but wrong answers.

### TST-401: EME Path Detection

| Field | Value |
|-------|-------|
| **Purpose** | Catch EME-like inputs that look ionospheric |
| **Scenario** | 2m, 500 km, -28 dB expected (classic EME signature) |
| **Expected Result** | Rejected as VHF |
| **Pass Criteria** | Oracle recognizes this isn't ionospheric |
| **Failure Mode** | Model predicts confidently for physics it never learned |
| **Notes** | 1500W, 500km, -28 dB on 2m = Moon bounce, not skip |

### TST-402: Sporadic E Trap (Future)

| Field | Value |
|-------|-------|
| **Purpose** | Identify E-skip conditions model wasn't trained on |
| **Scenario** | 6m, 1500 km, summer afternoon |
| **Expected Result** | Warning about sporadic E uncertainty |
| **Pass Criteria** | Oracle flags low confidence |
| **Status** | NOT IMPLEMENTED — 6m not in training data |
| **Notes** | Sporadic E is unpredictable; model should admit uncertainty |

### TST-403: Ground Wave Confusion

| Field | Value |
|-------|-------|
| **Purpose** | Flag very short paths that may be ground wave |
| **Scenario** | 80m, 50 km path |
| **Expected Result** | Warning issued (likely ground wave) |
| **Pass Criteria** | Oracle warns about ground wave possibility |
| **Failure Mode** | Model predicts ionospheric SNR for ground wave path |
| **Notes** | WSPR < 100 km is often ground wave, not skywave |

### TST-404: Extreme Solar Event

| Field | Value |
|-------|-------|
| **Purpose** | Flag predictions during X-class flare conditions |
| **Scenario** | SFI 400+, Kp 9 |
| **Expected Result** | Warning about extreme conditions |
| **Pass Criteria** | Oracle flags low confidence |
| **Status** | PARTIALLY IMPLEMENTED (SFI warning at >350) |
| **Notes** | Extreme space weather is outside training distribution |

---

## Test Execution

### Running the Implemented Tests

```bash
cd /Users/gbeam/workspace/ionis-ai/ionis-training

# 1. Physics Verification (4 tests)
.venv/bin/python versions/v20/verify_v20.py

# 2. Sensitivity Analysis (8 sweeps)
.venv/bin/python versions/v20/test_v20.py

# 3. PSK Reporter Live Validation
.venv/bin/python versions/v20/validate_v20_pskr.py
```

### Expected Output: verify_v20.py

```
Loading versions/v20/ionis_v20.pth...
  Parameters: 203,573
  RMSE: 0.8620 sigma (5.78 dB equiv)
  Pearson: +0.4777

============================================================
TEST 1: STORM SIDECAR (Kp)
============================================================
  Storm Cost (Kp 0->9): +3.487 sigma (+23.4 dB)
  PASS: Signal DROPPED during storm (correct physics)

============================================================
TEST 2: SUN SIDECAR (SFI)
============================================================
  Sun Benefit (SFI 70->200): +0.482 sigma (+3.2 dB)
  PASS: Signal IMPROVED with higher SFI (correct physics)

============================================================
TEST 3: GATE RANGE [0.5, 2.0]
============================================================
  PASS: All gate values within [0.5, 2.0]

============================================================
TEST 4: DECOMPOSITION MATH
============================================================
  PASS: base + sun_gate*sun_raw + storm_gate*storm_raw = predicted

============================================================
V20 PHYSICS VERIFICATION SUMMARY
============================================================
  Storm Sidecar (Kp 0->9)       PASS
  Sun Sidecar (SFI 70->200)     PASS
  Gate range [0.5, 2.0]         PASS
  Decomposition math            PASS

ALL TESTS PASSED -- Physics constraints enforced
```

### Interpreting Failures

| Failure Pattern | Likely Cause |
|-----------------|--------------|
| SFI monotonicity fails | Sun sidecar broken or inverted |
| Kp monotonicity fails | Storm sidecar broken or inverted (CRITICAL) |
| All paths show same SNR | Trunk collapsed to constant |
| VHF not rejected | Input validation bypassed |
| Polar = Equatorial storm cost | Gates not differentiating |

---

## Group 5: Model Robustness (TST-500)

Standard ML model tests — not physics-specific, applies to any neural network.

### TST-501: Reproducibility

| Field | Value |
|-------|-------|
| **Purpose** | Same input produces same output |
| **Method** | Run identical prediction 100 times |
| **Expected Result** | All outputs identical (deterministic inference) |
| **Pass Criteria** | Zero variance in predictions |
| **Failure Mode** | Non-deterministic behavior indicates dropout left on or random state leak |
| **Category** | Determinism |

### TST-502: Input Perturbation Stability

| Field | Value |
|-------|-------|
| **Purpose** | Small input changes produce small output changes |
| **Method** | Perturb inputs by ±0.1%, measure output variance |
| **Expected Result** | Output changes < 0.5 dB for tiny input changes |
| **Pass Criteria** | No catastrophic sensitivity |
| **Failure Mode** | Exploding gradients, unstable regions in input space |
| **Category** | Stability |

### TST-503: Boundary Value Testing

| Field | Value |
|-------|-------|
| **Purpose** | Model handles edge cases gracefully |
| **Method** | Test at domain boundaries (SFI=50, SFI=300, Kp=0, Kp=9, etc.) |
| **Expected Result** | Reasonable predictions, no NaN/Inf |
| **Pass Criteria** | All outputs finite and within plausible range |
| **Failure Mode** | NaN, Inf, or predictions outside [-50, +30] dB |
| **Category** | Boundary |

### TST-504: Null Input Handling

| Field | Value |
|-------|-------|
| **Purpose** | Model rejects or handles missing/null values |
| **Method** | Pass NaN, None, or empty values |
| **Expected Result** | ValueError raised or graceful default |
| **Pass Criteria** | No silent corruption |
| **Failure Mode** | NaN propagates through model silently |
| **Category** | Input Sanitization |

### TST-505: Numerical Overflow

| Field | Value |
|-------|-------|
| **Purpose** | Model handles extreme (but valid) inputs |
| **Method** | Test with SFI=300, Kp=9, distance=19999 km simultaneously |
| **Expected Result** | Finite output, no overflow |
| **Pass Criteria** | Output in valid range |
| **Failure Mode** | Inf, -Inf, or NaN in computation |
| **Category** | Numerical Stability |

### TST-506: Checkpoint Integrity

| Field | Value |
|-------|-------|
| **Purpose** | Saved model loads correctly and matches training |
| **Method** | Load checkpoint, verify architecture, run reference prediction |
| **Expected Result** | Matches documented RMSE/Pearson within tolerance |
| **Pass Criteria** | Reference prediction within 0.01 dB of expected |
| **Failure Mode** | Corrupted checkpoint, architecture mismatch |
| **Category** | Serialization |

### TST-507: Device Portability

| Field | Value |
|-------|-------|
| **Purpose** | Model runs on CPU, MPS, and CUDA |
| **Method** | Load and run on each available device |
| **Expected Result** | Identical predictions across devices |
| **Pass Criteria** | Cross-device variance < 0.001 dB |
| **Failure Mode** | Device-specific numerical differences |
| **Category** | Portability |

---

## Group 6: Adversarial & Security (TST-600)

Tests for robustness against malicious or malformed inputs.

### TST-601: Injection via String Coordinates

| Field | Value |
|-------|-------|
| **Purpose** | Reject non-numeric coordinate inputs |
| **Method** | Pass "51.5; DROP TABLE" as latitude |
| **Expected Result** | TypeError or ValueError |
| **Pass Criteria** | No code execution, clean rejection |
| **Failure Mode** | Injection vulnerability (unlikely in numeric model but test anyway) |
| **Category** | Input Injection |

### TST-602: Extremely Large Values

| Field | Value |
|-------|-------|
| **Purpose** | Reject absurdly large inputs |
| **Method** | Pass SFI=1e30, distance=1e20 |
| **Expected Result** | ValueError (out of bounds) |
| **Pass Criteria** | Rejected before reaching model |
| **Failure Mode** | Float overflow in computation |
| **Category** | Bounds Checking |

### TST-603: Negative Physical Values

| Field | Value |
|-------|-------|
| **Purpose** | Reject physically impossible negative values |
| **Method** | Pass SFI=-100, Kp=-5, freq=-14.0 |
| **Expected Result** | ValueError |
| **Pass Criteria** | All rejected |
| **Failure Mode** | Negative values accepted, nonsense predictions |
| **Category** | Physical Validity |

### TST-604: Type Coercion Attack

| Field | Value |
|-------|-------|
| **Purpose** | Handle unexpected types gracefully |
| **Method** | Pass list, dict, or object instead of float |
| **Expected Result** | TypeError |
| **Pass Criteria** | Clean error message |
| **Failure Mode** | Silent type coercion producing wrong results |
| **Category** | Type Safety |

---

## Group 7: Bias & Fairness (TST-700)

Tests for systematic biases in model predictions.

### TST-701: Geographic Coverage Bias

| Field | Value |
|-------|-------|
| **Purpose** | Verify model doesn't favor training-dense regions |
| **Method** | Compare similar-distance paths in data-rich (EU) vs data-sparse (Africa) regions |
| **EU Path** | G → DL (London to Berlin), ~900 km |
| **Africa Path** | 5H → 9J (Tanzania to Zambia), ~1,200 km |
| **Conditions** | 14 MHz, SFI 150, Kp 2, 14:00 UTC |
| **Expected Result** | Bias < 5 dB between regions |
| **Pass Criteria** | Similar predictions for similar physics |
| **Failure Mode** | >5 dB difference suggests model memorized dense regions |
| **Actual** | EU: -15.2 dB, Africa: -15.2 dB, Bias: 0.0 dB |
| **Category** | Geographic Bias |
| **Status** | AUTOMATED |

### TST-702: Temporal Bias

| Field | Value |
|-------|-------|
| **Purpose** | Verify model doesn't favor specific times |
| **Method** | Sweep all 24 hours, verify no anomalous spikes |
| **Expected Result** | Smooth diurnal variation |
| **Pass Criteria** | No discontinuities at hour boundaries |
| **Failure Mode** | Training data imbalance causing time-of-day artifacts |
| **Category** | Temporal Bias |

### TST-703: Band Coverage Bias

| Field | Value |
|-------|-------|
| **Purpose** | Verify all bands receive reasonable predictions |
| **Method** | Run same path on all bands 160m-10m |
| **Expected Result** | All predictions in valid range, physics-consistent |
| **Pass Criteria** | No band returns NaN or wildly different behavior |
| **Failure Mode** | Underrepresented bands produce poor predictions |
| **Category** | Feature Bias |

---

## Group 8: Regression Tests (TST-800)

Baseline tests to catch future regressions.

### TST-801: Reference Prediction

| Field | Value |
|-------|-------|
| **Purpose** | Catch silent model changes |
| **Method** | Fixed input, compare to documented output |
| **Reference Input** | W3→G, 20m, SFI 150, Kp 2, 14:00 UTC |
| **Reference Output** | -20.0 dB (±0.5 dB tolerance) |
| **Pass Criteria** | Within tolerance of documented value |
| **Failure Mode** | Model weights changed, retraining without version bump |
| **Category** | Regression |

### TST-802: RMSE Regression

| Field | Value |
|-------|-------|
| **Purpose** | Ensure model accuracy hasn't degraded |
| **Method** | Check checkpoint metadata |
| **Reference Value** | RMSE = 0.862σ |
| **Pass Criteria** | Loaded RMSE matches documented |
| **Failure Mode** | Wrong checkpoint loaded |
| **Category** | Regression |

### TST-803: Pearson Regression

| Field | Value |
|-------|-------|
| **Purpose** | Ensure correlation hasn't degraded |
| **Method** | Check checkpoint metadata |
| **Reference Value** | Pearson = +0.4879 |
| **Pass Criteria** | Loaded Pearson matches documented |
| **Failure Mode** | Wrong checkpoint loaded |
| **Category** | Regression |

---

## Standard ML Test Categories Reference

| Category | Purpose | Examples |
|----------|---------|----------|
| **Determinism** | Same input → same output | TST-501 |
| **Stability** | Small input changes → small output changes | TST-502 |
| **Boundary** | Edge cases handled | TST-503 |
| **Input Sanitization** | Invalid inputs rejected | TST-504, TST-601-604 |
| **Numerical Stability** | No overflow/underflow | TST-505 |
| **Serialization** | Save/load integrity | TST-506 |
| **Portability** | Cross-device consistency | TST-507 |
| **Bias/Fairness** | No systematic favoritism | TST-701-703 |
| **Regression** | Catch silent degradation | TST-801-803 |
| **Adversarial** | Malicious input handling | TST-601-604 |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-05 | Initial specification |
| 1.1 | 2026-02-05 | Added TST-500 (Robustness), TST-600 (Security), TST-700 (Bias), TST-800 (Regression) |
| 1.2 | 2026-02-05 | Added TST-206 (Grey line twilight), automated TST-701 (Geographic bias) per Gemini review |
| 2.0 | 2026-02-16 | Updated for V20 Golden Master; fixed script paths to `versions/v20/`; documented implementation status; renamed from `v12_test_specification.md` |

---

## References

- Training: `ionis-training/versions/v20/train_v20.py`
- Physics Verification: `ionis-training/versions/v20/verify_v20.py`
- Sensitivity Analysis: `ionis-training/versions/v20/test_v20.py`
- PSKR Live Validation: `ionis-training/versions/v20/validate_v20_pskr.py`
- Model Checkpoint: `ionis-training/versions/v20/ionis_v20.pth`
- Config: `ionis-training/versions/v20/config_v20.json`
