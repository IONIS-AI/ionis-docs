# Monotonic Sidecars — Physics Constraints

## The Problem

WSPR data contains **survivorship bias**: during geomagnetic storms (high Kp), only strong signals are decoded. A naive DNN learns "storms = good" — the **Kp Inversion Problem**.

## The Solution: Dual Monotonic Sidecars

Two small MonotonicMLP networks enforce physics constraints that the DNN cannot override:

### Sun Sidecar (SFI → SNR boost)

- **Input**: Solar Flux Index (SFI), normalized as SFI / 300
- **Constraint**: Monotonic increasing — higher SFI always improves SNR
- **Physics**: More solar flux → more ionization → better HF propagation

### Storm Sidecar (Kp → SNR penalty)

- **Input**: `kp_penalty = 1 - Kp/9` (inverted so monotonic increasing = storms degrade)
- **Constraint**: Monotonic increasing — higher penalty (lower Kp) always improves SNR
- **Physics**: Geomagnetic storms → ionospheric disturbance → absorption/fading

## Relief Valve Design

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Weight Clamp Range | 0.5 – 2.0 | Prevents collapse AND explosion |
| fc1.bias | Frozen | Maintains activation shape |
| fc2.bias | Learnable (-10.65) | Relief valve for calibration |
| Initial fc2.bias | -10.0 | Defibrillator jump-start |

## Physics Verification

| Test | Condition | Result | Status |
|------|-----------|--------|--------|
| Sun Test | SFI 70 → 200 | +0.48 dB benefit | PASS |
| Storm Test | Kp 0 → 9 | +1.12 dB cost | PASS |

## SFI × Kp Matrix

Reference path: FN31 → JO21 (5,900 km, 20m WSPR)

| SFI \ Kp | Kp=0 | Kp=2 | Kp=4 | Kp=6 | Kp=8 |
|----------|------|------|------|------|------|
| SFI 80 | -21.2 | -21.5 | -21.7 | -22.0 | -22.2 |
| SFI 120 | -21.1 | -21.3 | -21.6 | -21.8 | -22.1 |
| SFI 150 | -20.9 | -21.2 | -21.5 | -21.7 | -22.0 |
| SFI 200 | -20.7 | -21.0 | -21.3 | -21.5 | -21.8 |
| SFI 250 | -20.6 | -20.8 | -21.1 | -21.3 | -21.6 |

Down = higher SFI = better. Right = higher Kp = worse. Correct physics.
