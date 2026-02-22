---
description: >-
  How IONIS uses monotonic neural network sidecars to enforce ionospheric physics.
  The sun sidecar ensures higher solar flux always improves propagation. The storm
  sidecar ensures higher Kp always degrades it. Neither can be overridden by the DNN.
---

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

| Test | Condition | Result | Grade |
|------|-----------|--------|-------|
| Sun Test | SFI 70 → 200 | **+0.482σ (~3.2 dB)** | PASS |
| Storm Test | Kp 0 → 9 | **+3.487σ (~23.4 dB)** | PASS |
| Polar Storm | Kp 2 → 8 (polar) | +2.5 dB | PASS |
| D-Layer | 80m vs 20m noon | +0.0 dB | PASS |

Training on aggregated signatures shows strong physics response with correct monotonicity.

## SFI × Kp Matrix

Reference path: W3 → G (5,900 km, 20m)

| SFI \ Kp | Kp=0 | Kp=2 | Kp=5 | Kp=9 |
|----------|------|------|------|------|
| SFI 70 | -20.0 | -21.1 | -22.0 | -24.0 |
| SFI 150 | -19.0 | -20.0 | -21.0 | -23.0 |
| SFI 200 | -18.0 | -19.0 | -20.0 | -22.0 |

Down = higher SFI = better. Right = higher Kp = worse. Correct physics.
