# Tools Overview

The IONIS pipeline ships **19 CLI tools** across three packages, plus one
external tool used for validation. All pipeline tools use the `ch-go` native
protocol for ClickHouse connectivity with LZ4 compression. The PSK Reporter
collector uses MQTT for real-time spot streaming.

## WSPR Ingestion

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [wspr-turbo](wspr.md#wspr-turbo) | Go | ionis-apps | Streaming .gz → ClickHouse, 22 Mrps (16 workers) |
| [wspr-shredder](wspr.md#wspr-shredder) | Go | ionis-apps | Uncompressed CSV → ClickHouse, 21 Mrps |
| [wspr-parquet-native](wspr.md#wspr-parquet-native) | Go | ionis-apps | Parquet → ClickHouse, 8.4 Mrps |
| [wspr-download](wspr.md#wspr-download) | Go | ionis-apps | Parallel archive downloader from wsprnet.org |

## Solar Pipeline

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [solar-download](solar.md#solar-download) | Go | ionis-apps | Multi-source downloader (10 NOAA/SIDC endpoints) |
| [solar-ingest](solar.md#solar-ingest) | Go | ionis-apps | Solar/geomagnetic data ingester |
| [solar-backfill](solar.md#solar-backfill) | Go | ionis-apps | GFZ Potsdam historical SSN/SFI/Kp (1932–present) |
| [solar-refresh](solar.md#solar-refresh) | Shell | ionis-apps | Download + truncate + ingest pipeline |
| [solar-live-update](solar.md#solar-live-update) | Shell | ionis-apps | Now-Casting updater, 15-min cron |
| [solar-history-load](solar.md#solar-history-load) | Shell | ionis-apps | Training data loader, 6-hour cron |

## Contest & RBN

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [contest-download](contest.md#contest-download) | Go | ionis-apps | CQ/ARRL Cabrillo log downloader (15 contests) |
| [contest-ingest](contest.md#contest-ingest) | Go | ionis-apps | Cabrillo V2/V3 parser → ClickHouse with enrichment |
| [rbn-download](contest.md#rbn-download) | Go | ionis-apps | RBN daily ZIP downloader (2009–present) |
| [rbn-ingest](contest.md#rbn-ingest) | Go | ionis-apps | RBN ZIP → CSV → ClickHouse ingester |

## PSK Reporter

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [pskr-collector](pskr.md#pskr-collector) | Go | ionis-apps | MQTT real-time spot collector → gzip JSONL (~22M spots/day) |

## Database

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [ionis-db-init](database.md#ionis-db-init) | Shell | ionis-core | Initialize ClickHouse schemas (idempotent) |
| [ionis-env](database.md#ionis-env) | Shell | ionis-core | Standardized environment variables (sourceable) |
| [db-validate](database.md#db-validate) | Go | ionis-apps | Validate ClickHouse table row counts |

## CUDA Engine

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [bulk-processor](cuda.md#bulk-processor) | CUDA | ionis-cuda | Float4 embedding generator → wspr.silver |

## Validation (External)

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [voacapl](voacapl.md#voacapl) | Fortran | External (local build) | NTIA/ITS HF propagation prediction engine |
