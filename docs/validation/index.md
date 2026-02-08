# Validation Reports

Automated test results from IONIS model evaluations.

## Current Status: V12 Complete

!!! success "35/35 Tests Passing"
    IONIS V12 Signatures has a comprehensive automated test suite.

    **Physics Score**: 74.2/100 (Grade C — Needs Improvement)

Run the test suite:
```bash
python scripts/oracle_v12.py --test
```

## Test Categories

| Group | ID Range | Tests | Purpose |
|-------|----------|-------|---------|
| Canonical Paths | TST-100 | 10 | Known HF paths |
| Physics Constraints | TST-200 | 6 | Monotonicity, sidecars |
| Input Validation | TST-300 | 9 | Boundary checks |
| Robustness | TST-500 | 9 | Determinism, stability |
| Regression | TST-800 | 1 | Catch silent degradation |

## Physics Grades (V12)

| Test | Description | Result | Grade |
|------|-------------|--------|-------|
| TST-201 | SFI 70→200 | +1.7 dB | C |
| TST-202 | Kp 0→9 storm cost | +4.2 dB | **A** |
| TST-203 | D-layer absorption | +0.0 dB | C |
| TST-204 | Polar storm | +2.7 dB | B |
| TST-205 | 10m SFI sensitivity | +1.6 dB | C |
| TST-206 | Grey line twilight | +0.3 dB | C |

Grade C items are V13 improvement targets.

## Documentation

- [V12 Test Specification](v12_test_specification.md) — NASA-style test documentation
