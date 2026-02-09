# KI7MT Sovereign AI Lab

> *"The logs have been speaking for decades, but nobody is listening."*

Every day, millions of radio contacts are logged — WSPR beacons, RBN spots, contest QSOs. They contain the ground truth of HF propagation: what actually worked, when, and under what conditions. Until now, that data sat in archives, unused.

---

## What is IONIS?

**IONIS** (Ionospheric Neural Inference System) is a machine learning engine that predicts HF radio propagation using real-world observations instead of theoretical models.

The ionosphere is chaotic. Traditional tools like VOACAP rely on monthly median models derived from 1960s ionosonde data — they tell you what propagation *should* look like on an average day, not what it *will* look like today.

IONIS takes a different approach: learn from billions of actual radio contacts to predict what the bands will do next.

## Building on Traditional Prediction

Tools like VOACAP represent decades of ionospheric research and remain valuable references. But they have inherent limitations:

- **Static models**: Based on historical averages, updated infrequently
- **Limited validation**: Difficult to verify predictions against real-world results
- **Coarse resolution**: Monthly medians can miss daily and hourly variations

IONIS aims to complement these tools by adding what they lack: continuous learning from real-world observations. The two approaches validate each other — physics models provide theoretical grounding, while observational data reveals what actually happens.

## The IONIS Approach

IONIS is built on three pillars:

1. **Massive observational data**: 13.2B radio contacts from WSPR, RBN, and contest logs
2. **Neural network with physics constraints**: The model can't violate known ionospheric physics
3. **Continuous learning**: New data flows in every 2 minutes, forever

The goal: improve real-world accuracy by learning patterns that physics-first models can miss, while using traditional tools like VOACAP for validation and comparison.

## Current Status

**IONIS V13 Combined** is trained on WSPR signatures plus RBN DXpedition data, covering 152 rare DXCC entities that WSPR alone cannot reach. It correctly predicts:

- Higher solar flux (SFI) improves propagation (+5.2 dB benefit)
- Geomagnetic storms (Kp) degrade propagation (+10.4 dB cost)
- Path geometry, time of day, and seasonal effects

| Metric | Value |
|--------|-------|
| **RMSE** | 0.60σ (~4.0 dB) |
| **Pearson correlation** | +0.2865 |
| **Physics Tests** | 4/4 PASS |
| **Step I Recall** | 85.34% (+9.5 pp vs reference) |

V13 demonstrates consistent improvement over the ITS/NTIA reference model (VOACAP) on 1M validated contest paths, with particular gains on NVIS (160m) and sporadic-E (10m) propagation modes.

## Data Sources

| Source | Volume | Purpose |
|--------|--------|---------|
| **WSPR** | 10.8B spots | Signal floor, path attenuation |
| **RBN** | 2.18B spots | CW/RTTY traffic, DXpedition coverage |
| **Contest Logs** | 195M QSOs | Ground truth — proof the band was open |
| **Signatures** | 93.4M buckets | Aggregated path×band×hour×month patterns |
| **Solar Indices** | 76K rows | SFI, Kp, SSN conditions (2000–2026) |

## Infrastructure

Self-hosted, no cloud dependencies:

| Host | Role |
|------|------|
| **Threadripper 9975WX** | Control node — ClickHouse, CUDA, Go pipelines |
| **Mac Studio M3 Ultra** | Sage node — PyTorch training |
| **EPYC 7302P** | Forge node — backup/replica |

## Documentation

- [Architecture](architecture/model_v10.md) — Model design, sidecars, gated physics
- [Methodology](methodology/data_pipeline.md) — Data ingestion and training process
- [Validation](validation/index.md) — 35-test automated verification suite
- [Roadmap](roadmap/d_to_z.md) — D-to-Z path to production validation
- [Data Privacy](data-privacy.md) — GDPR compliance, data authorization
- [Ethos](ethos.md) — Core principles and statement of intent

## Open Source

All code, data pipelines, and documentation are open source. The goal is a reproducible, verifiable propagation prediction system that anyone can run.

*Built by KI7MT. No cloud. No vendor lock-in. Just physics and data.*
