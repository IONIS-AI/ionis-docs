# IONIS V10 — IonisDualMono Architecture

## Overview

IONIS V10 resolves the Kp Inversion Problem through Dual Monotonic Sidecars. The DNN receives **zero** direct solar information ("Nuclear Option"), forcing all physics through constrained monotonic networks.

## Architecture

```
Input (13 features)
    │
    ├── DNN (11 features) ──► 512 ──► 256 ──► 128 ──► 1 (base SNR)
    │                                                    │
    ├── Sun Sidecar (sfi) ──► MonotonicMLP(8) ──────────►│ (sun boost)
    │                                                    │
    └── Storm Sidecar (kp_penalty) ──► MonotonicMLP(8) ──► (storm boost)
                                                         │
                                                    Output = Sum
```

## Parameter Count

| Component | Parameters | Role |
|-----------|------------|------|
| DNN | 170,497 | Geography & temporal patterns |
| Sun Sidecar | 25 | SFI → SNR boost (monotonic increasing) |
| Storm Sidecar | 25 | kp_penalty → SNR boost (monotonic increasing) |
| **Total** | **170,547** | |

## Training Configuration

| Setting | Value |
|---------|-------|
| Dataset | 10,000,000 WSPR spots |
| Date Range | 2020-01-01 to 2026-02-04 |
| Batch Size | 8,192 |
| Epochs | 100 |
| DNN Learning Rate | 1e-5 (slow student) |
| Sidecar Learning Rate | 1e-3 (maintain physics) |
| Optimizer | AdamW with differential LR |

## DNN Features (11)

| Feature | Normalization | Role |
|---------|---------------|------|
| `distance` | km / 20,000 | Path length |
| `freq_log` | log10(Hz) / 8.0 | Operating band |
| `hour_sin` | sin(2π·hour/24) | Time of day |
| `hour_cos` | cos(2π·hour/24) | Time of day |
| `az_sin` | sin(2π·az/360) | Azimuth direction |
| `az_cos` | cos(2π·az/360) | Azimuth direction |
| `lat_diff` | \|Δlat\| / 180 | North-south span |
| `midpoint_lat` | (lat_tx + lat_rx) / 2 / 90 | Path latitude |
| `season_sin` | sin(2π·month/12) | Seasonal variation |
| `season_cos` | cos(2π·month/12) | Seasonal variation |
| `day_night_est` | cos(2π·local_hour/24) | Solar illumination |

## Sidecar Features (2)

| Feature | Normalization | Sidecar | Constraint |
|---------|---------------|---------|------------|
| `sfi` | SFI / 300 | Sun | Monotonic increasing |
| `kp_penalty` | 1 - Kp/9 | Storm | Monotonic increasing |

## Model Lineage

```
v2 → v6_monotonic → v7_lobotomy → v8_sidecar → v9_dual_mono → v10_final → v11_gate → v12_signatures
```

- **V10** (`ionis_v10_final.pth`): Dual monotonic sidecars, Nuclear Option. RMSE 2.48 dB, Pearson +0.2395.
- **V11** (`ionis_v11_gate.pth`): Added gated multiplicative interaction between sidecars and DNN.
- **V12** (`ionis_v12_signatures.pth`): Trained on aggregated signatures (93.4M buckets). RMSE 2.03 dB, Pearson +0.3153. 35/35 physics tests. **Current production model.**

See [V11/V12 Gatekeeper](v11_design_intent.md) for architecture details.
