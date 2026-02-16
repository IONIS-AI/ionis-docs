# Testing

The IONIS validation suite lets you verify the V20 model against your own
operating experience. Install the package, run the tests, predict your paths,
and tell us what the model gets wrong.

This is **end-user model testing** — you do not need ClickHouse, training
scripts, or any understanding of the IONIS pipeline. Everything runs locally
with the shipped checkpoint.

## What You Can Do

| Command | Purpose |
|---------|---------|
| `ionis-validate test` | Run the full 62-test automated battery |
| `ionis-validate predict` | Predict a single HF path from your grid |
| `ionis-validate custom` | Batch-test your own paths from a JSON file |
| `ionis-validate report` | Generate a structured report for GitHub Issues |
| `ionis-validate info` | Show model version, system info, and diagnostics |

## Requirements

- Rocky Linux 9 / RHEL 9 / Fedora (x86_64)
- Python 3.9+
- ~1 GB disk (PyTorch + model checkpoint)
- No GPU required (CPU inference)

## Quick Start

```bash
# Enable the COPR repository
sudo dnf copr enable ki7mt/ionis-ai

# Install the validation package
sudo dnf install ionis-training-validate

# Install Python dependencies
pip3 install -r /usr/share/ionis-training/requirements-validate.txt

# Verify installation
ionis-validate info

# Run the test suite
ionis-validate test
```

## Documentation

- [Getting Started](getting-started.md) — Installation and first run
- [Test Suite](test-suite.md) — What the 62 tests cover and how to read results
- [Single Path Prediction](predict.md) — Predict any HF path from the command line
- [Custom Path Tests](custom-paths.md) — Define your own test paths in JSON
- [Reporting Issues](reporting.md) — How to file feedback and what to include
