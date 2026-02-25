# Single Path Prediction

Predict the signal-to-noise ratio for any HF path from the command line.

## Usage

```bash
ionis-validate predict \
    --tx-grid <grid> --rx-grid <grid> \
    --band <band> \
    --sfi <value> --kp <value> \
    --hour <utc_hour> --month <month> \
    --day-of-year <day>
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `--tx-grid` | Yes | Transmitter grid (4-char Maidenhead) | `FN20` |
| `--rx-grid` | Yes | Receiver grid (4-char Maidenhead) | `IO91` |
| `--band` | Yes | Band (160m, 80m, 60m, 40m, 30m, 20m, 17m, 15m, 12m, 10m) | `20m` |
| `--sfi` | Yes | Solar Flux Index | `140` |
| `--kp` | Yes | Kp geomagnetic index 0-9 | `3` |
| `--hour` | Yes | UTC hour 0-23 | `14` |
| `--month` | Yes | Month 1-12 | `6` |
| `--day-of-year` | Yes | Day of year 1-366 | `172` |

## Example

```bash
ionis-validate predict \
    --tx-grid DN26 --rx-grid IO91 \
    --band 20m --sfi 150 --kp 2 \
    --hour 14 --month 6 --day-of-year 172
```

Output:

```
============================================================
  IONIS V22-gamma — Path Prediction
============================================================

  TX Grid:    DN26 (46.5N, -113.0E)
  RX Grid:    IO91 (51.5N, -1.0E)
  Distance:   7,842 km
  Band:       20m (14.097 MHz)
  Conditions: SFI 150, Kp 2.0
  Time:       14:00 UTC, month 6, day 172

  TX Solar:   +49.1 deg
  RX Solar:   +54.2 deg

  Raw Model:  +0.432 sigma
  Override:   not triggered
  Final SNR:  +0.432 sigma (-6.8 dB)

  Mode Verdicts:
    >>> WSPR   OPEN    (threshold: -28 dB)
    >>> FT8    OPEN    (threshold: -21 dB)
    >>> CW     OPEN    (threshold: -15 dB)
        RTTY   closed  (threshold: -5 dB)
        SSB    closed  (threshold: +3 dB)
```

## How It Works

The predictor:

1. Converts Maidenhead grids to latitude/longitude
2. Computes path geometry (distance, azimuth, midpoint)
3. Calculates solar depression angles for both endpoints
4. Engineers 17 features matching training exactly
5. Runs the V22-gamma checkpoint (single forward pass)
6. Applies PhysicsOverrideLayer (clamps high-band night paths if triggered)
7. Denormalizes the sigma output to dB using per-band WSPR norm constants
8. Applies mode thresholds to produce open/closed verdicts

## PhysicsOverrideLayer

After neural inference, a deterministic post-processing clamp is applied:

- **Condition**: freq >= 21 MHz AND both endpoints below -6 deg solar depression AND prediction > -1.0 sigma
- **Action**: Clamp prediction to -1.0 sigma
- **Purpose**: Close high bands (15m, 12m, 10m) when both endpoints are in darkness

The override status is shown in the output as "triggered" or "not triggered."

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
- **Day of year**: Use `--day-of-year` to capture seasonal effects. The model
  uses this for solar depression angle calculations.
