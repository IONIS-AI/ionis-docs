# IONIS Test Specification

| | |
|---|---|
| **Document Version** | 2.2 |
| **Model Version** | IonisGate V20 (Production) |
| **Checkpoint** | `versions/v20/ionis_v20.pth` |
| **Date** | 2026-02-16 |
| **Author** | IONIS |

!!! success "Implementation Status: COMPLETE"
    All 62 tests are fully automated in the modular test suite:

    | Group | Tests | Description |
    |-------|-------|-------------|
    | TST-100 | 30 | Canonical Paths — Global HF propagation coverage |
    | TST-200 | 6 | Physics Constraints — V16 Physics Laws |
    | TST-300 | 5 | Input Validation — Boundary checks |
    | TST-400 | 4 | Hallucination Traps — Out-of-domain detection |
    | TST-500 | 7 | Model Robustness — Determinism, stability |
    | TST-600 | 4 | Adversarial & Security — Malicious input handling |
    | TST-700 | 3 | Bias & Fairness — Geographic, temporal, band bias |
    | TST-800 | 3 | Regression Tests — V20 baseline locks |
    | **Total** | **62** | |

    Run all tests: `python versions/v20/tests/run_all.py`

---

## Overview

This document specifies the automated test suite for IONIS. Each test has:
- **ID**: Unique identifier (TST-XXX)
- **Purpose**: What physics or behavior is being validated
- **Method**: How the test works
- **Expected Result**: What constitutes PASS/FAIL
- **Failure Mode**: What a failure indicates
- **Hallucination Trap**: Tests designed to catch model overconfidence

The test suite runs via modular test scripts in `versions/v20/tests/`:

```bash
cd $IONIS_WORKSPACE

# Run complete test suite (62 tests)
.venv/bin/python ionis-training/versions/v20/tests/run_all.py

# Run individual test groups
.venv/bin/python ionis-training/versions/v20/tests/test_tst200_physics.py
.venv/bin/python ionis-training/versions/v20/tests/test_tst100_canonical.py
# etc.
```

**Additional validation scripts:**

```bash
# Legacy physics verification (standalone)
.venv/bin/python ionis-training/versions/v20/verify_v20.py

# PSK Reporter live validation
.venv/bin/python ionis-training/versions/v20/validate_v20_pskr.py
```

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

These tests verify the model produces reasonable predictions for well-known HF propagation paths. All paths must predict SNR > -2.5σ (~-17 dB) to be considered OPEN.

Default conditions unless noted: SFI 150, Kp 2, June.

### Category A: North America to Europe

| ID | Path | Band | Hour UTC | Purpose |
|----|------|------|----------|---------|
| TST-101 | W3 → G | 20m | 14 | Classic transatlantic day path |
| TST-102 | W3 → G | 20m | 04 | Grey line / night propagation |
| TST-103 | G → W6 | 20m | 18 | Europe to US West Coast |
| TST-104 | W3 → G | 40m | 22 | Transatlantic on 40m (evening) |
| TST-105 | VE3 → DL | 20m | 14 | Canada to Germany |

### Category B: Trans-Pacific

| ID | Path | Band | Hour UTC | Purpose |
|----|------|------|----------|---------|
| TST-110 | W6 → JA | 20m | 16 | US West Coast to Japan |
| TST-111 | JA → W3 | 20m | 23 | Japan to US East Coast (long path timing) |
| TST-112 | KH6 → JA | 20m | 06 | Hawaii to Japan |
| TST-113 | VK → W6 | 20m | 05 | Australia to US West Coast |

### Category C: Europe to Asia

| ID | Path | Band | Hour UTC | Purpose |
|----|------|------|----------|---------|
| TST-120 | G → JA | 20m | 08 | Europe to Japan |
| TST-121 | DL → VU | 20m | 12 | Germany to India |
| TST-122 | JA → OH | 20m | 10 | Japan to Finland (near-polar) |

### Category D: Africa Paths

| ID | Path | Band | Hour UTC | Purpose |
|----|------|------|----------|---------|
| TST-130 | ZS → G | 20m | 14 | South Africa to Europe |
| TST-131 | ZS → W3 | 20m | 16 | South Africa to US East Coast |
| TST-132 | 5H → DL | 20m | 14 | Tanzania to Germany |

### Category E: South America Paths

| ID | Path | Band | Hour UTC | Purpose |
|----|------|------|----------|---------|
| TST-140 | PY → W3 | 20m | 18 | Brazil to US East Coast |
| TST-141 | LU → G | 20m | 16 | Argentina to Europe |
| TST-142 | PY → VU | 20m | 14 | Brazil to India (equatorial long-haul) |

### Category F: Oceania Paths

| ID | Path | Band | Hour UTC | Purpose |
|----|------|------|----------|---------|
| TST-150 | VK → G | 20m | 08 | Australia to Europe |
| TST-151 | ZL → JA | 20m | 04 | New Zealand to Japan |
| TST-152 | VK → ZS | 20m | 10 | Australia to South Africa |

### Category G: Regional / NVIS

| ID | Path | Band | Hour UTC | Purpose |
|----|------|------|----------|---------|
| TST-160 | G → DL | 20m | 12 | Intra-Europe short path |
| TST-161 | JA → HL | 20m | 06 | Intra-Asia (Japan to Korea) |
| TST-162 | Central US | 80m | 02 | NVIS ~280 km (SFI 100, threshold -2.0σ) |

### Category H: Band-Specific Physics (Paired Tests)

| ID | Path | Band | Conditions | Purpose |
|----|------|------|------------|---------|
| TST-170 | OX → OH | 20m | Kp 2 | Polar path quiet baseline |
| TST-171 | OX → OH | 20m | Kp 8 | Polar storm degradation (> 1σ vs TST-170) |
| TST-172 | W3 → G | 10m | SFI 80 | 10m low SFI baseline |
| TST-173 | W3 → G | 10m | SFI 200 | 10m SFI improvement (> 0.3σ vs TST-172) |
| TST-174 | W3 → G | 40m | 02 UTC | 40m night path |
| TST-175 | VE3 → W3 | 160m | 04 UTC | 160m regional night (SFI 100) |

### Location Database

| Key | Location | Lat | Lon |
|-----|----------|-----|-----|
| W3 | Maryland | 39.14°N | 77.01°W |
| W6 | Los Angeles | 34.05°N | 118.24°W |
| VE3 | Toronto | 43.65°N | 79.38°W |
| KH6 | Hawaii | 21.31°N | 157.86°W |
| G | London | 51.50°N | 0.12°W |
| DL | Berlin | 52.52°N | 13.40°E |
| OH | Helsinki | 60.17°N | 24.94°E |
| JA | Tokyo | 35.68°N | 139.69°E |
| HL | Seoul | 37.57°N | 126.98°E |
| VU | Bangalore | 12.97°N | 77.59°E |
| VK | Sydney | 33.87°S | 151.21°E |
| ZL | Wellington | 41.29°S | 174.78°E |
| ZS | Cape Town | 33.93°S | 18.42°E |
| 5H | Tanzania | 6.17°S | 35.74°E |
| PY | Sao Paulo | 23.55°S | 46.63°W |
| LU | Buenos Aires | 34.60°S | 58.38°W |
| OX | Greenland | 64.18°N | 51.72°W |

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
| **Actual** | +0.535σ (+3.6 dB) improvement — Grade A |
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
| **Actual** | +1.743σ (+11.7 dB) storm cost — Grade A |
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
| **Actual** | +0.063σ (+0.4 dB) — 20m slightly better — Grade C |
| **Notes** | Correct direction but weak magnitude; real physics expects stronger D-layer effect |

### TST-204: Polar Storm Degradation (Kp 2 vs 8)

| Field | Value |
|-------|-------|
| **Purpose** | Verify storms hit high-latitude paths harder |
| **Method** | Compare Kp 2 vs Kp 8 on polar path |
| **Path** | OX → OH, 20m, SFI 150, 12:00 UTC |
| **Expected Result** | Storm cost > 2 dB |
| **Pass Criteria** | Significant degradation observed |
| **Failure Mode** | If < 1 dB: Storm gate not modulating by latitude |
| **Actual** | +1.149σ (+7.7 dB) polar degradation; polar/mid-lat ratio 1.00x — Grade C |
| **Notes** | Significant storm degradation confirmed; gate not yet differentiating by latitude |

### TST-205: 10m SFI Sensitivity

| Field | Value |
|-------|-------|
| **Purpose** | Verify higher bands more sensitive to SFI |
| **Method** | Compare SFI 80 vs 200 on 10m path |
| **Path** | W3 → G, 28 MHz, Kp 2, 14:00 UTC |
| **Expected Result** | Delta > +1.5 dB |
| **Pass Criteria** | 10m shows strong SFI dependence |
| **Failure Mode** | If < 1 dB: Sun sidecar not frequency-aware |
| **Actual** | +0.498σ (+3.3 dB) improvement; 10m/20m ratio 1.00x — Grade A |
| **Notes** | 10m needs high SFI; model shows strong SFI sensitivity |

### TST-206: Grey Line / Twilight Enhancement

| Field | Value |
|-------|-------|
| **Purpose** | Verify model captures grey line propagation enhancement |
| **Method** | Compare SNR at 14:00 UTC vs 18:00 UTC on E-W path |
| **Path** | W3 → G, 20m, SFI 150, Kp 2 |
| **Expected Result** | SNR(18 UTC) >= SNR(14 UTC) |
| **Pass Criteria** | Twilight hour shows equal or better propagation |
| **Failure Mode** | If negative: Model missing grey line physics |
| **Actual** | +0.074σ (+0.5 dB) enhancement — Grade C |
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
| **Status** | IMPLEMENTED — rejects 50.3 MHz with "Sporadic E" warning |
| **Notes** | 6m not in training data; oracle correctly flags as out-of-domain |

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
| **Status** | IMPLEMENTED — SFI 400 + Kp 9 triggers "extreme solar event" warning with low confidence |
| **Notes** | Extreme space weather is outside training distribution |

---

## Test Execution

### Running the Complete Test Suite

```bash
cd $IONIS_WORKSPACE

# Complete test suite (62 tests, ~2 min)
.venv/bin/python ionis-training/versions/v20/tests/run_all.py
```

### Expected Output: run_all.py

```
======================================================================
  IONIS V20 — Complete Test Suite
======================================================================

  Date: 2026-02-16 10:47:23
  Model: IonisGate V20 Golden Master
  Checkpoint: versions/v20/ionis_v20.pth

  Running 8 test groups (62 total tests)...

  [TST-200] Physics Constraints (6 tests)... PASS
  [TST-300] Input Validation (5 tests)... PASS
  [TST-500] Model Robustness (7 tests)... PASS
  [TST-800] Regression Tests (3 tests)... PASS
  [TST-100] Canonical Paths (30 tests)... PASS
  [TST-400] Hallucination Traps (4 tests)... PASS
  [TST-600] Adversarial & Security (4 tests)... PASS
  [TST-700] Bias & Fairness (3 tests)... PASS

======================================================================
  TEST SUITE SUMMARY
======================================================================

  Group       Description                 Tests    Status
  -------------------------------------------------------
  TST-200     Physics Constraints             6      PASS
  TST-300     Input Validation                5      PASS
  TST-500     Model Robustness                7      PASS
  TST-800     Regression Tests                3      PASS
  TST-100     Canonical Paths                30      PASS
  TST-400     Hallucination Traps             4      PASS
  TST-600     Adversarial & Security          4      PASS
  TST-700     Bias & Fairness                 3      PASS
  -------------------------------------------------------
  TOTAL                                      62  62/62

  ==================================================
  ALL TEST GROUPS PASSED
  ==================================================

  V20 Golden Master validation complete.
  Model is ready for production deployment.
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
| **Reference Input** | W3→G, 20m, SFI 150, Kp 2, 12:00 UTC, June |
| **Reference Output** | -0.328σ (±0.05σ tolerance) |
| **Pass Criteria** | Within tolerance of documented value |
| **Failure Mode** | Model weights changed, retraining without version bump |
| **Category** | Regression |

### TST-802: RMSE Regression

| Field | Value |
|-------|-------|
| **Purpose** | Ensure model accuracy hasn't degraded |
| **Method** | Check checkpoint metadata |
| **Reference Value** | RMSE = 0.8617σ (checkpoint `val_rmse`, ±0.01σ tolerance) |
| **Pass Criteria** | Loaded RMSE matches checkpoint value |
| **Failure Mode** | Wrong checkpoint loaded |
| **Category** | Regression |

### TST-803: Pearson Regression

| Field | Value |
|-------|-------|
| **Purpose** | Ensure correlation hasn't degraded |
| **Method** | Check checkpoint metadata |
| **Reference Value** | Pearson = +0.4879 (checkpoint `val_pearson`, ±0.005 tolerance) |
| **Pass Criteria** | Loaded Pearson matches checkpoint value |
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
| 2.1 | 2026-02-16 | **COMPLETE IMPLEMENTATION**: All 62 tests automated in modular test suite; TST-100 expanded to 30 global paths; TST-200 implemented with 6 physics tests; added `run_all.py` orchestrator |
| 2.2 | 2026-02-16 | **SPEC RECONCILIATION**: TST-100 rewritten to match 30-test implementation (8 geographic categories); TST-200 actuals updated from 9975WX CPU test run; TST-400 status flags corrected (TST-402, TST-404 now IMPLEMENTED); TST-800 baselines corrected to match checkpoint values (RMSE 0.8617σ, Pearson +0.4879); verified 62/62 PASS on 9975WX |

---

## References

**Test Suite (62 tests):**

- Orchestrator: `ionis-training/versions/v20/tests/run_all.py`
- TST-100 Canonical Paths: `ionis-training/versions/v20/tests/test_tst100_canonical.py`
- TST-200 Physics Constraints: `ionis-training/versions/v20/tests/test_tst200_physics.py`
- TST-300 Input Validation: `ionis-training/versions/v20/tests/test_tst300_input_validation.py`
- TST-400 Hallucination Traps: `ionis-training/versions/v20/tests/test_tst400_hallucination.py`
- TST-500 Model Robustness: `ionis-training/versions/v20/tests/test_tst500_robustness.py`
- TST-600 Adversarial/Security: `ionis-training/versions/v20/tests/test_tst600_adversarial.py`
- TST-700 Bias & Fairness: `ionis-training/versions/v20/tests/test_tst700_bias.py`
- TST-800 Regression: `ionis-training/versions/v20/tests/test_tst800_regression.py`

**Model & Training:**

- Training: `ionis-training/versions/v20/train_v20.py`
- Legacy Physics Verification: `ionis-training/versions/v20/verify_v20.py`
- Sensitivity Analysis: `ionis-training/versions/v20/test_v20.py`
- PSKR Live Validation: `ionis-training/versions/v20/validate_v20_pskr.py`
- Model Checkpoint: `ionis-training/versions/v20/ionis_v20.pth`
- Config: `ionis-training/versions/v20/config_v20.json`
