# Custom Path Tests

Define your own test paths in a JSON file and batch-validate them against the
V22-gamma model. This is the best way to check whether IONIS matches your on-air
experience.

## Usage

```bash
ionis-validate custom my_paths.json
```

## JSON Format

```json
{
  "description": "My 20m paths from KI7MT",
  "conditions": {
    "sfi": 140,
    "kp": 1.5
  },
  "paths": [
    {
      "tx_grid": "DN26",
      "rx_grid": "IO91",
      "band": "20m",
      "hour": 14,
      "month": 6,
      "label": "KI7MT to G"
    },
    {
      "tx_grid": "DN26",
      "rx_grid": "PM95",
      "band": "20m",
      "hour": 6,
      "month": 12,
      "expect_open": true,
      "mode": "CW",
      "label": "KI7MT to JA — CW should decode"
    },
    {
      "tx_grid": "DN26",
      "rx_grid": "GG66",
      "band": "15m",
      "hour": 16,
      "month": 3,
      "sfi": 200,
      "label": "KI7MT to VK (high SFI override)"
    }
  ]
}
```

### Fields

**Top-level `conditions`** (optional) — default solar conditions applied to
all paths unless overridden per-path:

| Field | Default | Description |
|-------|---------|-------------|
| `sfi` | 150 | Solar Flux Index |
| `kp` | 2.0 | Kp geomagnetic index |

**Per-path fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `tx_grid` | Yes | Transmitter 4-char Maidenhead grid |
| `rx_grid` | Yes | Receiver 4-char Maidenhead grid |
| `band` | Yes | Band label (20m, 15m, etc.) |
| `hour` | Yes | UTC hour (0-23) |
| `month` | Yes | Month (1-12) |
| `label` | No | Human-readable path description (not shown in table) |
| `sfi` | No | Per-path SFI override |
| `kp` | No | Per-path Kp override |
| `expect_open` | No | Boolean — assert the path should be open (true) or closed (false) |
| `mode` | No | Mode to test against: WSPR, FT8, CW, RTTY, or SSB (default: WSPR) |

### Expectations and Mode Testing

Add `"expect_open": true` or `"expect_open": false` to assert model behavior.
The optional `"mode"` field controls which decode threshold is used for the
PASS/FAIL verdict:

```json
{
  "tx_grid": "DN26",
  "rx_grid": "IO91",
  "band": "20m",
  "hour": 14,
  "month": 6,
  "expect_open": true,
  "mode": "CW"
}
```

This path passes if the predicted dB is at or above the CW threshold (-15 dB).
Without a `"mode"` field, expectations test against the WSPR threshold (-28 dB).

| Mode | Threshold | Meaning |
|------|-----------|---------|
| WSPR | -28 dB | Beacon decode floor |
| FT8 | -21 dB | Digital decode limit |
| CW | -15 dB | Readable by experienced operator |
| RTTY | -5 dB | Machine-copy reliable |
| SSB | +3 dB | Voice-quality communication |

If the model disagrees with your expectation, the test reports FAIL and exits
with a non-zero return code. This is the feedback mechanism — paths where the
model and your experience diverge are exactly what we need to know about.

## Example Output

```
======================================================================
  IONIS V22-gamma — Custom Path Tests
======================================================================

  Stress test — 20 paths across good, marginal, bad, and storm conditions
  Device: cuda

      #  Path           Band      dB       km  SFI   Kp  Hour  Mon  WSPR   FT8    CW   SSB  Result
  ────────────────────────────────────────────────────────────────────────────────────────────────
      1  DN26 > IO91    20m    -18.8    7,432  160    1    14    6  OPEN  OPEN    --    --    PASS
      2  FN31 > JO31    20m     -1.7    5,912  140    2    18    3  OPEN  OPEN  OPEN    --    PASS
      3  PM95 > QF56    40m     -5.0    7,773  120    1    10   10  OPEN  OPEN  OPEN    --    PASS
      4  DN26 > IO91    10m    -22.5    7,432   70    2    14    6  OPEN    --    --    --    FAIL
      5  DN26 > IO91    20m    -29.0    7,432  160    9    14    6    --    --    --    --    PASS
  ────────────────────────────────────────────────────────────────────────────────────────────────

  Expectations: 4/5 passed (mode: WSPR)
  1 path(s) did not match expected open/closed state
```

**Reading the table:**

- **Path**: TX and RX grids
- **dB**: Predicted SNR in decibels — the primary output
- **SFI, Kp, Hour, Mon**: The resolved conditions for each path (per-path override or default)
- **WSPR, FT8, CW, SSB**: Inline mode verdicts — `OPEN` if the predicted dB meets that mode's decode threshold, `--` if not
- **Result**: `PASS`/`FAIL` for paths with expectations, `OPEN`/`closed` for paths without

## Tips for Writing Good Tests

1. **Test paths you actually work.** The value is in comparing model predictions
   to your real experience — not hypothetical paths.

2. **Vary conditions.** Test the same path at different hours, months, and SFI
   values. If 20m to Europe opens at 14 UTC for you, does the model agree?

3. **Include known failures.** If you know 160m from your grid to VK never
   works, add it with `"expect_open": false`. Confirming negatives is as
   valuable as confirming positives.

4. **Use the `mode` field for SSB/CW tests.** If you work SSB to Europe and
   the model says the path is open for WSPR but not SSB, set
   `"mode": "SSB", "expect_open": true` to flag the disagreement.

5. **Use real solar conditions.** Check current SFI at
   [NOAA SWPC](https://www.swpc.noaa.gov/) and test with today's actual value
   instead of the default 150.

6. **Share your results.** Custom path test files that expose model weaknesses
   are the most valuable feedback you can provide. See
   [Reporting Issues](reporting.md).
