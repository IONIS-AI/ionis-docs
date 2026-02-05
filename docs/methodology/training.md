# Training Methodology

## Differential Learning Rate

V10 uses a two-speed optimizer to let the DNN learn slowly while sidecars maintain physics:

| Component | Learning Rate | Purpose |
|-----------|---------------|---------|
| DNN | 1e-5 | Slow student — learns geography/time |
| Sun Sidecar | 1e-3 | Fast — maintains SFI monotonicity |
| Storm Sidecar | 1e-3 | Fast — maintains Kp monotonicity |

## Weight Clamping

Sidecar weights are clamped to `[0.5, 2.0]` after each optimizer step:

- **Lower bound (0.5)**: Prevents sidecar collapse to zero influence
- **Upper bound (2.0)**: Prevents sidecar explosion

## Defibrillator Jump-Start

Sidecars are initialized with `fc2.bias = -10.0` ("Defibrillator V2") to ensure they begin in a useful operating range. Without this, sidecars can start in a dead zone and never activate.

## The Nuclear Option (Starvation Protocol)

The DNN receives **zero** direct solar/storm features. This forces the model to:

1. Learn geography, time, and seasonal patterns from the DNN
2. Learn solar physics exclusively through the constrained sidecars
3. Prevent the DNN from learning the survivorship bias shortcut

## Training Hardware

| Setting | Value |
|---------|-------|
| Hardware | Mac Studio M3 Ultra (96 GB unified) |
| Backend | PyTorch MPS |
| Data Path | ClickHouse via DAC link (10 Gbps+) at `10.60.1.1:9000` |
| Workers | 12 (Turbo Loader) |
| Prefetch | 4 |
| GPU Utilization | 88% @ 1238 MHz |
| Epoch Time | ~6-8s |

## Convergence

| Epoch | RMSE | Pearson | SFI+ | Kp9- |
|-------|------|---------|------|------|
| 1 | 2.51 | +0.106 | +0.6 | +1.5 |
| 10 | 2.49 | +0.197 | +0.5 | +1.5 |
| 25 | 2.48 | +0.226 | +0.5 | +1.1 |
| 50 | 2.48 | +0.235 | +0.5 | +1.1 |
| 100 | 2.48 | +0.240 | +0.5 | +1.1 |

Physics constraints (SFI+ and Kp9-) remained positive throughout all 100 epochs.
