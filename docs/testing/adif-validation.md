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
4. Each QSO is run through the V20 model as a validation path
5. The report shows recall: how often the model agrees the band was open

Every QSO in your log is a confirmed contact — the band **was** open.
Recall measures how often the model agrees.

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

### Example

```bash
ionis-validate adif eqsl_export.adi --my-grid DN26 --sfi 140
```

Output:

```
  IONIS V20 — ADIF Log Validation
======================================================================

  Log file:      eqsl_export.adi
  Your grid:     DN26
  Conditions:    SFI=140, Kp=2.0

  Observations validated: 12,847
  Band open (predicted):  11,493
  Recall:                 89.47%

  Date range:    2018 – 2025

  Recall by Mode:
    Digital     93.21%  (8,412 QSOs)
    CW          88.76%  (2,103 QSOs)
    SSB         81.34%  (1,890 QSOs)
    RTTY        90.52%  (442 QSOs)

  Recall by Band:
    160m    62.14%  (215 QSOs)
    80m     71.88%  (1,024 QSOs)
    40m     85.92%  (3,412 QSOs)
    20m     94.23%  (4,891 QSOs)
    15m     96.01%  (2,103 QSOs)
    10m     93.47%  (1,202 QSOs)

======================================================================
  Overall Recall: 89.47% on 12,847 confirmed QSOs
======================================================================

  Every QSO in your log is a confirmed contact — the band WAS open.
  Recall measures how often the model agrees.
```

## Exporting Your Log

### From eQSL.cc

1. Log in to [eQSL.cc](https://www.eqsl.cc/)
2. Go to **Log Page** > **Download ADIF File**
3. Select your date range and download
4. Save the `.adi` file

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

Your log represents **confirmed two-way contacts** — stronger ground truth
than one-way reception reports. Benefits over other validation data:

- **Confirmed communication**: Both stations copied each other. The band was unambiguously open.
- **Mode diversity**: SSB and RTTY QSOs that PSK Reporter barely covers.
- **Historical depth**: Many operators have 10-20 years of logs spanning multiple solar cycles.
- **Explicit opt-in**: You export, you run, you review, you decide to share.

Logs where the model consistently disagrees with your experience are exactly
what we need to improve the next version.
