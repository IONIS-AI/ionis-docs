# Reproducing the Bronze Stack

This guide documents every step needed to reproduce the full IONIS bronze layer — raw data loaded into ClickHouse from source archives on ZFS — from a clean slate.

## Overview

The "bronze stack" is the set of ClickHouse tables containing raw and lightly transformed data. All tables are reproducible from source archives stored on ZFS, using deterministic DDL and population scripts from `ki7mt-ai-lab-core`.

**Current state** (2026-02-07):

| Database | Tables | Total Rows | Total Size |
|----------|--------|------------|------------|
| `wspr` | 10 (+ 2 views, 1 MV) | 15.4B | 236 GiB |
| `rbn` | 1 | 2.18B | 45.3 GiB |
| `contest` | 1 | 225.7M | 3.9 GiB |
| `solar` | 1 (+ 1 view) | 76.5K | 868 KiB |
| `data_mgmt` | 2 | — | — |
| `geo` | 0 (+ 1 view) | — | — |

## Prerequisites

1. **ClickHouse** running on the target host (default `192.168.1.90`)
2. **ZFS datasets** mounted:
    - `/mnt/wspr-data` — WSPR raw CSV archives (.csv.gz)
    - `/mnt/contest-logs` — CQ + ARRL Cabrillo log files
    - `/mnt/rbn-data` — RBN daily ZIP archives
3. **RPM packages** installed (v2.2.0+):
    - `ki7mt-ai-lab-core` — DDL schemas and population scripts
    - `ki7mt-ai-lab-apps` — Go ingesters (wspr-turbo, rbn-ingest, contest-ingest, solar-backfill)
    - `ki7mt-ai-lab-cuda` — bulk-processor (CUDA signature engine)

## DDL Application Order

All DDL files live in `ki7mt-ai-lab-core/src/` and must be applied in numerical order. Each file is idempotent (`CREATE TABLE IF NOT EXISTS`).

```bash
for f in ki7mt-ai-lab-core/src/*.sql; do
    echo "Applying: $f"
    clickhouse-client --multiquery < "$f"
done
```

| # | File | Database | Creates |
|---|------|----------|---------|
| 01 | `wspr_schema_v2.sql` | wspr | `spots_raw`, `v_schema_contract`, `v_data_integrity` |
| 02 | `solar_indices.sql` | solar | `indices_raw` |
| 03 | `solar_silver.sql` | solar | `v_daily_indices` |
| 04 | `data_mgmt.sql` | data_mgmt | `config` |
| 05 | `geo_functions.sql` | geo | `v_grid_validation_example` |
| 06 | `lab_versions.sql` | data_mgmt | `lab_versions`, `v_lab_versions_latest` |
| 07 | `callsign_grid.sql` | wspr | `callsign_grid` |
| 08 | `model_features.sql` | wspr | `model_features` |
| 09 | `quality_distribution_mv.sql` | wspr | `v_quality_distribution` (MV) |
| 10 | `rbn_schema_v1.sql` | rbn | `spots_raw` |
| 11 | `contest_schema_v1.sql` | contest | `qsos` |
| 12 | `signatures_v1.sql` | wspr | `signatures_v1` |
| 13 | `training_stratified.sql` | wspr | `training_stratified` |
| 14 | `training_continuous.sql` | wspr | `training_continuous` |
| 15 | `training_v6_clean.sql` | wspr | `training_v6_clean` |

!!! note "DDL 09 depends on DDL 08"
    The `v_quality_distribution` materialized view reads from `model_features`. DDL 08 must be applied first.

## Bronze Tables

These are the primary data tables populated directly from source archives.

### `wspr.spots_raw` — 10.8B rows, 191 GiB

Raw WSPR spot records from wsprnet.org CSV archives.

- **Source**: `/mnt/wspr-data/*.csv.gz`
- **Tool**: `wspr-turbo` (streaming .gz parser, 24.67 Mrps with 24 workers)
- **Command**: `wspr-turbo --host 192.168.1.90 --workers 24 /mnt/wspr-data`
- **Wall time**: ~7m30s on 9975WX

```sql
-- Verification
SELECT count() FROM wspr.spots_raw;
-- Expected: ~10,800,000,000

SELECT uniq(band) FROM wspr.spots_raw WHERE band BETWEEN 102 AND 111;
-- Expected: 10 (all HF bands)
```

### `solar.indices_raw` — 76.5K rows, 868 KiB

Daily/3-hourly SSN, SFI, and Kp from GFZ Potsdam (2000–present).

- **Source**: GFZ Potsdam FTP (downloaded by tool)
- **Tool**: `solar-backfill`
- **Command**: `solar-backfill --host 192.168.1.90`
- **Wall time**: <1s

```sql
-- Verification
SELECT count() FROM solar.indices_raw;
-- Expected: ~76,500

SELECT min(date), max(date) FROM solar.indices_raw;
-- Expected: 2000-01-01 to ~today
```

### `rbn.spots_raw` — 2.18B rows, 45.3 GiB

Reverse Beacon Network CW/RTTY spots from daily ZIP archives.

- **Source**: `/mnt/rbn-data/*.zip`
- **Tool**: `rbn-ingest`
- **Command**: `rbn-ingest --host 192.168.1.90 /mnt/rbn-data`
- **Wall time**: ~3m30s (10.32 Mrps)

```sql
-- Verification
SELECT count() FROM rbn.spots_raw;
-- Expected: ~2,180,000,000
```

### `contest.qsos` — 225.7M rows, 3.9 GiB

Parsed QSO records from CQ and ARRL Cabrillo log files.

- **Source**: `/mnt/contest-logs/` (475K files across 15 contests)
- **Tool**: `contest-ingest`
- **Command**: `contest-ingest --host 192.168.1.90 /mnt/contest-logs`
- **Wall time**: ~5 min

```sql
-- Verification
SELECT count() FROM contest.qsos;
-- Expected: ~225,700,000

SELECT contest, count() FROM contest.qsos GROUP BY contest ORDER BY count() DESC;
```

### `wspr.callsign_grid` — 3.6M rows, 58 MiB

Callsign-to-grid Rosetta Stone derived from WSPR TX/RX data.

- **Source**: `wspr.spots_raw` (derived)
- **Tool**: `contest-ingest --enrich` (or manual SQL — see commented section in `07-callsign_grid.sql`)
- **Wall time**: ~2 min

```sql
-- Verification
SELECT count() FROM wspr.callsign_grid FINAL;
-- Expected: ~3,600,000
```

### `wspr.model_features` — 4.4B rows, 41 GiB

Float4 embeddings generated by the CUDA bulk-processor from spots + solar data.

- **Source**: `wspr.spots_raw` + `solar.indices_raw` (derived)
- **Tool**: `bulk-processor` (CUDA, RTX PRO 6000)
- **Command**: `bulk-processor --host 192.168.1.90`
- **Wall time**: ~45 min on 9975WX

!!! warning "Requires NVIDIA GPU"
    The bulk-processor requires an NVIDIA GPU with sufficient VRAM. The RTX PRO 6000 (96 GB) processes all 10.8B spots in a single pass.

```sql
-- Verification
SELECT count() FROM wspr.model_features;
-- Expected: ~4,430,000,000
```

## Derived Tables

These tables are built from bronze tables using SQL queries or population scripts in `ki7mt-ai-lab-core/scripts/`.

### `wspr.signatures_v1` — 93.8M rows, 2.3 GiB

Median-bucketed WSPR signatures — 115:1 compression from raw spots.

- **Prerequisites**: `wspr.spots_raw`, `solar.indices_raw`
- **Script**: `scripts/populate_signatures.sh`
- **Command**: `bash populate_signatures.sh` (or `CH_HOST=10.60.1.1 bash populate_signatures.sh`)
- **Wall time**: ~3 min 10s on 9975WX

```sql
-- Verification
SELECT count() FROM wspr.signatures_v1;
-- Expected: ~93,800,000
```

### `wspr.training_stratified` — 10M rows, 167 MiB

SSN-stratified training set (200K per band x quintile).

- **Prerequisites**: `wspr.spots_raw`, `solar.indices_raw`
- **Script**: `scripts/populate_stratified.sh`
- **Command**: `bash populate_stratified.sh`
- **Wall time**: ~10 min

```sql
SELECT count() FROM wspr.training_stratified;
-- Expected: 10,000,000
```

### `wspr.training_continuous` — 10M rows, 218 MiB

IFW-weighted training set (1M per band, Efraimidis-Spirakis sampling).

- **Prerequisites**: `wspr.spots_raw`, `solar.indices_raw`
- **Script**: `scripts/populate_continuous.sh`
- **Command**: `bash populate_continuous.sh`
- **Wall time**: ~15 min

```sql
SELECT count() FROM wspr.training_continuous;
-- Expected: 10,000,000
```

### `wspr.training_v6_clean` — 10M rows, 240 MiB

Phase 6 training set: `training_continuous` + `kp_penalty` constraint column.

- **Prerequisites**: `wspr.training_continuous` (must be populated first)
- **Script**: `scripts/populate_v6_clean.sh`
- **Command**: `bash populate_v6_clean.sh`
- **Wall time**: <30s

```sql
SELECT count() FROM wspr.training_v6_clean;
-- Expected: 10,000,000

-- Verify kp_penalty range
SELECT min(kp_penalty), max(kp_penalty) FROM wspr.training_v6_clean;
-- Expected: ~0.0 to 1.0
```

### `wspr.v_quality_distribution` (Materialized View)

Automatically populated as rows are inserted into `wspr.model_features`. No manual population needed.

```sql
SELECT count() FROM wspr.v_quality_distribution;
-- Expected: ~6,100,000
```

## Full Stack Build Order

To reproduce the entire bronze stack from scratch:

```text
Phase 1: DDL
  Apply all ki7mt-ai-lab-core/src/*.sql in order (01-15)

Phase 2: Bronze Ingest (independent, can run in parallel)
  2a. solar-backfill           →  solar.indices_raw        (~1s)
  2b. wspr-turbo               →  wspr.spots_raw           (~7m30s)
  2c. rbn-ingest               →  rbn.spots_raw            (~3m30s)
  2d. contest-ingest           →  contest.qsos             (~5m)

Phase 3: Derived from spots_raw + solar (sequential)
  3a. bulk-processor (CUDA)    →  wspr.model_features      (~45m)
      (also auto-populates v_quality_distribution via MV)
  3b. callsign_grid population →  wspr.callsign_grid       (~2m)
  3c. populate_signatures.sh   →  wspr.signatures_v1       (~3m)

Phase 4: Training tables (sequential)
  4a. populate_stratified.sh   →  wspr.training_stratified (~10m)
  4b. populate_continuous.sh   →  wspr.training_continuous  (~15m)
  4c. populate_v6_clean.sh     →  wspr.training_v6_clean   (<30s)
```

**Total wall time**: ~1h30m on 9975WX (Threadripper 9975WX, 128 GB DDR5, RTX PRO 6000)

## Training Table Lineage

!!! info "V1–V5 were iterative development tables"
    Training tables V1 through V5 were development/testing iterations that did not survive:

    - **V1** (`training_set_v1`): First attempt at gold-standard dataset from `model_features`. Dropped — solar backfill didn't exist yet, so embeddings had zeroed solar features.
    - **V2–V3**: Experimental sampling strategies (uniform random, distance-weighted). Never formalized as tables.
    - **V4** (`training_stratified`): SSN-stratified quintile bins. Retained — useful for ablation studies but superseded for production training.
    - **V5** (`training_continuous`): IFW-weighted continuous sampling. Current production training source.
    - **V6** (`training_v6_clean`): V5 + `kp_penalty` constraint column. Used for Phase 6+ training (Kp inversion fix).

    The CSV artifact `data/training_v6_clean.csv` (878 MB, 10M rows) is a valid export of `wspr.training_v6_clean` used for M3 training. It is not needed for reproduction — regenerate with `clickhouse-client --query "SELECT * FROM wspr.training_v6_clean FORMAT CSV" > training_v6_clean.csv`.
