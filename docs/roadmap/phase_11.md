# Phase 11: Production Validation & Expansion

!!! warning "Legacy Document"
    This phase planning document has been superseded by the [D-to-Z Digital Twin Roadmap](d_to_z.md).

    V11 and V12 have been trained and validated. Current work is on Steps F–I.

## Overview (Historical)

Phase 10 resolved the Kp Inversion Problem through Dual Monotonic Sidecars. Phase 11 focused on quantifying V10 performance across diverse global conditions and preparing for V11.

## V10 Stress Testing

### A. Path-Specific Holdout Tests

- **Polar Challenge**: Test paths crossing the Auroral Ovals. Does the Kp Sidecar correctly penalize high-latitude paths more severely than equatorial ones?
- **Long-Path vs. Short-Path**: Evaluate NVIS vs. 10,000km+ multi-hop paths
- **Blind Geographic Regions**: Test on under-represented regions (South America, Africa) for spatial generalization

### B. Temporal Stability

- **Dawn/Dusk Transition**: Verify Grey Line SNR swings are captured by `hour_sin/cos` and `day_night_est`
- **Solar Cycle Extrapolation**: Feed extreme SFI (350+) to verify sidecars don't explode

## V11 Design Goals

### Frequency-Aware Sidecars

Current sidecars apply global solar benefit regardless of band. In reality, high SFI benefits 10m far more than 160m (which suffers D-layer absorption).

### Seasonal Path Interactions

Introduce `midpoint_lat × season_cos` interaction terms to capture seasonal ionization density shifts.

## Engineering Infrastructure

| Feature | Description |
|---------|-------------|
| Ionis-Eval Suite | 50 globally distributed paths for checkpoint evaluation |
| Sidecar Visualization | Automated Benefit vs SFI plots per epoch |
| Quantization Pipeline | CoreML/ONNX export for M3 Ultra Neural Engine |

## First Deliverable

**Global SNR Heatmap Generator** — takes a transmitter location and generates a world map of predicted SNR for a given band and solar condition. Fastest path to visual model audit.
