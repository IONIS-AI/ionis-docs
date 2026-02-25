# Test Suite

The IONIS validation suite runs 29 automated tests that verify the V22-gamma model
behaves correctly — operator-grounded physics gates and band x time discrimination.

## Running

```bash
ionis-validate test
```

All tests run sequentially. Each prints PASS or FAIL with details. The runner
exits with code 0 if all pass, non-zero otherwise.

## Test Groups

### KI7MT Operator Tests (18 tests)

Eighteen operator-grounded test paths derived from 49,000 QSOs and 5.7 million
contest signatures. Each path has a physically-motivated expectation based on
real operating experience from KI7MT (DN13, Idaho).

The tests are organized into 4 gates:

| Gate | Tests | Purpose |
|------|-------|---------|
| Raw model | 17 hard pass | V22-gamma predictions without override |
| PhysicsOverrideLayer | 17 hard pass + acid test | Override clamps high-band night |
| Regression | 17 | No paths that passed raw should fail with override |
| Acid test | 1 | 10m EU at night must be negative (override fires) |

Examples:

- 20m FN31 to JO21 at 14 UTC in June (US East Coast to England, daytime)
- 160m DN13 to EM73 at 03 UTC (domestic NVIS, nighttime)
- 10m DN13 to JN48 at 03 UTC (acid test — both endpoints dark, override fires)

### TST-900: Band x Time Discrimination (11 tests)

Eleven band x time combinations testing whether the model correctly
discriminates propagation across HF bands and time periods:

| Test | Band | Time | Expected |
|------|------|------|----------|
| TST-901 | 20m | Day | Positive SNR |
| TST-902 | 40m | Night | Positive SNR |
| TST-903 | 10m | Day, low SFI | Marginal (known fail) |
| TST-904 | 15m | Twilight | Marginal (known fail) |
| TST-905–911 | Various | Various | Band-appropriate response |

**Expected score: 9/11.** TST-903 and TST-904 are known limitations —
the model predicts these marginal conditions slightly outside the expected
range. These are tracked for future model versions.

## Interpreting Results

A passing run looks like:

```
============================================================
  IONIS V22-gamma — Validation Suite
============================================================

  KI7MT Operator Tests
  ────────────────────
  Gate 1: Raw Model ................ 16/17 hard pass
  Gate 2: Override ................. 17/17 hard pass
  Gate 3: Regression ............... 0 regressions
  Gate 4: Acid Test ................ PASS (override fired)
  KI7MT Result: 18/18 PASS

  TST-900 Band x Time
  ────────────────────
  TST-901 .... PASS
  TST-902 .... PASS
  ...
  TST-900 Result: 9/11

  Summary: KI7MT 18/18 PASS | TST-900 9/11
```

If a test fails, the output includes:

- The test ID and description
- Expected vs actual values
- Suggested diagnostic steps

Report failures via [Reporting Issues](reporting.md).

## V20 Legacy Test Suite

The V20 test specification (TST-100 through TST-800, 62 tests) is documented
in the [Test Specification](../model/validation/test_specification.md) for
historical reference. V22-gamma replaces this battery with the focused
operator-grounded validation above.
