---
description: >-
  IONIS predicts HF propagation using physics-constrained neural networks trained
  on 14 billion real amateur radio observations. Open source, self-hosted,
  outperforms VOACAP by 20 percentage points on live PSK Reporter data.
---

# IONIS Sovereign AI Lab

> *"The logs have been speaking for decades, but nobody is listening."*

Every day, millions of radio contacts are logged — WSPR beacons, RBN spots, contest
QSOs, PSK Reporter decodes. They contain the ground truth of HF propagation: what
actually worked, when, and under what conditions. Until now, that data sat in archives,
unused for prediction.

---

## What is IONIS?

**IONIS** (Ionospheric Neural Inference System) is a machine learning engine that
predicts HF radio propagation using real-world observations instead of theoretical models.

IONIS answers one question: **"Can I work this path right now, on my mode?"**

One model predicts the signal level. A mode-aware threshold layer converts that into
operational verdicts for six mode families — from WSPR at -28 dB to SSB at +5 dB. One
forward pass, six answers.

## Building on Traditional Prediction

Tools like [VOACAP](https://www.voacap.com/) represent decades of ionospheric research and remain valuable
references. But they have inherent limitations:

- **Static models**: Based on historical averages, updated infrequently
- **Single-mode focus**: Designed for SSB voice circuits, with no concept of digital mode thresholds
- **Limited validation**: No feedback loop — predictions are never checked against observations
- **Coarse resolution**: Monthly medians miss daily and hourly variations

When FT8 operators use VOACAP and find "closed" paths that are wide open at -20 dB,
that's not a VOACAP bug — it was never designed for the digital world.

IONIS extends VOACAP's legacy by adding what it lacks: mode-aware thresholds, continuous
learning from real-world observations, and a closed-loop feedback cycle. The two
approaches validate each other — physics models provide theoretical grounding, while
observational data reveals what actually happens.

## The IONIS Approach

IONIS is built on four pillars:

1. **Massive observational data**: 14B+ radio contacts from four independent networks (WSPR, RBN, contest logs, and PSK Reporter)
2. **Neural network with physics constraints**: The model can't violate known ionospheric physics
3. **Mode-aware prediction**: One SNR prediction yields six operational verdicts (WSPR, FT8, CW, RTTY, SSB)
4. **Closed-loop validation**: Live [PSK Reporter](https://pskreporter.info) data continuously scores the model against observations it has never seen

The model predicts signal-to-noise ratio — a physical quantity that is mode-agnostic.
The threshold layer applies mode-specific decode limits to determine operational
viability. The physics doesn't change by mode; only the minimum signal required to use
it does.

## Current Status

**IONIS V22-gamma + PhysicsOverrideLayer** is the production model. Trained on 20M WSPR + 4.55M DXpedition (50x) + 6.34M Contest signatures (~31M rows), with a deterministic post-inference clamp for high-band night closure. It correctly predicts:

- Higher solar flux (SFI) improves propagation (monotonic)
- Geomagnetic storms (Kp) degrade propagation (monotonic)
- Path geometry, time of day, seasonal effects, and solar depression angle
- High-band closure at night (PhysicsOverrideLayer)

| Metric | Value |
|--------|-------|
| **Pearson correlation** | +0.492 |
| **RMSE** | 0.821σ (~5.5 dB) |
| **KI7MT operator tests** | 17/17 PASS |
| **TST-900 band x time** | 9/11 |
| **Parameters** | 205,621 |

V22-gamma demonstrates consistent improvement over the ITS/NTIA reference model (VOACAP) on validated contest paths. PSK Reporter live validation confirms the model generalizes to data it has never seen. For digital modes (FT8, FT4, WSPR) and CW, IONIS provides predictions where no comparable reference model exists.

## Data Sources

| Source | Volume | Mode Coverage | Purpose |
|--------|--------|---------------|---------|
| **WSPR** | 10.94B spots | WSPR (-28 dB) | Signal floor, continuous baseline |
| **RBN** | 2.26B spots | CW, RTTY | Machine-decoded SNR, DXpedition coverage |
| **Contest Logs** | 234M QSOs | SSB, CW, RTTY, Digi | Ground truth — proof the band was open |
| **PSK Reporter** | 514M+ spots (~26M/day, live) | FT8, FT4, WSPR | Real-time validation and future training |
| **Solar Indices** | 77K rows | — | SFI, Kp, SSN conditions (2000-2026) |

## Infrastructure

Self-hosted, no cloud dependencies:

| Host | Role |
|------|------|
| **Threadripper 9975WX** | Control node — ClickHouse, CUDA, Go pipelines |
| **Mac Studio M3 Ultra** | Sage node — PyTorch training |
| **EPYC 7302P** | Forge node — backup/replica |

## Documentation

- [Model](model/index.md) — IonisGate architecture, training methodology, validation results
- [Testing](testing/index.md) — Install, run, and report — beta testing for operators
- [Pipeline Apps](tools/index.md) — WSPR, solar, contest, RBN, PSK Reporter ingesters
- [DevOps](devops/index.md) — Hardware, pipeline runbook, operations
- [About](about/ethos.md) — Ethos, credits, data privacy

## Open Source

All code, data pipelines, and documentation are open source. The goal is a reproducible, verifiable propagation prediction system that anyone can run.

*Built by KI7MT. No cloud. No vendor lock-in. Just physics and data.*
