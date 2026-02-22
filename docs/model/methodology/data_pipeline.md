---
description: >-
  How IONIS ingests 13 billion radio observations from WSPR, RBN, contest logs,
  and PSK Reporter into ClickHouse at 22 million rows per second using custom
  Go binaries with native protocol and LZ4 compression.
---

# Data Pipeline

## WSPR Ingestion

**Source**: 10.8B WSPR spots from [wsprnet.org](https://wsprnet.org) CSV archives

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
- **Output**: `wspr.silver` (4.4B embeddings, 41 GiB)
- **Throughput**: 4.43B embeddings in 45m13s

## RBN Ingestion

**Source**: 2.18B [Reverse Beacon Network](https://reversebeacon.net) spots from daily ZIP archives (2009-02-21 to 2025)

| Tool | Method | Throughput |
|------|--------|------------|
| `rbn-download` | Daily ZIP download → `/mnt/rbn-data` | 6,183 daily files |
| `rbn-ingest` | CSV → ClickHouse (`rbn.bronze`) | 2.18B rows in 3m35s (10.15 Mrps) |

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
| `contest-ingest` | Cabrillo V2/V3 parser → ClickHouse (`contest.bronze`) | 195M QSOs |

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
| **WSPR** | `wspr-turbo` | 10.8B spots | WSPR only | 4-char [Maidenhead](https://en.wikipedia.org/wiki/Maidenhead_Locator_System) |
| **RBN** | `rbn-ingest` | 2.18B spots | CW, RTTY | DXCC prefix only (24% geocoded via Rosetta Stone) |
| **Contest Logs** | `contest-ingest` | 195M QSOs (491K files) | CW/SSB/RTTY/Digi | HQ-GRID-LOCATOR (98.5% ARRL) + callsign lookup |
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

| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| `wspr.bronze` | 10.8B | 191 GiB | Raw WSPR spots |
| `rbn.bronze` | 2.18B | 45.3 GiB | Raw RBN CW/RTTY spots |
| `contest.bronze` | 234.3M | 4.1 GiB | Parsed contest QSOs (15 contests) |
| `wspr.silver` | 4.4B | 41 GiB | CUDA float4 embeddings |
| `wspr.signatures_v2_terrestrial` | 93.6M | 2.3 GiB | Aggregated signatures (training source, balloon-filtered) |
| `wspr.callsign_grid` | 38.6K | — | Rosetta Stone: callsign → grid lookup |
| `wspr.gold_continuous` | 10M | 218 MiB | IFW-weighted training set |
| `wspr.gold_stratified` | 10M | 167 MiB | SSN-stratified training set |
| `wspr.gold_v6` | 10M | 240 MiB | V6 training set (continuous + kp_penalty) |
| `pskr.bronze` | — | — | PSK Reporter reception spots (accumulating) |
| `solar.bronze` | 17.8K | 868 KiB | SSN, SFI, Kp daily/3-hourly |
