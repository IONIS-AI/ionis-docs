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

## Propagation Data Sources

Three pillars of propagation truth, each on a dedicated ZFS dataset:

| Source | Tool | Volume | Modes | Grid Quality |
|--------|------|--------|-------|-------------|
| **WSPR** | `wspr-turbo` | 10.8B spots | WSPR only | 4-char Maidenhead |
| **RBN** | `rbn-download` | ~2.2B spots | CW, RTTY | DXCC prefix only |
| **CQ Contests** | `contest-download` | ~120 log sets | CW/SSB/RTTY/Digi | Callsign lookup needed |
| **PSK Reporter** | `pskr-collector` (planned) | ~30-50M/day | FT8/FT4/CW | 6-8 char Maidenhead |

### RBN (Reverse Beacon Network)

- **Archive**: `https://data.reversebeacon.net/rbn_history/YYYYMMDD.zip`
- **Range**: 2009-02-21 to present (~6,183 daily files)
- **Size**: ~21 GB compressed, ~135 GB uncompressed
- **Format**: CSV, 13 columns: `callsign, de_pfx, de_cont, freq, band, dx, dx_pfx, dx_cont, mode, db, date, speed, tx_mode`
- **Limitation**: No grid squares — needs callsign-to-grid mapping

### CQ Contest Logs (Cabrillo)

- **Sources**: CQ WW, CQ WPX, CQ WW RTTY, CQ WPX RTTY, CQ 160, WW Digi
- **Range**: 2005-2025 (varies by contest)
- **Format**: Cabrillo v2 and v3 (parser must handle both)
- **Limitation**: Signal reports useless (always 59/599) except digi (real SNR)

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
| `archive-pool` | `/mnt/wspr-archive` | zstd | WSPR raw CSV archives |
| `archive-pool/contest-logs` | `/mnt/contest-logs` | zstd-9 | CQ contest Cabrillo logs |
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
| `wspr.model_features` | 4.4B | 41 GiB | CUDA embeddings |
| `wspr.training_continuous` | 10M | — | IFW-weighted training set |
| `solar.indices_raw` | 76K | — | SSN, SFI, Kp daily/3-hourly |
