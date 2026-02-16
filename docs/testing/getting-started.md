# Getting Started

## Prerequisites

You need a Rocky Linux 9 / RHEL 9 / Fedora system with Python 3.9+. No GPU,
no ClickHouse, no special hardware.

## Install

### 1. Enable the COPR Repository

```bash
sudo dnf copr enable ki7mt/ionis-ai
```

### 2. Install the Validation Package

```bash
sudo dnf install ionis-training-validate
```

This installs:

- `/usr/bin/ionis-validate` — CLI entry point
- `/usr/share/ionis-training/versions/v20/` — model checkpoint, config, tests
- `/usr/share/ionis-training/requirements-validate.txt` — Python dependency list

### 3. Install Python Dependencies

```bash
pip3 install -r /usr/share/ionis-training/requirements-validate.txt
```

This pulls in PyTorch and NumPy. No other dependencies.

### 4. Verify Installation

```bash
ionis-validate info
```

Expected output includes model version (V20), parameter count (203,573),
checkpoint metrics, and your system's PyTorch device (CPU, CUDA, or MPS).

## First Run

Run the full test suite:

```bash
ionis-validate test
```

This executes 62 tests across 8 groups:

| Group | Tests | What It Checks |
|-------|-------|----------------|
| TST-100 | 30 | Canonical paths — global HF coverage |
| TST-200 | 6 | Physics — SFI helps, storms hurt, polar degrades |
| TST-300 | 5 | Input validation — boundary checks |
| TST-400 | 4 | Hallucination traps — out-of-domain detection |
| TST-500 | 7 | Robustness — determinism, device portability |
| TST-600 | 4 | Adversarial — malicious input handling |
| TST-700 | 3 | Bias — geographic, temporal, band fairness |
| TST-800 | 3 | Regression — catch silent degradation |

All 62 should pass. If any fail, see [Reporting Issues](reporting.md).

## Try a Prediction

Predict a 20m path from your grid:

```bash
ionis-validate predict \
    --tx-grid FN20 --rx-grid IO91 \
    --band 20m --sfi 150 --kp 2 \
    --hour 14 --month 6
```

The output shows predicted SNR (in sigma and dB) and per-mode verdicts:
WSPR, FT8, CW, RTTY, and SSB — open or closed.

## What's Next

- [Test Suite](test-suite.md) — understand what each test group validates
- [Single Path Prediction](predict.md) — full CLI reference
- [Custom Path Tests](custom-paths.md) — batch-test your own paths
