# V22-gamma Beta Test Plan

This page walks you through every test we need you to run. Follow the
tests in order. Each test tells you exactly what to enter, what to
expect, and what to record.

You can use either the **command line** (CLI) or the **browser UI**.
Both produce identical results — pick whichever you prefer.

!!! tip "Before you start"
    Complete the [Getting Started](getting-started.md) installation first.
    Run `ionis-validate --version` and confirm you see `4.0.0` or later.

---

## Test-1: Verify Installation

**Objective:** Confirm the model loads and reports correct metadata.

=== "CLI"

    ```
    ionis-validate info
    ```

=== "Browser UI"

    ```
    ionis-validate ui
    ```

    Click the **Info** tab.

**Expected results:**

| Field | Expected Value |
|-------|----------------|
| Version | V22-gamma + PhysicsOverrideLayer |
| Architecture | IonisGate |
| Parameters | 205,621 |
| Device | cpu, cuda, or mps |

**Record:** Your device type (cpu, cuda, or mps).

!!! failure "Stop condition"
    If any value is missing or wrong, do not continue. Skip to
    [Test-8](#test-8-submit-your-results) and report the problem.

---

## Test-2: Automated Test Suite

**Objective:** Run all 29 operator-grounded and band x time tests.

=== "CLI"

    ```
    ionis-validate test
    ```

=== "Browser UI"

    Click the **Report** tab. Leave "Include test suite results" on.
    Click **Generate Report**. The test results appear in the report body.

**Expected result:** KI7MT 18/18 PASS, TST-900 9/11 (TST-903/904 are known).

**Record:** KI7MT pass count and TST-900 score.

!!! failure "Stop condition"
    If any test fails, do not continue. Skip to
    [Test-8](#test-8-submit-your-results) and report the failure.
    Failed automated tests on your system are high-priority findings.

---

## Test-3: Reference Path — Good Conditions

**Objective:** Predict a well-known 20m transatlantic path under quiet
solar conditions. This gives us a baseline to compare across all testers.

=== "CLI (Windows)"

    ```
    ionis-validate predict --tx-grid FN31 --rx-grid IO91 --band 20m --sfi 150 --kp 2 --hour 14 --month 6 --day-of-year 172
    ```

=== "CLI (macOS / Linux)"

    ```bash
    ionis-validate predict \
        --tx-grid FN31 --rx-grid IO91 \
        --band 20m --sfi 150 --kp 2 \
        --hour 14 --month 6 --day-of-year 172
    ```

=== "Browser UI"

    **Predict** tab. Enter these values:

    | Field | Value |
    |-------|-------|
    | TX Grid | `FN31` |
    | RX Grid | `IO91` |
    | Band | 20m |
    | SFI | 150 |
    | Kp | 2 |
    | Hour UTC | 14 |
    | Month | 6 |
    | Day of Year | 172 |

    Click **Predict**.

**Expected results:**

- Predicted dB: **-18.9 dB** (exactly, on all platforms)
- WSPR: **OPEN**
- FT8: **OPEN**
- CW: **closed** (below the -15 dB threshold)
- SSB: **closed**

**Record:** The exact predicted dB value and all five mode verdicts.

---

## Test-4: Reference Path — Marginal Conditions

**Objective:** Predict a difficult 15m path with moderate solar flux.
This tests whether the model correctly identifies marginal openings.

=== "CLI (Windows)"

    ```
    ionis-validate predict --tx-grid DN46 --rx-grid PM95 --band 15m --sfi 120 --kp 2 --hour 6 --month 12 --day-of-year 350
    ```

=== "CLI (macOS / Linux)"

    ```bash
    ionis-validate predict \
        --tx-grid DN46 --rx-grid PM95 \
        --band 15m --sfi 120 --kp 2 \
        --hour 6 --month 12 --day-of-year 350
    ```

=== "Browser UI"

    **Predict** tab. Click **Clear** first, then enter:

    | Field | Value |
    |-------|-------|
    | TX Grid | `DN46` |
    | RX Grid | `PM95` |
    | Band | 15m |
    | SFI | 120 |
    | Kp | 2 |
    | Hour UTC | 6 |
    | Month | 12 |
    | Day of Year | 350 |

    Click **Predict**.

**Expected results:**

- Predicted dB: **-17.1 dB** (exactly, on all platforms)
- WSPR: **OPEN**
- FT8: **OPEN**
- CW: **closed**
- SSB: **closed**

**Record:** The exact predicted dB value and all five mode verdicts.

---

## Test-5: Reference Path — Geomagnetic Storm

**Objective:** Repeat the Test-3 path but under severe storm conditions
(Kp 7). The model should predict significantly worse propagation.

=== "CLI (Windows)"

    ```
    ionis-validate predict --tx-grid FN31 --rx-grid IO91 --band 20m --sfi 150 --kp 7 --hour 14 --month 6 --day-of-year 172
    ```

=== "CLI (macOS / Linux)"

    ```bash
    ionis-validate predict \
        --tx-grid FN31 --rx-grid IO91 \
        --band 20m --sfi 150 --kp 7 \
        --hour 14 --month 6 --day-of-year 172
    ```

=== "Browser UI"

    **Predict** tab. Click **Clear** first, then enter:

    | Field | Value |
    |-------|-------|
    | TX Grid | `FN31` |
    | RX Grid | `IO91` |
    | Band | 20m |
    | SFI | 150 |
    | Kp | 7 |
    | Hour UTC | 14 |
    | Month | 6 |
    | Day of Year | 172 |

    Click **Predict**.

**Expected results:**

- Predicted dB: **-24.1 dB** (exactly, on all platforms)
- This is **5.2 dB worse** than the Kp 2 result in Test-3 — the storm
  sidecar is applying a real penalty
- FT8 is now **closed** (below -21 dB threshold) — the storm killed the opening
- If your value does not match, that is a finding worth reporting

**Record:** The exact predicted dB value. Confirm it is worse than Test-3.

---

## Test-6: Your Own Path — Known Good

**Objective:** Predict a path you work regularly. You are the ground truth.

Think of an HF path you know well — one you work often enough to know
when it opens and closes. Enter your own grid, their grid, the band you
use, and the time and month when you typically make the contact.

=== "CLI"

    ```
    ionis-validate predict --tx-grid YOURGRID --rx-grid THEIRGRID --band 20m --sfi 150 --kp 2 --hour 14 --month 6 --day-of-year 172
    ```

    Replace `YOURGRID`, `THEIRGRID`, band, hour, and month with your real
    values.

=== "Browser UI"

    **Predict** tab. Click **Clear** first, then enter your own values.
    Click **Predict**.

**Record:**

- The grids, band, hour, and month you used
- The predicted dB value and mode verdicts
- Whether the model **agrees** with your experience
- If it disagrees, note the details — this is exactly what we need

---

## Test-7: Your Own Path — Known Bad

**Objective:** Predict a path you know does NOT work. Confirming negatives
is as valuable as confirming positives.

Think of a path you have tried and failed — for example, 10m to Australia
from your grid at midnight, or 160m to Japan. Enter it with realistic
conditions.

=== "CLI"

    Same command as Test-6 but with a path you know is dead.

=== "Browser UI"

    **Predict** tab. Click **Clear** first, then enter a path you know
    does not open. Click **Predict**.

**Expected result:** The model should predict your mode as **closed**.

**Record:**

- The grids, band, hour, and month you used
- Whether the model correctly predicted it as closed
- If the model says OPEN for a dead path, that is a finding

---

## Test-8: Submit Your Results

**Objective:** Generate a report and submit it so we can review your
findings.

=== "CLI (Windows)"

    ```
    ionis-validate report
    ```

    Copy the output from the terminal.

=== "CLI (macOS / Linux)"

    ```bash
    # macOS — copies to clipboard
    ionis-validate report | pbcopy

    # Linux — copies to clipboard
    ionis-validate report | xclip -selection clipboard
    ```

=== "Browser UI"

    Click the **Report** tab. Click **Generate Report**. Click **Copy to
    Clipboard**.

**Where to submit:**

Open a new issue here and paste your report:

[https://github.com/IONIS-AI/ionis-validate/issues/new/choose](https://github.com/IONIS-AI/ionis-validate/issues/new/choose)

**Include in your issue:**

1. The generated report (paste from clipboard)
2. Your Test-3, Test-4, Test-5 dB values (reference predictions)
3. Your Test-6 and Test-7 results (did the model agree with your
   experience?)
4. Anything that surprised you — good or bad

---

## Quick Reference Card

| Test | What | Key Input | Pass Criteria |
|------|------|-----------|---------------|
| Test-1 | Verify install | `ionis-validate info` | V22-gamma, 205,621 params |
| Test-2 | Automated suite | `ionis-validate test` | KI7MT 18/18, TST-900 9/11 |
| Test-3 | Good path | FN31 > IO91, 20m, Kp 2 | -18.9 dB, FT8 OPEN |
| Test-4 | Marginal path | DN46 > PM95, 15m, SFI 120 | -17.1 dB, FT8 OPEN |
| Test-5 | Storm path | FN31 > IO91, 20m, Kp 7 | -24.1 dB (5.2 dB worse) |
| Test-6 | Your good path | Your grids, your band | Matches your experience |
| Test-7 | Your bad path | A path you know is dead | Predicts closed |
| Test-8 | Submit results | `ionis-validate report` | GitHub Issue filed |
