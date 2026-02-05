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

## ClickHouse Tables

| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| `wspr.spots_raw` | 10.8B | 191 GiB | Raw WSPR spots |
| `wspr.model_features` | 4.4B | 41 GiB | CUDA embeddings |
| `wspr.training_continuous` | 10M | — | IFW-weighted training set |
| `solar.indices_raw` | 76K | — | SSN, SFI, Kp daily/3-hourly |
