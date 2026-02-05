# KI7MT Sovereign AI Lab

**IONIS** — Ionospheric Neural Inference System

Self-hosted data center for HF radio propagation prediction using 10.8B WSPR spots, solar indices, and GPU-accelerated ML. No cloud dependencies.

## Current Model: IONIS V10

| Metric | Value |
|--------|-------|
| **Architecture** | IonisDualMono (170,547 params) |
| **RMSE** | 2.48 dB |
| **Pearson** | +0.2395 |
| **SFI 70→200 benefit** | +0.48 dB |
| **Kp 0→9 storm cost** | +1.12 dB |
| **Kp Inversion** | SOLVED |

## Infrastructure

| Host | Role |
|------|------|
| **Threadripper 9975WX** | Control node — ClickHouse, CUDA, Go pipelines |
| **Mac Studio M3 Ultra** | Sage node — PyTorch training (MPS) |
| **EPYC 7302P** | Forge node — backup/replica |

## Documentation

- [Architecture](architecture/model_v10.md) — Model specs, sidecars, parameter counts
- [Methodology](methodology/data_pipeline.md) — Ingestion, feature engineering, training
- [Validation](validation/index.md) — Automated test reports
- [Roadmap](roadmap/phase_11.md) — Phase 11 planning
