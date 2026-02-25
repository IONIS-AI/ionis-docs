---
description: >-
  IonisGate neural network architecture for HF propagation prediction. Physics-constrained
  sidecars enforce solar flux and geomagnetic storm behavior. V22-gamma production model
  with PhysicsOverrideLayer achieves Pearson +0.492, KI7MT 17/17, TST-900 9/11.
---

# IONIS Model

IONIS (Ionospheric Neural Inference System) predicts HF radio signal-to-noise
ratio (SNR) for any transmitter-receiver path. One model, one forward pass,
six mode-aware operational verdicts — from WSPR at -28 dB to SSB at +5 dB.

## Current Production: IONIS V22-gamma + PhysicsOverrideLayer

| Metric | Value |
|--------|-------|
| **Architecture** | IonisGate (205,621 parameters) + PhysicsOverrideLayer |
| **Pearson correlation** | +0.492 |
| **RMSE** | 0.821σ (~5.5 dB) |
| **KI7MT operator tests** | 17/17 PASS |
| **TST-900 band x time** | 9/11 |
| **Checkpoint** | safetensors (805 KB) |

Trained on 20M WSPR + 4.55M DXpedition (50x) + 6.34M Contest signatures
(~31M rows) on Mac Studio M3 Ultra. PhysicsOverrideLayer adds deterministic
post-inference clamping for high-band night closure.

## Architecture

IonisGate separates geography from physics by design:

- **Trunk DNN**: 15 geography/time features through 512 - 256 - 128 - 1
- **Sun Sidecar**: SFI (solar flux) through a monotonic MLP — higher SFI always helps
- **Storm Sidecar**: Kp (geomagnetic) through a monotonic MLP — storms always hurt
- **Gated mixing**: Trunk-derived gates scale sidecar contributions by geography

The "Nuclear Option" — the trunk receives zero direct solar information. All
physics flows through constrained sidecars that cannot violate ionospheric law.

Read more: [IonisGate Architecture](architecture/ionisgate.md) |
[Monotonic Sidecars](architecture/sidecars.md)

## Methodology

The training pipeline transforms 14B+ raw radio observations into model-ready
signatures through a medallion architecture:

- **Bronze**: Raw ingest from WSPR, RBN, contest logs, PSK Reporter
- **Silver**: CUDA-accelerated embeddings with solar enrichment
- **Gold**: Aggregated signatures — grid-pair, band, time, solar, SNR

Read more: [Data Pipeline](methodology/data_pipeline.md) |
[Training](methodology/training.md)

## Validation

V22-gamma is validated against multiple independent benchmarks:

1. **KI7MT operator-grounded tests** — 17/17 hard pass (18 tests from 49K QSOs + 5.7M contest signatures)
2. **TST-900 band x time discrimination** — 9/11 across all HF bands and time periods
3. **PhysicsOverrideLayer verification** — deterministic clamp fires on high-band night paths

V20 historical validation (VOACAP comparison, PSK Reporter acid test) provides
the foundation that V22-gamma inherits and improves upon.

Read more: [Validation Overview](validation/index.md) |
[Link Budget Battery](validation/v20_link_budget_battery.md)
