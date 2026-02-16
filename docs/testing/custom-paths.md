# Custom Path Tests

Define your own test paths in a JSON file and batch-validate them against the
V20 model. This is the best way to check whether IONIS matches your on-air
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
      "label": "KI7MT to JA"
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
| `label` | No | Human-readable path description |
| `sfi` | No | Per-path SFI override |
| `kp` | No | Per-path Kp override |
| `expect_open` | No | Boolean — assert the band should be open (true) or closed (false) |

### Expectations

Add `"expect_open": true` or `"expect_open": false` to assert model behavior:

```json
{
  "tx_grid": "DN26",
  "rx_grid": "IO91",
  "band": "20m",
  "hour": 14,
  "month": 6,
  "expect_open": true,
  "label": "KI7MT to G — should be open"
}
```

If the model disagrees with your expectation, the test reports FAIL and exits
with a non-zero return code. This is the feedback mechanism — paths where the
model and your experience diverge are exactly what we need to know about.

## Example Output

```
Custom Path Test: My 20m paths from KI7MT
==========================================
  Conditions: SFI=140, Kp=1.5

  Path                          Band   SNR (dB)   CW    FT8   SSB   Result
  KI7MT to G                    20m     -6.8      OPEN  OPEN  ---   PASS
  KI7MT to JA                   20m    -18.2      ---   OPEN  ---   PASS
  KI7MT to VK (high SFI)        15m     -4.1      OPEN  OPEN  ---   PASS

  3/3 paths tested, 3 PASS, 0 FAIL
```

## Tips for Writing Good Tests

1. **Test paths you actually work.** The value is in comparing model predictions
   to your real experience — not hypothetical paths.

2. **Vary conditions.** Test the same path at different hours, months, and SFI
   values. If 20m to Europe opens at 14 UTC for you, does the model agree?

3. **Include known failures.** If you know 160m from your grid to VK never
   works, add it with `"expect_open": false`. Confirming negatives is as
   valuable as confirming positives.

4. **Use real solar conditions.** Check current SFI at
   [NOAA SWPC](https://www.swpc.noaa.gov/) and test with today's actual value
   instead of the default 150.

5. **Share your results.** Custom path test files that expose model weaknesses
   are the most valuable feedback you can provide. See
   [Reporting Issues](reporting.md).
