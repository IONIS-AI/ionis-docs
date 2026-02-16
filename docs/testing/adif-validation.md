# ADIF Log Validation

Validate the V20 model against your own QSO log. Export from eQSL, LoTW,
or QRZ, then run the tool. All processing happens locally — callsigns are
stripped immediately and never leave your machine.

!!! info "We only want the paths"
    IONIS studies propagation between grid squares, not the operators who
    generated them. This tool extracts **only propagation observations** —
    grid-pair, band, mode, and time — from your log. Callsigns, names,
    comments, and all personal fields are discarded at parse time. They are
    never stored, never transmitted, and never enter the validation pipeline.

    This complies with the [IONIS Ethos](../about/ethos.md) ("We have zero
    interest in personal data — only the propagation paths it represents")
    and our [Data Privacy & GDPR](../about/data-privacy.md) policy. There
    are no exceptions to that compliance.

## How It Works

1. You export your log as an ADIF (.adi) file from your logging service
2. `ionis-validate adif` parses the file **locally on your machine**
3. Callsigns are discarded at parse time — only grid-pairs, bands, times, and modes are kept
4. Each QSO that meets the model's input requirements (valid grids + HF band) is measured
5. Records missing required fields are skipped with the reason noted
6. The report shows recall: how often the model agrees the band was open

!!! tip "Use confirmed QSOs for best results"
    For the strongest ground truth, export only confirmed QSOs (eQSL, LoTW,
    or paper QSL) from your logger. A confirmed QSL proves the contact
    happened and the band was open. The tool will process any valid ADIF
    record, but unconfirmed QSOs may include logging errors or busted calls.

## Usage

```bash
ionis-validate adif my_log.adi --my-grid DN26
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `adif_file` | Yes | Path to your ADIF (.adi) file |
| `--my-grid` | Yes | Your 4-character Maidenhead grid |
| `--sfi` | No | Solar Flux Index (default: 150) |
| `--kp` | No | Kp geomagnetic index (default: 2) |
| `--export` | No | Export anonymized observations to JSON |
| `--encoding` | No | File encoding (default: utf-8) |

### Model Input Requirements

Each QSO must have these fields to be measured against the model:

| Requirement | ADIF Fields Used | If Missing |
|-------------|------------------|------------|
| TX grid | `MY_GRIDSQUARE` or `--my-grid` flag | Skipped (`no_grid`) |
| RX grid | `GRIDSQUARE` | Skipped (`no_grid`) |
| HF band | `BAND` or derived from `FREQ` | Skipped (`no_band`) |

Time (`QSO_DATE`, `TIME_ON`) and mode (`MODE`, `SUBMODE`) are used when
present. If missing, defaults are applied (12:00 UTC, June, Digital mode).

### Example

```bash
ionis-validate adif ki7mt-eqsl-inbox.adi --my-grid DN26
```

Output:

```
======================================================================
  IONIS V20 — ADIF Log Validation
======================================================================

  Log file:      ki7mt-eqsl-inbox.adi
  Your grid:     DN26
  Conditions:    SFI=150.0, Kp=2.0

  Records skipped: 130
    no_grid: 87
    no_band: 42
    bad_grid: 1

  Observations validated: 23,747
  Band open (predicted):  7,108
  Recall:                 29.93%

  Date range:    2009 – 2025

  Recall by Mode:
    CW           37.61%  (2,975 QSOs)
    Digital      98.21%  (4,025 QSOs)
    SSB           7.19%  (2,906 QSOs)
    RTTY         13.20%  (13,841 QSOs)

  Recall by Band:
    160m      5.28%  (776 QSOs)
    80m       8.19%  (891 QSOs)
    40m      30.24%  (5,049 QSOs)
    30m      70.33%  (1,483 QSOs)
    20m      23.11%  (9,183 QSOs)
    17m      63.85%  (899 QSOs)
    15m      27.90%  (3,516 QSOs)
    12m      71.03%  (321 QSOs)
    10m      31.86%  (1,629 QSOs)

  SNR Comparison (3,455 QSOs with signal reports):
    Pearson correlation:  -0.0815
    RMSE:                13.4 dB

======================================================================
  Overall Recall: 29.93% on 23,747 QSOs
======================================================================

  Each QSO is a contact that happened — the band was open.
  Recall measures how often the model agrees.
```

!!! note "Why is recall low with static conditions?"
    The example above uses static SFI=150, Kp=2 for 16 years of QSOs
    (2009-2025). Real conditions varied from deep solar minimum (SFI ~65)
    to solar maximum (SFI ~250+). Per-QSO solar conditions from the
    `solar.bronze` table would improve recall significantly — that
    integration is planned for a future release.

## Exporting Your Log

### From eQSL.cc

1. Log in to [eQSL.cc](https://www.eqsl.cc/)
2. Go to **Log Page** > **Download ADIF File**
3. Select your date range and download
4. Save the `.adi` file

!!! note
    eQSL limits the number of downloadable QSOs. If your inbox is large,
    you may need to download in date-range batches.

### From LoTW (ARRL Logbook of The World)

1. Log in to [LoTW](https://lotw.arrl.org/)
2. Go to **Your Logbook** > **Download Report**
3. Select ADIF format and your date range
4. Save the `.adi` file

### From QRZ.com

1. Log in to [QRZ.com](https://www.qrz.com/)
2. Go to **Logbook** > **Settings** > **Export**
3. Select ADIF format
4. Save the `.adi` file

## Contributing Observations

If you want to share your results to help improve the model:

```bash
ionis-validate adif my_log.adi --my-grid DN26 --export observations.json
```

This creates a JSON file containing **only anonymous observations**:
grid-pair, band, mode, datetime, and predicted SNR. No callsigns, no names,
no personal information.

Review the file before sharing:

```bash
# Verify — should see grid squares, bands, times. No callsigns.
head -20 observations.json
```

Then attach it to a [GitHub Issue](https://github.com/IONIS-AI/ionis-training/issues/new/choose)
using the **Custom Path Results** template.

## Privacy and Compliance

This tool follows the same principles as the IONIS training pipeline, as
documented in our [Ethos](../about/ethos.md) and
[Data Privacy & GDPR](../about/data-privacy.md) statements. There are no
exceptions to that compliance.

**What the parser extracts** (exhaustive list):

- Grid square (yours and theirs) — 4-character Maidenhead locators (~100 x 200 km areas)
- Band and frequency
- Mode (CW, SSB, FT8, etc.)
- UTC date and time
- Signal report (RST/SNR where present)

**What the parser discards** (at parse time, before any processing):

- Callsigns (CALL, STATION_CALLSIGN, MY_CALL, OPERATOR)
- Names, addresses, comments, notes
- QSL messages and eQSL/LoTW metadata
- Every other ADIF field not listed above

| Stage | Contains Callsigns? | Where It Runs |
|-------|---------------------|---------------|
| Your ADIF file (input) | Yes — your log | Your machine |
| Parsed observations | **No** — stripped at parse time | Your machine |
| Report output | **No** — grid-pairs and statistics | Your machine |
| Exported JSON (optional) | **No** — anonymous observations | Your choice to share |

In the IONIS training pipeline, callsigns exist only to resolve a grid
square and are permanently discarded in the silver-to-gold transition. In
ADIF validation, the grid is already in the record — so the callsign is
never needed at all. It is parsed, discarded, and forgotten in the same
function call.

This tool makes no network calls. It reads a local file, runs local
inference, and prints a local report. Nothing leaves your machine unless
you explicitly choose to share the exported JSON.

## Why This Matters

Your log represents real contacts across real propagation paths — ground truth
from your own operating experience. Benefits over other validation data:

- **Mode diversity**: SSB and RTTY QSOs that PSK Reporter barely covers.
- **Historical depth**: Many operators have 10-20 years of logs spanning multiple solar cycles.
- **Explicit opt-in**: You export, you run, you review, you decide to share.

Logs where the model consistently disagrees with your experience are exactly
what we need to improve the next version.
