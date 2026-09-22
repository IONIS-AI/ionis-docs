---
description: >-
  How IONIS ingests 14 billion radio observations from WSPR, RBN, contest logs,
  and PSK Reporter into ClickHouse at 22 million rows per second using custom
  Go binaries with native protocol and LZ4 compression.
---

# Data Pipeline

## WSPR Ingestion

**Source**: 10.94B WSPR spots from [wsprnet.org](https://wsprnet.org) CSV archives

| Tool | Method | Throughput |
|------|--------|------------|
| `wspr-turbo` | Streaming .gz → ClickHouse | 22.55 Mrps (16 workers) |
| `wspr-shredder` | Raw CSV → ClickHouse | 21.81 Mrps |

All ingesters normalize band via `bands.GetBand(freqMHz)` — single source of truth.

### Band IDs (ADIF)

| ID | Band | ID | Band |
|----|------|----|------|
| 102 | 160m | 108 | 17m |
| 103 | 80m | 109 | 15m |
| 104 | 60m | 110 | 12m |
| 105 | 40m | 111 | 10m |
| 106 | 30m | | |
| 107 | 20m | | |

## Solar Pipeline

**Source**: [GFZ Potsdam](https://kp.gfz-potsdam.de/) (SSN, SFI, Kp) — ~17,840 rows, 2000-2026

| Tool | Schedule | Purpose |
|------|----------|---------|
| `solar-live-update` | 15-min cron | Real-time NOAA/SIDC |
| `solar-history-load` | 6-hour cron | Historical backfill |
| `solar-backfill` | Manual | GFZ Potsdam 1932–present |

### Kp Alignment

WSPR spots are aligned with Kp values using 3-hour bucket JOINs:

```sql
intDiv(toHour(timestamp), 3)
```

This matches the Kp publication cadence from GFZ Potsdam.

## CUDA Signature Engine

Generates float4 embeddings from WSPR+solar data:

- **Input**: `wspr.bronze` + `solar.bronze`
- **Output**: none at present — `wspr.silver` was dropped 2026-09-22
- **Throughput**: 4.43B embeddings in 45m13s (2026-02-07 QA run)

!!! warning "Not part of the pipeline"
    This engine is unpackaged, hand-run, and has no consumer. No gold or signatures table
    derives from it; every one of them reads `wspr.bronze` directly. See
    [Silver Layer](silver_layer.md) for the retirement note.

## RBN Ingestion

**Source**: 2.26B [Reverse Beacon Network](https://reversebeacon.net) spots from daily ZIP archives (2009-02-21 to 2026)

| Tool | Method | Throughput |
|------|--------|------------|
| `rbn-download` | Daily ZIP download → `/mnt/rbn-data` | 6,183 daily files |
| `rbn-ingest` | CSV → ClickHouse (`rbn.bronze`) | 2.26B rows in 3m35s (10.15 Mrps) |

- **Archive**: `https://data.reversebeacon.net/rbn_history/YYYYMMDD.zip`
- **Size**: ~21 GB compressed, ~135 GB uncompressed
- **Format**: CSV, 13 columns: `callsign, de_pfx, de_cont, freq, band, dx, dx_pfx, dx_cont, mode, db, date, speed, tx_mode`
- **Limitation**: No grid squares for transmitters — requires callsign-to-grid mapping (Rosetta Stone)
- **Grid coverage**: 525.8M spots geocoded (24.07%) via `wspr.callsign_grid`; 121,307 of 2.12M unique DX callsigns matched (5.71%)
- Zero failures, zero skipped rows on full ingest

## Contest Log Ingestion

**Source**: 491K [Cabrillo](https://wwrof.org/cabrillo/) log files across 15 contests (CQ + ARRL, 2005-2025)

| Tool | Method | Throughput |
|------|--------|------------|
| `contest-download` | Index scrape + hash-based download → `/mnt/contest-logs` | 491K files, 3.5 GB |
| `contest-ingest` | Cabrillo V2/V3 parser → ClickHouse (`contest.bronze`) | 234M QSOs |

### Contests Downloaded

| Source | Contests | Years | Files |
|--------|----------|-------|-------|
| **CQ** | WW, WPX, WPX-RTTY, WW-RTTY, 160, WW-Digi | 2005-2025 | ~120 log sets |
| **ARRL** | DX CW/Ph, SS CW/Ph, 10m, 160m, RTTY, Digi, IARU HF | 2018-2025 | ~475K logs |

- **Format**: Cabrillo v2 and v3 (parser handles both)
- **Bonus**: 98.5% of ARRL logs include `HQ-GRID-LOCATOR` header — free grid squares
- **Limitation**: Signal reports useless (always 59/599) except digital contests
- **Download etiquette**: Rate limited (2-3s delays), max 3 concurrent ARRL streams

## Propagation Data Sources

Four pillars of propagation truth, each on a dedicated ZFS dataset:

| Source | Tool | Volume | Modes | Grid Quality |
|--------|------|--------|-------|-------------|
| **WSPR** | `wspr-turbo` | 10.94B spots | WSPR only | 4-char [Maidenhead](https://en.wikipedia.org/wiki/Maidenhead_Locator_System) |
| **RBN** | `rbn-ingest` | 2.26B spots | CW, RTTY | DXCC prefix only (24% geocoded via Rosetta Stone) |
| **Contest Logs** | `contest-ingest` | 234M QSOs (491K files) | CW/SSB/RTTY/Digi | HQ-GRID-LOCATOR (98.5% ARRL) + callsign lookup |
| **PSK Reporter** | `pskr-collector` | ~26M HF spots/day (live since 2026-02-10) | FT8/FT4/WSPR/JS8/CW | 4-6 char Maidenhead |

### PSK Reporter (Forward Collection — Active)

Created by **Philip Gladstone, N1DQ**. MQTT feed provided by **Tom Sevart, M0LTE**.

- **No bulk archive exists** — forward-only, collection started 2026-02-09
- **MQTT firehose** at `mqtt.pskreporter.info:1883` (~26M HF spots/day)
- **Best data quality**: machine-decoded SNR, 4-6 char grids, multi-mode
- **Collection tool**: `pskr-collector` — Go MQTT subscriber → hourly-rotated gzip JSONL → `/mnt/pskr-data`
- **Running as systemd service** since 2026-02-10 (~19 bytes/spot compressed, ~15 GB/year)
- **Observed throughput**: ~300 HF spots/sec sustained, all 10 HF bands
- **Mode mix**: 88.7% FT8, 9.1% WSPR, 1.5% FT4, 0.5% JS8
- **Grid coverage**: 28% receiver grids, 15% sender grids (per-spot)
- **Dual purpose**: Training feed for future models + validation feed for live scoring
- **Stage 2** (live): `pskr-ingest` JSONL → ClickHouse `pskr.bronze` (hourly cron, watermark-tracked via `pskr.ingest_log`)

## Storage Layout (9975WX)

### ZFS Archive Pool

7.12 TB mirrored Samsung 990 Pro on `archive-pool`:

| Dataset | Mountpoint | Compression | Purpose |
|---------|------------|-------------|---------|
| `archive-pool` | `/mnt/archive-pool` | — | Pool root (unused) |
| `archive-pool/wspr-data` | `/mnt/wspr-data` | lz4 | WSPR raw CSV archives (.csv.gz) |
| `archive-pool/contest-logs` | `/mnt/contest-logs` | zstd-9 | CQ + ARRL Cabrillo logs |
| `archive-pool/rbn-data` | `/mnt/rbn-data` | lz4 | RBN daily ZIP archives |
| `archive-pool/pskr-data` | `/mnt/pskr-data` | lz4 | PSK Reporter MQTT collection (pre-compressed gzip) |

**Compression rationale**:

- `zstd-9` for text data (Cabrillo logs) — 10-20x compression ratio
- `lz4` for pre-compressed archives (RBN ZIPs, PSK Reporter gzip JSONL) — near-zero CPU overhead on incompressible data

Each dataset can be independently snapshotted, replicated (`zfs send`), and quota'd.

### NVMe Layout

| Mount | Device | Purpose |
|-------|--------|---------|
| `/mnt/ai-stack` | NVMe | Source code, working data |
| `/var/lib/clickhouse` | NVMe (separate) | ClickHouse storage (3.7T, I/O decoupled) |

## ClickHouse Tables

Measured against `10.60.1.1` on **2026-09-22**. Counts move; the lineage in
`ionis-core/docs/DATA-DICTIONARY.md` does not, and that file is authoritative for what each
table is and what derives it.

| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| `wspr.bronze` | 12.68 billion | 225.67 GiB | Raw WSPR spots — wsprnet CSV archives + `wspr.live` |
| `pskr.bronze` | 7.10 billion | 96.81 GiB | Raw PSK Reporter reception spots (MQTT, since 2026-02-10) |
| `rbn.bronze` | 2.37 billion | 48.38 GiB | Raw RBN CW/RTTY skimmer spots |
| `contest.bronze` | 234.28 million | 4.11 GiB | Parsed contest QSOs from Cabrillo logs |
| `solar.iri_lookup` | 319.46 million | 3.60 GiB | Pre-computed IRI ionospheric model output |
| `wspr.signatures_v2_terrestrial` | 93.60 million | 2.25 GiB | Aggregated signatures, balloon-filtered — **the training source** |
| `wspr.signatures_v1` | 93.62 million | 2.20 GiB | Aggregated signatures from bronze ⋈ solar |
| `rbn.signatures` | 67.35 million | 1.28 GiB | RBN signatures from bronze ⋈ solar |
| `wspr.gold_v6` | 10.00 million | 238.92 MiB | V6 training set (continuous + kp_penalty) |
| `wspr.gold_continuous` | 10.00 million | 218.02 MiB | IFW-weighted training set |
| `wspr.gold_stratified` | 10.00 million | 167.42 MiB | SSN-stratified training set |
| `pskr.signatures` | 8.45 million | 145.18 MiB | PSKR signatures — **covers month 2 of 8 collected; regeneration pending** |
| `contest.signatures` | 5.74 million | 90.33 MiB | Contest signatures from bronze ⋈ solar |
| `wspr.callsign_grid` | 3.68 million | 58.88 MiB | Rosetta Stone: callsign → grid lookup |
| `solar.dscovr` | 226.59 thousand | 6.60 MiB | DSCOVR/ACE L1 solar wind, 1-minute |
| `solar.bronze` | 78.33 thousand | 901.57 KiB | SSN, SFI, Kp — daily / 3-hourly |
