# Tools Overview

The IONIS pipeline ships **18 CLI tools** across three packages, plus one
external tool used for validation. All pipeline tools use the `ch-go` native
protocol for ClickHouse connectivity with LZ4 compression.

## WSPR Ingestion

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [wspr-turbo](wspr.md#wspr-turbo) | Go | ki7mt-ai-lab-apps | Streaming .gz → ClickHouse, 22 Mrps (16 workers) |
| [wspr-shredder](wspr.md#wspr-shredder) | Go | ki7mt-ai-lab-apps | Uncompressed CSV → ClickHouse, 21 Mrps |
| [wspr-parquet-native](wspr.md#wspr-parquet-native) | Go | ki7mt-ai-lab-apps | Parquet → ClickHouse, 8.4 Mrps |
| [wspr-download](wspr.md#wspr-download) | Go | ki7mt-ai-lab-apps | Parallel archive downloader from wsprnet.org |

## Solar Pipeline

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [solar-download](solar.md#solar-download) | Go | ki7mt-ai-lab-apps | Multi-source downloader (10 NOAA/SIDC endpoints) |
| [solar-ingest](solar.md#solar-ingest) | Go | ki7mt-ai-lab-apps | Solar/geomagnetic data ingester |
| [solar-backfill](solar.md#solar-backfill) | Go | ki7mt-ai-lab-apps | GFZ Potsdam historical SSN/SFI/Kp (1932–present) |
| [solar-refresh](solar.md#solar-refresh) | Shell | ki7mt-ai-lab-core | Download + truncate + ingest pipeline |
| [solar-live-update](solar.md#solar-live-update) | Shell | ki7mt-ai-lab-core | Now-Casting updater, 15-min cron |
| [solar-history-load](solar.md#solar-history-load) | Shell | ki7mt-ai-lab-core | Training data loader, 6-hour cron |

## Contest & RBN

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [contest-download](contest.md#contest-download) | Go | ki7mt-ai-lab-apps | CQ/ARRL Cabrillo log downloader (15 contests) |
| [contest-ingest](contest.md#contest-ingest) | Go | ki7mt-ai-lab-apps | Cabrillo V2/V3 parser → ClickHouse with enrichment |
| [rbn-download](contest.md#rbn-download) | Go | ki7mt-ai-lab-apps | RBN daily ZIP downloader (2009–present) |
| [rbn-ingest](contest.md#rbn-ingest) | Go | ki7mt-ai-lab-apps | RBN ZIP → CSV → ClickHouse ingester |

## Database

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [ki7mt-lab-db-init](database.md#ki7mt-lab-db-init) | Shell | ki7mt-ai-lab-core | Initialize ClickHouse schemas (idempotent) |
| [ki7mt-lab-env](database.md#ki7mt-lab-env) | Shell | ki7mt-ai-lab-core | Standardized environment variables (sourceable) |
| [db-validate](database.md#db-validate) | Go | ki7mt-ai-lab-apps | Validate ClickHouse table row counts |

## CUDA Engine

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [bulk-processor](cuda.md#bulk-processor) | CUDA | ki7mt-ai-lab-cuda | Float4 embedding generator → wspr.silver |

## Validation (External)

| Tool | Type | Package | Description |
|------|------|---------|-------------|
| [voacapl](voacapl.md#voacapl) | Fortran | External (local build) | NTIA/ITS HF propagation prediction engine |
