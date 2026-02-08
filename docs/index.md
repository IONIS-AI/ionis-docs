# KI7MT Sovereign AI Lab

**IONIS** — Ionospheric Neural Inference System

*The open-source HF propagation prediction engine.*

HF propagation prediction for the 21st century — built on 13.2B real-world observations. Self-hosted. No cloud dependencies.

| Data Source | Volume | Purpose |
|-------------|--------|---------|
| WSPR Spots | 10.8B | Signal floor, raw attenuation |
| RBN Spots | 2.18B | CW/RTTY traffic density |
| Contest Logs | 459K files (15 contests) | Ground truth validation |
| Aggregated Signatures | 93.8M | Noise-filtered training targets |
| Solar Indices | 76K rows (2000–2026) | SFI, Kp, SSN conditions |

## Current Model: IONIS V12 Signatures

| Metric | Value |
|--------|-------|
| **Architecture** | IonisV12Gate (203,573 params) |
| **RMSE** | 2.05 dB |
| **Pearson** | +0.3051 |
| **Physics Score** | 76.7/100 (Grade B) |
| **Test Suite** | 35/35 PASS |
| **SFI 70→200 benefit** | +2.1 dB |
| **Kp 0→9 storm cost** | +4.0 dB |

## Infrastructure

| Host | Role |
|------|------|
| **Threadripper 9975WX** | Control node — ClickHouse, CUDA, Go pipelines |
| **Mac Studio M3 Ultra** | Sage node — PyTorch training (MPS) |
| **EPYC 7302P** | Forge node — backup/replica |

## Documentation

- [Architecture](architecture/model_v10.md) — Model specs, sidecars, parameter counts
- [Methodology](methodology/data_pipeline.md) — Ingestion, feature engineering, training
- [Validation](validation/index.md) — V12 test specification (35 automated tests)
- [Roadmap](roadmap/d_to_z.md) — D-to-Z Digital Twin roadmap
- [Data Privacy & GDPR](data-privacy.md) — Data authorization, GDPR compliance, attribution
- [Ethos](ethos.md) — Core principles, statement of intent
