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

!!! warning "Use a virtual environment"
    We **strongly recommend** installing into a virtual environment, not
    your system Python. This keeps your system clean and makes cleanup
    easy — when you are done testing, just delete the folder.

### Step 1 — Create a virtual environment

=== "Windows"

    Open **Command Prompt** or **PowerShell**:

    ```
    python -m venv .venv
    .venv\Scripts\activate
    ```

=== "macOS"

    Open **Terminal**:

    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```

=== "Linux"

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

You should see `(.venv)` at the start of your prompt. This means the
virtual environment is active and all installs will go into the `.venv`
folder instead of your system Python.

!!! tip "Using uv instead"
    If you have [uv](https://docs.astral.sh/uv/) installed, you can use
    it for faster setup:

    ```
    uv venv .venv
    source .venv/bin/activate      # macOS / Linux
    .venv\Scripts\activate         # Windows
    ```

### Step 2 — Install ionis-validate

```
pip install ionis-validate
```

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

Create a separate virtual environment for the UI so you can remove it
independently:

=== "Windows"

    ```
    python -m venv .venv-ui
    .venv-ui\Scripts\activate
    pip install "ionis-validate[ui]"
    ionis-validate ui
    ```

=== "macOS"

    ```
    python3 -m venv .venv-ui
    source .venv-ui/bin/activate
    pip install "ionis-validate[ui]"
    ionis-validate ui
    ```

=== "Linux"

    ```bash
    python3 -m venv .venv-ui
    source .venv-ui/bin/activate
    pip install "ionis-validate[ui]"
    ionis-validate ui
    ```

This opens a browser tab at `http://localhost:8765` with tabs for
Predict, Custom, ADIF, Report, and Info.

!!! info "Python 3.10+ required for the UI"
    If your Python is 3.9, the base CLI works fine — only the browser UI
    needs 3.10+. The `ionis-validate ui` command will tell you if your
    Python version is too old.

## Cleanup

When you are done testing, deactivate the virtual environment and delete
the folder. Nothing else to uninstall.

=== "Windows"

    ```
    deactivate
    rmdir /s /q .venv
    rmdir /s /q .venv-ui
    ```

=== "macOS / Linux"

    ```bash
    deactivate
    rm -rf .venv .venv-ui
    ```

## What's Next

- [Test Suite](test-suite.md) — understand what each test group validates
- [Single Path Prediction](predict.md) — full CLI reference
- [Custom Path Tests](custom-paths.md) — batch-test your own paths
- [ADIF Log Validation](adif-validation.md) — validate the model against your own QSO log
