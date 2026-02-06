# Training Methodology

## Current Production Model: V12

V12 is trained on **aggregated signatures** (`wspr.signatures_v1`) rather than raw spots.
This strips site-level noise and reveals the atmospheric transfer function.

| Setting | V10 (raw spots) | V12 (aggregated) |
|---------|-----------------|------------------|
| Training rows | 10M spots | 20M signatures |
| Target | Individual SNR | Median SNR per bucket |
| RMSE | 2.48 dB | **2.05 dB** |
| Pearson | +0.24 | **+0.31** |

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

## Gated Architecture (V11/V12)

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

## V12 Convergence

| Epoch | RMSE | Pearson | SFI+ | Kp9 Cost |
|-------|------|---------|------|----------|
| 1 | 2.25 | +0.18 | +1.5 | +3.0 |
| 25 | 2.10 | +0.27 | +2.0 | +3.8 |
| 50 | 2.06 | +0.30 | +2.1 | +4.0 |
| 100 | 2.05 | +0.31 | +2.1 | +4.0 |

Physics constraints remained positive throughout. Aggregated signatures produce
4x stronger physics response than raw spots.
