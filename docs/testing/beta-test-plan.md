# V20 Beta Test Plan

This page walks you through every test we need you to run. Follow the
tests in order. Each test tells you exactly what to enter, what to
expect, and what to record.

You can use either the **command line** (CLI) or the **browser UI**.
Both produce identical results — pick whichever you prefer.

!!! tip "Before you start"
    Complete the [Getting Started](getting-started.md) installation first.
    Run `ionis-validate --version` and confirm you see `0.2.0` or later.

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
| Version | V20 (production) |
| Architecture | IonisGate |
| Parameters | 203,573 |
| Device | cpu, cuda, or mps |

**Record:** Your device type (cpu, cuda, or mps).

!!! failure "Stop condition"
    If any value is missing or wrong, do not continue. Skip to
    [Test-9](#test-9-submit-your-results) and report the problem.

---

## Test-2: Automated Test Suite

**Objective:** Run all 62 physics, robustness, and regression tests.

=== "CLI"

    ```
    ionis-validate test
    ```

=== "Browser UI"

    Click the **Report** tab. Leave "Include test suite results" on.
    Click **Generate Report**. The test results appear in the report body.

**Expected result:** `62/62` — every group shows `PASS`.

**Record:** Total pass count (should be 62/62).

!!! failure "Stop condition"
    If any test fails, do not continue. Skip to
    [Test-9](#test-9-submit-your-results) and report the failure.
    Failed automated tests on your system are high-priority findings.

---

## Test-3: Reference Path — Good Conditions

**Objective:** Predict a well-known 20m transatlantic path under quiet
solar conditions. This gives us a baseline to compare across all testers.

=== "CLI (Windows)"

    ```
    ionis-validate predict --tx-grid FN31 --rx-grid IO91 --band 20m --sfi 150 --kp 2 --hour 14 --month 6
    ```

=== "CLI (macOS / Linux)"

    ```bash
    ionis-validate predict \
        --tx-grid FN31 --rx-grid IO91 \
        --band 20m --sfi 150 --kp 2 \
        --hour 14 --month 6
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

    Click **Predict**.

**Expected results:**

- Predicted dB: **-18.8 dB** (exactly, on all platforms)
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
    ionis-validate predict --tx-grid DN46 --rx-grid PM95 --band 15m --sfi 120 --kp 2 --hour 6 --month 12
    ```

=== "CLI (macOS / Linux)"

    ```bash
    ionis-validate predict \
        --tx-grid DN46 --rx-grid PM95 \
        --band 15m --sfi 120 --kp 2 \
        --hour 6 --month 12
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

    Click **Predict**.

**Expected results:**

- Predicted dB: **-19.4 dB** (exactly, on all platforms)
- WSPR: **OPEN**
- FT8: **OPEN** (just above the -21 dB threshold)
- CW: **closed**
- SSB: **closed**

**Record:** The exact predicted dB value and all five mode verdicts.

---

## Test-5: Reference Path — Geomagnetic Storm

**Objective:** Repeat the Test-3 path but under severe storm conditions
(Kp 7). The model should predict significantly worse propagation.

=== "CLI (Windows)"

    ```
    ionis-validate predict --tx-grid FN31 --rx-grid IO91 --band 20m --sfi 150 --kp 7 --hour 14 --month 6
    ```

=== "CLI (macOS / Linux)"

    ```bash
    ionis-validate predict \
        --tx-grid FN31 --rx-grid IO91 \
        --band 20m --sfi 150 --kp 7 \
        --hour 14 --month 6
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

    Click **Predict**.

**Expected results:**

- Predicted dB: **-25.2 dB** (exactly, on all platforms)
- This is **6.4 dB worse** than the Kp 2 result in Test-3 — the storm
  sidecar is applying a real penalty
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
    ionis-validate predict --tx-grid YOURGRID --rx-grid THEIRGRID --band 20m --sfi 150 --kp 2 --hour 14 --month 6
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

## Test-8: ADIF Log Validation (Optional)

**Objective:** Validate the model against your actual QSO history. This
is the most statistically meaningful test — hundreds or thousands of
real contacts compared to the model's predictions.

!!! info "Where to get your ADIF file"
    Export from your logger:

    - **QRZ**: Logbook > Export > ADIF (recommended — most reliable)
    - **LoTW**: Log Downloads > check both "Include QSL details" and
      "Include QSO station details"
    - **eQSL**: may be missing `MY_GRIDSQUARE` — QRZ is more reliable

=== "CLI"

    ```
    ionis-validate adif my_log.adi
    ```

    Replace `my_log.adi` with the path to your file.

=== "Browser UI"

    Click the **ADIF** tab. Upload your `.adi` or `.adif` file. Leave SFI
    at 150 and Kp at 2 (defaults). Click **Validate**.

**What to record:**

| Metric | Where to find it |
|--------|-----------------|
| Overall recall % | The headline number |
| Observations count | How many QSOs were validated |
| Skipped count | How many were skipped (and why) |
| Recall by mode | Digital, CW, RTTY, SSB breakdown |
| Recall by band | Which bands score highest and lowest |
| Pearson correlation | Shown if you have FT8 QSOs with signal reports |

!!! note "What recall means"
    Every QSO in your log is a contact that happened — the band was open.
    Recall measures how often the model agrees. 80% recall means the model
    correctly predicted "band open" for 80% of your actual contacts.

---

## Test-9: Submit Your Results

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
4. Your Test-8 recall percentage (if you ran it)
5. Anything that surprised you — good or bad

---

## Quick Reference Card

| Test | What | Key Input | Pass Criteria |
|------|------|-----------|---------------|
| Test-1 | Verify install | `ionis-validate info` | V20, 203,573 params |
| Test-2 | Automated suite | `ionis-validate test` | 62/62 pass |
| Test-3 | Good path | FN31 > IO91, 20m, Kp 2 | -18.8 dB, FT8 OPEN |
| Test-4 | Marginal path | DN46 > PM95, 15m, SFI 120 | -19.4 dB, FT8 OPEN |
| Test-5 | Storm path | FN31 > IO91, 20m, Kp 7 | -25.2 dB (6.4 dB worse) |
| Test-6 | Your good path | Your grids, your band | Matches your experience |
| Test-7 | Your bad path | A path you know is dead | Predicts closed |
| Test-8 | ADIF log | Your QSO log file | Recall %, mode/band split |
| Test-9 | Submit results | `ionis-validate report` | GitHub Issue filed |
