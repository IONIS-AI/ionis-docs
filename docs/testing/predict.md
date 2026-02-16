# Single Path Prediction

Predict the signal-to-noise ratio for any HF path from the command line.

## Usage

```bash
ionis-validate predict \
    --tx-grid <grid> --rx-grid <grid> \
    --band <band> \
    --sfi <value> --kp <value> \
    --hour <utc_hour> --month <month>
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `--tx-grid` | Yes | Transmitter grid (4-char Maidenhead) | `FN20` |
| `--rx-grid` | Yes | Receiver grid (4-char Maidenhead) | `IO91` |
| `--band` | Yes | Band (160m, 80m, 60m, 40m, 30m, 20m, 17m, 15m, 12m, 10m) | `20m` |
| `--sfi` | No | Solar Flux Index (default: 150) | `140` |
| `--kp` | No | Kp geomagnetic index 0-9 (default: 2) | `3` |
| `--hour` | No | UTC hour 0-23 (default: 12) | `14` |
| `--month` | No | Month 1-12 (default: 6) | `1` |

## Example

```bash
ionis-validate predict \
    --tx-grid DN26 --rx-grid IO91 \
    --band 20m --sfi 150 --kp 2 \
    --hour 14 --month 6
```

Output:

```
IONIS V20 Single Path Prediction
=================================
  TX: DN26 (47.0N, 112.0W)  →  RX: IO91 (51.5N, 1.0W)
  Band: 20m  |  SFI: 150  |  Kp: 2  |  Hour: 14 UTC  |  Month: June
  Distance: 7,842 km  |  Azimuth: 39.2°

  Predicted SNR: +0.432 sigma  (-6.8 dB)

  Mode Verdicts:
    WSPR (-28 dB):  OPEN
    FT8  (-21 dB):  OPEN
    CW   (-15 dB):  OPEN
    RTTY  (-5 dB):  OPEN
    SSB   (+3 dB):  CLOSED
```

## How It Works

The predictor:

1. Converts Maidenhead grids to latitude/longitude
2. Computes path geometry (distance, azimuth, midpoint)
3. Engineers 13 features matching training exactly
4. Runs the V20 checkpoint (single forward pass)
5. Denormalizes the sigma output to dB using per-band WSPR norm constants
6. Applies mode thresholds to produce open/closed verdicts

## Mode Thresholds

| Mode | Threshold | What It Means |
|------|-----------|---------------|
| WSPR | -28 dB | Beacon minimum — signal floor |
| FT8/FT4 | -21 dB | Digital decode limit |
| CW | -15 dB | Readable by experienced operator |
| RTTY | -5 dB | Machine-copy reliable |
| SSB | +3 dB | Voice-quality communication |

A prediction of -6.8 dB means WSPR, FT8, and CW will work. RTTY is marginal.
SSB needs a stronger path.

## Tips

- **Try different hours**: HF propagation changes dramatically by time of day.
  Sweep `--hour 0` through `--hour 23` to find your opening.
- **Check SFI sensitivity**: Compare `--sfi 70` (solar minimum) vs `--sfi 200`
  (solar maximum) to see how much the sun matters for your path.
- **Storm impact**: Compare `--kp 1` (quiet) vs `--kp 5` (moderate storm) —
  high-latitude paths are most affected.
- **Band comparison**: The same path may be open on 20m but closed on 10m
  depending on solar conditions.
