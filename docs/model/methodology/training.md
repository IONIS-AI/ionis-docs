---
description: >-
  Training methodology for the IONIS HF propagation model on Mac Studio M3 Ultra.
  Aggregated signatures from 13B observations, HuberLoss, differential learning
  rates, and physics-constrained sidecars that enforce ionospheric behavior.
---

# Training Methodology

## Training Architecture

IONIS is trained on **aggregated signatures** (`wspr.signatures_v2_terrestrial`) rather than raw spots.
This strips site-level noise and reveals the atmospheric transfer function.

| Setting | Raw spots | Aggregated signatures |
|---------|-----------|----------------------|
| Training rows | 10M spots | 20M signatures |
| Target | Individual SNR | Median SNR per bucket |
| RMSE | 2.48 dB | **0.862σ** (V20) |
| Pearson | +0.24 | **+0.4879** (V20) |

## Differential Learning Rate

Two-speed optimizer lets the trunk learn slowly while sidecars maintain physics:

| Component | Learning Rate | Purpose |
|-----------|---------------|---------|
| Trunk + Heads | 1e-5 | Slow — learns geography/time |
| Sun Sidecar | 1e-3 | Fast — maintains SFI monotonicity |
| Storm Sidecar | 1e-3 | Fast — maintains Kp monotonicity |

## Weight Clamping

Sidecar weights are clamped to `[0.5, 2.0]` after each optimizer step:

- **Lower bound (0.5)**: Prevents sidecar collapse to zero influence
- **Upper bound (2.0)**: Prevents sidecar explosion

## Gated Architecture

The trunk produces three outputs:

1. **base_snr** — geography-driven baseline
2. **sun_scaler** — gate ∈ [0.5, 2.0] modulating SFI effect by path
3. **storm_scaler** — gate ∈ [0.5, 2.0] modulating Kp effect by latitude

```
output = base_snr + sun_scaler × SunSidecar(sfi)
                  + storm_scaler × StormSidecar(kp)
```

## The Nuclear Option (Starvation Protocol)

The DNN receives **zero** direct solar/storm features. This forces the model to:

1. Learn geography, time, and seasonal patterns from the trunk
2. Learn solar physics exclusively through the constrained sidecars
3. Prevent the trunk from learning the survivorship bias shortcut

## Training Hardware

| Setting | Value |
|---------|-------|
| Hardware | Mac Studio M3 Ultra (96 GB unified) |
| Backend | PyTorch MPS |
| Data Path | ClickHouse via DAC link (10 Gbps+) at `10.60.1.1:9000` |
| Workers | 0 (MPS memory safety) |
| Epochs | 100 |
| Epoch Time | ~9s |
| Total Time | ~15 min |

## Convergence

Physics constraints remain positive throughout training. Aggregated signatures produce
stronger physics response than raw spots. V20 production achieves Pearson +0.4879
after 100 epochs (4h 16m on MPS).
