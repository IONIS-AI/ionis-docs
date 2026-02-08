# KI7MT Sovereign AI Lab

## What is IONIS?

**IONIS** (Ionospheric Neural Inference System) is a machine learning engine that predicts HF radio propagation using real-world observations instead of theoretical models.

The ionosphere is chaotic. Traditional tools like VOACAP rely on monthly median models derived from 1960s ionosonde data — they tell you what propagation *should* look like on an average day, not what it *will* look like today.

IONIS takes a different approach: learn from billions of actual radio contacts to predict what the bands will do next.

## The Problem with Traditional Prediction

VOACAP and similar tools have fundamental limitations:

- **Static models**: Based on historical averages, never updated
- **No ground truth**: No way to verify predictions against reality
- **Coarse resolution**: Monthly medians miss daily and hourly variations
- **No learning**: Same prediction today as 20 years ago

Amateur radio operators know this intuitively. The bands don't behave like the textbooks say — but nobody has quantified *how* they differ or built tools that learn from experience.

## The IONIS Approach

IONIS is built on three pillars:

1. **Massive observational data**: 13.2B radio contacts from WSPR, RBN, and contest logs
2. **Neural network with physics constraints**: The model can't violate known ionospheric physics
3. **Continuous learning**: New data flows in every 2 minutes, forever

The goal: beat VOACAP on real-world accuracy by learning patterns that physics-first models miss.

## Current Status

IONIS V12 is trained on 20M aggregated WSPR signatures covering 2020–2026. It correctly predicts:

- Higher solar flux (SFI) improves propagation
- Geomagnetic storms (Kp) degrade propagation
- Path geometry, time of day, and seasonal effects

| Metric | Value |
|--------|-------|
| **RMSE** | 2.03 dB |
| **Pearson correlation** | +0.3153 |
| **Physics Score** | 74.2/100 |
| **Test Suite** | 35/35 PASS |

The model is not perfect — a Pearson of +0.32 means "right more than wrong, but not always." That's expected for ionospheric prediction. The atmosphere doesn't fully cooperate.

## Data Sources

| Source | Volume | Purpose |
|--------|--------|---------|
| **WSPR** | 10.8B spots | Signal floor, path attenuation |
| **RBN** | 2.18B spots | CW/RTTY traffic patterns |
| **Contest Logs** | 232.6M QSOs | Ground truth — proof the band was open |
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
- [Roadmap](roadmap/d_to_z.md) — D-to-Z path to beating VOACAP
- [Data Privacy](data-privacy.md) — GDPR compliance, data authorization
- [Ethos](ethos.md) — Core principles and statement of intent

## Open Source

All code, data pipelines, and documentation are open source. The goal is a reproducible, verifiable propagation prediction system that anyone can run.

*Built by KI7MT. No cloud. No vendor lock-in. Just physics and data.*
