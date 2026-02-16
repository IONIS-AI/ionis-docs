# Test Suite

The IONIS validation suite runs 62 automated tests that verify the V20 model
behaves correctly — physics, predictions, edge cases, and regression baselines.

## Running

```bash
ionis-validate test
```

All tests run sequentially. Each prints PASS or FAIL with details. The runner
exits with code 0 if all pass, non-zero otherwise.

## Test Groups

### TST-100: Canonical Paths (30 tests)

Thirty known HF paths spanning all bands, distances, and geographic regions.
Each path has an expected SNR range based on operational experience. Tests
verify that model predictions fall within those bounds.

Examples:

- FN31 to JO21 on 20m at 14 UTC in June (US East Coast to England)
- DN26 to PM95 on 20m at 06 UTC in December (US West Coast to Japan)
- PJ2 to ZL on 15m during high SFI (Caribbean to New Zealand)

These are the "does the model match reality?" tests.

### TST-200: Physics Constraints (6 tests)

Verifies the model respects ionospheric physics:

- **SFI monotonicity**: Higher solar flux always improves SNR
- **Kp monotonicity**: Higher geomagnetic activity always degrades SNR
- **Polar degradation**: Polar paths are more sensitive to storms than equatorial
- **Storm/sun sidecar range**: Gate values stay within [0.5, 2.0]

If any of these fail, the model has learned unphysical behavior.

### TST-300: Input Validation (5 tests)

Boundary condition checks:

- Extreme latitudes (poles)
- Maximum distance (antipodal paths)
- Minimum distance (short skip)
- Edge frequencies (160m, 10m)
- Solar extremes (SFI 65, SFI 300)

### TST-400: Hallucination Traps (4 tests)

Feeds the model inputs that should produce bounded or known outputs:

- Night-side 10m path (should predict poor propagation)
- Geomagnetically impossible paths
- Out-of-training-range solar indices
- Paths with no historical observations

### TST-500: Robustness (7 tests)

- **Determinism**: Same input produces same output across runs
- **Device portability**: Results match across CPU, CUDA, and MPS
- **Batch consistency**: Single-sample and batched inference agree
- **Numerical stability**: No NaN, Inf, or overflow on edge inputs

### TST-600: Adversarial (4 tests)

Malicious or malformed inputs:

- NaN injection
- Extreme values (1e10, -1e10)
- Type confusion
- Buffer boundary inputs

### TST-700: Bias and Fairness (3 tests)

- **Geographic balance**: Model doesn't systematically favor one hemisphere
- **Temporal balance**: Day/night predictions are physically reasonable
- **Band balance**: No band shows anomalous recall collapse

### TST-800: Regression (3 tests)

Baseline checks against locked reference values:

- Checkpoint file integrity (hash verification)
- Known-input known-output regression vectors
- Metric bounds (Pearson, RMSE within expected range)

## Interpreting Results

A passing run looks like:

```
Running 62 tests across 8 groups...
TST-100: 30/30 PASS
TST-200:  6/6  PASS
TST-300:  5/5  PASS
TST-400:  4/4  PASS
TST-500:  7/7  PASS
TST-600:  4/4  PASS
TST-700:  3/3  PASS
TST-800:  3/3  PASS

62/62 PASS
```

If a test fails, the output includes:

- The test ID and description
- Expected vs actual values
- Suggested diagnostic steps

Report failures via [Reporting Issues](reporting.md).
