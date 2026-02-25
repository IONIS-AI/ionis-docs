# Getting Started

## Prerequisites

- Python 3.10+
- No GPU, no database, no special hardware

!!! tip "Check your Python version"
    Open a terminal (or Command Prompt on Windows) and run:

    ```
    python --version
    ```

    If you see `Python 3.10` or higher, you're good. If you don't have Python
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
- The V22-gamma model checkpoint and config (safetensors, ~50 MB)
- PyTorch, NumPy, and safetensors (pulled automatically, ~800 MB)

## Verify Installation

```
ionis-validate info
```

Expected output includes model version (V22-gamma), parameter count (205,621),
PhysicsOverrideLayer status, and your system's PyTorch device (CPU, CUDA, or MPS).

## First Run

Run the full test suite:

```
ionis-validate test
```

This executes 29 tests across 2 groups:

| Group | Tests | What It Checks |
|-------|-------|----------------|
| KI7MT Operator Tests | 18 | Operator-grounded paths from 49K QSOs + 5.7M contest signatures |
| TST-900 Band x Time | 11 | Band discrimination across day/night/twilight periods |

Expected: KI7MT 18/18 PASS, TST-900 9/11 (TST-903 and TST-904 are known).
If any KI7MT test fails, see [Reporting Issues](reporting.md).

## Try a Prediction

Predict a 20m path from your grid:

=== "Windows"

    ```
    ionis-validate predict --tx-grid FN20 --rx-grid IO91 --band 20m --sfi 150 --kp 2 --hour 14 --month 6 --day-of-year 172
    ```

=== "macOS / Linux"

    ```bash
    ionis-validate predict \
        --tx-grid FN20 --rx-grid IO91 \
        --band 20m --sfi 150 --kp 2 \
        --hour 14 --month 6 --day-of-year 172
    ```

The output shows predicted SNR (in sigma and dB) and per-mode verdicts:
WSPR, FT8, CW, RTTY, and SSB — open or closed.

## Browser UI

The optional browser UI wraps every command in a point-and-click dashboard.
Install the UI extras and launch:

```
pip install "ionis-validate[ui]"
ionis-validate ui
```

This opens a browser tab at `http://localhost:8765` with tabs for
Predict, Custom, Report, and Info.

## Cleanup

When you are done testing, deactivate the virtual environment and delete
the folder. Nothing else to uninstall.

=== "Windows"

    ```
    deactivate
    rmdir /s /q .venv
    ```

=== "macOS / Linux"

    ```bash
    deactivate
    rm -rf .venv
    ```

## What's Next

- [Test Suite](test-suite.md) — understand what each test group validates
- [Single Path Prediction](predict.md) — full CLI reference
- [Custom Path Tests](custom-paths.md) — batch-test your own paths
