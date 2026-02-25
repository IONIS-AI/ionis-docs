---
description: >-
  Install and run the IONIS V22-gamma validation suite. 29 operator-grounded tests
  verify physics constraints, band x time discrimination, and propagation predictions.
  Available via COPR (Rocky Linux) or PyPI.
---

# Testing

The IONIS validation suite lets you verify the V22-gamma model against your own
operating experience. Install the package, run the tests, predict your paths,
and tell us what the model gets wrong.

This is **end-user model testing** — you do not need ClickHouse, training
scripts, or any understanding of the IONIS pipeline. Everything runs locally
with the shipped checkpoint.

## What You Can Do

| Command | Purpose |
|---------|---------|
| `ionis-validate test` | Run the full 29-test automated battery |
| `ionis-validate predict` | Predict a single HF path from your grid |
| `ionis-validate custom` | Batch-test your own paths from a JSON file |
| `ionis-validate report` | Generate a structured report for GitHub Issues |
| `ionis-validate info` | Show model version, system info, and diagnostics |
| `ionis-validate ui` | Launch browser-based validation dashboard |

## Requirements

- Python 3.10+
- ~1 GB disk (PyTorch + model checkpoint)
- No GPU required (CPU inference)
- No database, no special hardware
- Works on **Windows**, **macOS**, and **Linux**

## Quick Start

```
pip install ionis-validate
```

```
ionis-validate info
ionis-validate test
```

See [Getting Started](getting-started.md) for platform-specific setup
instructions.

## Documentation

- [Getting Started](getting-started.md) — Installation and first run
- [Beta Test Plan](beta-test-plan.md) — Step-by-step testing checklist (start here after install)
- [Test Suite](test-suite.md) — What the 29 tests cover and how to read results
- [Single Path Prediction](predict.md) — Predict any HF path from the command line
- [Custom Path Tests](custom-paths.md) — Define your own test paths in JSON
- [Reporting Issues](reporting.md) — How to file feedback and what to include
