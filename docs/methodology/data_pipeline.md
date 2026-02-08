# Data Pipeline

## WSPR Ingestion

**Source**: 10.8B WSPR spots from wsprnet.org CSV archives

| Tool | Method | Throughput |
|------|--------|------------|
| `wspr-turbo` | Streaming .gz → ClickHouse | 24.67 Mrps (24 workers) |
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

**Source**: GFZ Potsdam (SSN, SFI, Kp) — 76,248 rows, 2000–2026

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

- **Input**: `wspr.spots_raw` + `solar.indices_raw`
- **Output**: `wspr.model_features` (4.4B embeddings, 41 GiB)
- **Throughput**: 4.43B embeddings in 45m13s

## RBN Ingestion

**Source**: 2.18B Reverse Beacon Network spots from daily ZIP archives (2009-02-21 to 2025)

| Tool | Method | Throughput |
|------|--------|------------|
| `rbn-download` | Daily ZIP download → `/mnt/rbn-data` | 6,183 daily files |
| `rbn-ingest` | CSV → ClickHouse (`rbn.spots_raw`) | 2.18B rows in 3m32s (10.32 Mrps) |

- **Archive**: `https://data.reversebeacon.net/rbn_history/YYYYMMDD.zip`
- **Size**: ~21 GB compressed, ~135 GB uncompressed
- **Format**: CSV, 13 columns: `callsign, de_pfx, de_cont, freq, band, dx, dx_pfx, dx_cont, mode, db, date, speed, tx_mode`
- **Limitation**: No grid squares for transmitters — requires callsign-to-grid mapping (Rosetta Stone)
- **Grid coverage**: 525.8M spots geocoded (24.07%) via `wspr.callsign_grid`; 121,307 of 2.12M unique DX callsigns matched (5.71%)
- Zero failures, zero skipped rows on full ingest

## Contest Log Ingestion

**Source**: 459K Cabrillo log files across 15 contests (CQ + ARRL, 2005-2025)

| Tool | Method | Throughput |
|------|--------|------------|
| `contest-download` | Index scrape + hash-based download → `/mnt/contest-logs` | 459K files, 3.3 GB |
| `contest-ingest` | Cabrillo V2/V3 parser → ClickHouse (`contest.qsos`) | 195M QSOs |

### Contests Downloaded

| Source | Contests | Years | Files |
|--------|----------|-------|-------|
| **CQ** | WW, WPX, WPX-RTTY, WW-RTTY, 160, WW-Digi | 2005-2025 | ~120 log sets |
| **ARRL** | DX CW/Ph, SS CW/Ph, 10m, 160m, RTTY, Digi, IARU HF | 2018-2025 | ~459K logs |

- **Format**: Cabrillo v2 and v3 (parser handles both)
- **Bonus**: 98.5% of ARRL logs include `HQ-GRID-LOCATOR` header — free grid squares
- **Limitation**: Signal reports useless (always 59/599) except digital contests
- **Download etiquette**: Rate limited (2-3s delays), max 3 concurrent ARRL streams

## Propagation Data Sources

Three pillars of propagation truth, each on a dedicated ZFS dataset:

| Source | Tool | Volume | Modes | Grid Quality |
|--------|------|--------|-------|-------------|
| **WSPR** | `wspr-turbo` | 10.8B spots | WSPR only | 4-char Maidenhead |
| **RBN** | `rbn-ingest` | 2.18B spots | CW, RTTY | DXCC prefix only (24% geocoded via Rosetta Stone) |
| **Contest Logs** | `contest-ingest` | 195M QSOs (459K files) | CW/SSB/RTTY/Digi | HQ-GRID-LOCATOR (98.5% ARRL) + callsign lookup |
| **PSK Reporter** | `pskr-collector` (planned) | ~30-50M/day | FT8/FT4/CW | 6-8 char Maidenhead |

### PSK Reporter (Future — Forward Collection Only)

- **No bulk archive exists** — 24-hour API lookback max
- **MQTT firehose** at `mqtt.pskreporter.info` (~30-50M spots/day)
- **Best data quality**: real SNR, 6-8 char grids, multi-mode
- **Collection tool**: Go MQTT listener → ClickHouse (planned)

## Storage Layout (9975WX)

### ZFS Archive Pool

7.12 TB mirrored Samsung 990 Pro on `archive-pool`:

| Dataset | Mountpoint | Compression | Purpose |
|---------|------------|-------------|---------|
| `archive-pool` | `/mnt/archive-pool` | — | Pool root (unused) |
| `archive-pool/wspr-data` | `/mnt/wspr-data` | lz4 | WSPR raw CSV archives (.csv.gz) |
| `archive-pool/contest-logs` | `/mnt/contest-logs` | zstd-9 | CQ + ARRL Cabrillo logs |
| `archive-pool/rbn-data` | `/mnt/rbn-data` | lz4 | RBN daily ZIP archives |
| `archive-pool/pskr-data` | `/mnt/pskr-data` | zstd-9 | PSK Reporter MQTT collection |

**Compression rationale**:

- `zstd-9` for text data (Cabrillo, JSON) — 10-20x compression ratio
- `lz4` for pre-compressed ZIPs (RBN) — near-zero CPU overhead, slight metadata savings

Each dataset can be independently snapshotted, replicated (`zfs send`), and quota'd.

### NVMe Layout

| Mount | Device | Purpose |
|-------|--------|---------|
| `/mnt/ai-stack` | NVMe | Source code, working data |
| `/var/lib/clickhouse` | NVMe (separate) | ClickHouse storage (3.7T, I/O decoupled) |

## ClickHouse Tables

| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| `wspr.spots_raw` | 10.8B | 191 GiB | Raw WSPR spots |
| `rbn.spots_raw` | 2.18B | 45.3 GiB | Raw RBN CW/RTTY spots |
| `contest.qsos` | 195M | 3.4 GiB | Parsed contest QSOs (15 contests) |
| `wspr.model_features` | 4.4B | 41 GiB | CUDA float4 embeddings |
| `wspr.signatures_v1` | 93.8M | 2.3 GiB | Aggregated signatures (V12 training source) |
| `wspr.callsign_grid` | 3.6M | 58 MiB | Rosetta Stone: callsign → grid lookup |
| `wspr.training_continuous` | 10M | 218 MiB | IFW-weighted training set |
| `wspr.training_stratified` | 10M | 167 MiB | SSN-stratified training set |
| `solar.indices_raw` | 76K | 868 KiB | SSN, SFI, Kp daily/3-hourly |
