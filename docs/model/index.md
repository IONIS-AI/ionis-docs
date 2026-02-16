# IONIS Model

IONIS (Ionospheric Neural Inference System) predicts HF radio signal-to-noise
ratio (SNR) for any transmitter-receiver path. One model, one forward pass,
six mode-aware operational verdicts — from WSPR at -28 dB to SSB at +5 dB.

## Current Production: V20 Golden Master

| Metric | Value |
|--------|-------|
| **Architecture** | IonisGate (203,573 parameters) |
| **Pearson correlation** | +0.4879 |
| **RMSE** | 0.862 sigma (~5.8 dB) |
| **Recall vs VOACAP** | 96.38% (+20.56 pp) |
| **PSK Reporter recall** | 84.14% (independent live data) |
| **Physics tests** | 4/4 PASS |

Trained on 20M WSPR + 4.55M DXpedition (50x) + 6.34M Contest signatures
(~31M rows) on Mac Studio M3 Ultra. 100 epochs in 4h 16m.

## Architecture

IonisGate separates geography from physics by design:

- **Trunk DNN**: 11 geography/time features through 512 - 256 - 128 - 1
- **Sun Sidecar**: SFI (solar flux) through a monotonic MLP — higher SFI always helps
- **Storm Sidecar**: Kp (geomagnetic) through a monotonic MLP — storms always hurt
- **Gated mixing**: Trunk-derived gates scale sidecar contributions by geography

The "Nuclear Option" — the trunk receives zero direct solar information. All
physics flows through constrained sidecars that cannot violate ionospheric law.

Read more: [IonisGate Architecture](architecture/ionisgate.md) |
[Monotonic Sidecars](architecture/sidecars.md)

## Methodology

The training pipeline transforms 13B+ raw radio observations into model-ready
signatures through a medallion architecture:

- **Bronze**: Raw ingest from WSPR, RBN, contest logs, PSK Reporter
- **Silver**: CUDA-accelerated embeddings with solar enrichment
- **Gold**: Aggregated signatures — grid-pair, band, time, solar, SNR

Read more: [Data Pipeline](methodology/data_pipeline.md) |
[Training](methodology/training.md)

## Validation

V20 is validated against three independent benchmarks:

1. **62-test automated battery** — physics, canonical paths, adversarial inputs, regression
2. **1M contest path comparison** — IONIS 96.38% vs VOACAP 75.82%
3. **PSK Reporter acid test** — 84.14% recall on data the model has never seen

Read more: [Validation Overview](validation/index.md) |
[Link Budget Battery](validation/v20_link_budget_battery.md)
