# Getting Started

## Prerequisites

You need Python 3.9 or newer. No GPU, no database, no special hardware.

!!! tip "Check your Python version"
    Open a terminal (or Command Prompt on Windows) and run:

    ```
    python --version
    ```

    If you see `Python 3.9` or higher, you're good. If you don't have Python
    installed, download it from [python.org](https://www.python.org/downloads/).

## Install

=== "Windows"

    Open **Command Prompt** or **PowerShell**:

    ```
    pip install ionis-validate
    ```

    !!! note
        If `pip` is not recognized, try `python -m pip install ionis-validate`.
        If you have both Python 2 and 3 installed, use `pip3` instead.

=== "macOS"

    Open **Terminal**:

    ```
    pip3 install ionis-validate
    ```

    On macOS, the system Python may be outdated. If you installed Python via
    [Homebrew](https://brew.sh/) or from python.org, `pip3` points to the
    correct version.

=== "Linux"

    ```bash
    pip3 install ionis-validate
    ```

    Most distributions ship Python 3.9+. If yours doesn't, use your package
    manager to install a newer Python first (e.g. `sudo apt install python3`
    on Debian/Ubuntu).

This installs:

- `ionis-validate` — the CLI tool
- The V20 model checkpoint and config (~50 MB)
- PyTorch and NumPy (pulled automatically, ~800 MB)

## Verify Installation

```
ionis-validate info
```

Expected output includes model version (V20), parameter count (203,573),
checkpoint metrics, and your system's PyTorch device (CPU, CUDA, or MPS).

## First Run

Run the full test suite:

```
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

=== "Windows"

    ```
    ionis-validate predict --tx-grid FN20 --rx-grid IO91 --band 20m --sfi 150 --kp 2 --hour 14 --month 6
    ```

=== "macOS / Linux"

    ```bash
    ionis-validate predict \
        --tx-grid FN20 --rx-grid IO91 \
        --band 20m --sfi 150 --kp 2 \
        --hour 14 --month 6
    ```

The output shows predicted SNR (in sigma and dB) and per-mode verdicts:
WSPR, FT8, CW, RTTY, and SSB — open or closed.

## Browser UI

The optional browser UI wraps every command in a point-and-click dashboard.
It requires **Python 3.10+** and an additional install step.

=== "Windows"

    ```
    pip install "ionis-validate[ui]"
    ionis-validate ui
    ```

=== "macOS"

    ```
    pip3 install "ionis-validate[ui]"
    ionis-validate ui
    ```

=== "Linux"

    ```bash
    pip3 install "ionis-validate[ui]"
    ionis-validate ui
    ```

This opens a browser tab at `http://localhost:8765` with four tabs:

- **Predict** — single path prediction form
- **Custom** — paste or upload a JSON test file
- **ADIF** — upload your QSO log and see recall stats
- **Info** — model version, checkpoint metrics, system details

!!! info "Python 3.10+ required for the UI"
    If you're on Python 3.9, the base CLI works fine — only the browser UI
    needs 3.10+. The `ionis-validate ui` command will tell you if your
    Python version is too old.

## What's Next

- [Test Suite](test-suite.md) — understand what each test group validates
- [Single Path Prediction](predict.md) — full CLI reference
- [Custom Path Tests](custom-paths.md) — batch-test your own paths
- [ADIF Log Validation](adif-validation.md) — validate the model against your own QSO log
