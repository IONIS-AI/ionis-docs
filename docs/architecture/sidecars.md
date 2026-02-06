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

## Physics Verification (V12)

| Test | Condition | V10 Result | V12 Result | Grade |
|------|-----------|------------|------------|-------|
| Sun Test | SFI 70 → 200 | +0.48 dB | **+2.1 dB** | B |
| Storm Test | Kp 0 → 9 | +1.12 dB | **+4.0 dB** | A |
| Polar Storm | Kp 2 → 8 (polar) | — | +2.5 dB | B |
| D-Layer | 80m vs 20m noon | — | +0.0 dB | C |

V12 trained on aggregated signatures shows 4x stronger physics response than V10 on raw spots.

## SFI × Kp Matrix (V12)

Reference path: W3 → G (5,900 km, 20m)

| SFI \ Kp | Kp=0 | Kp=2 | Kp=5 | Kp=9 |
|----------|------|------|------|------|
| SFI 70 | -20.0 | -21.1 | -22.0 | -24.0 |
| SFI 150 | -19.0 | -20.0 | -21.0 | -23.0 |
| SFI 200 | -18.0 | -19.0 | -20.0 | -22.0 |

Down = higher SFI = better. Right = higher Kp = worse. Correct physics.
