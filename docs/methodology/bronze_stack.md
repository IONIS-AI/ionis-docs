# Reproducing the Bronze Stack

This guide documents every step needed to reproduce the full IONIS bronze layer — raw data loaded into ClickHouse from source archives on ZFS — from a clean slate.

## Overview

The "bronze stack" is the set of ClickHouse tables containing raw and lightly transformed data. All tables are reproducible from source archives stored on ZFS, using deterministic DDL and population scripts from `ki7mt-ai-lab-core`.

**Current state** (2026-02-07):

| Database | Tables | Total Rows | Total Size |
|----------|--------|------------|------------|
| `wspr` | 10 (+ 2 views, 1 MV) | 10.8B | 191 GiB |
| `rbn` | 1 | 2.18B | 45.3 GiB |
| `contest` | 1 | 232.6M | 4.1 GiB |
| `solar` | 1 (+ 1 view) | 17.8K | 868 KiB |
| `data_mgmt` | 2 | — | — |
| `geo` | 0 (+ 1 view) | — | — |

## Prerequisites

1. **ClickHouse** running on the target host (default `192.168.1.90`)
2. **ZFS datasets** mounted:
    - `/mnt/wspr-data` — WSPR raw CSV archives (.csv.gz)
    - `/mnt/contest-logs` — CQ + ARRL Cabrillo log files
    - `/mnt/rbn-data` — RBN daily ZIP archives
3. **RPM packages** installed (v2.3.1+):
    - `ki7mt-ai-lab-core` — DDL schemas and population scripts
    - `ki7mt-ai-lab-apps` — Go ingesters (wspr-turbo, rbn-ingest, contest-ingest, solar-backfill)
    - `ki7mt-ai-lab-cuda` — bulk-processor (CUDA signature engine)

## DDL Application Order

All DDL files live in `/usr/share/ki7mt-ai-lab-core/ddl/` (installed by the RPM) and must be applied in numerical order. Each file is idempotent (`CREATE TABLE IF NOT EXISTS`).

```bash
for f in /usr/share/ki7mt-ai-lab-core/ddl/*.sql; do
    echo "Applying: $f"
    clickhouse-client --multiquery < "$f"
done
```

| # | File | Database | Creates |
|---|------|----------|---------|
| 01 | `wspr_schema_v2.sql` | wspr | `bronze`, `v_schema_contract`, `v_data_integrity` |
| 02 | `solar_indices.sql` | solar | `bronze` |
| 03 | `solar_silver.sql` | solar | `v_daily_indices` |
| 04 | `data_mgmt.sql` | data_mgmt | `config` |
| 05 | `geo_functions.sql` | geo | `v_grid_validation_example` |
| 06 | `lab_versions.sql` | data_mgmt | `lab_versions`, `v_lab_versions_latest` |
| 07 | `callsign_grid.sql` | wspr | `callsign_grid` |
| 08 | `model_features.sql` | wspr | `silver` |
| 09 | `quality_distribution_mv.sql` | wspr | `v_quality_distribution` (MV) |
| 10 | `rbn_schema_v1.sql` | rbn | `bronze` |
| 11 | `contest_schema_v1.sql` | contest | `bronze` |
| 12 | `signatures_v1.sql` | wspr | `signatures_v1` |
| 13 | `gold_stratified.sql` | wspr | `gold_stratified` |
| 14 | `gold_continuous.sql` | wspr | `gold_continuous` |
| 15 | `gold_v6.sql` | wspr | `gold_v6` |

!!! note "DDL 09 depends on DDL 08"
    The `v_quality_distribution` materialized view reads from `silver`. DDL 08 must be applied first.

## Bronze Tables

These are the primary data tables populated directly from source archives.

### `wspr.bronze` — 10.8B rows, 191 GiB

Raw WSPR spot records from wsprnet.org CSV archives.

- **Source**: `/mnt/wspr-data/*.csv.gz`
- **Tool**: `wspr-turbo` (streaming .gz parser, 22.55 Mrps with 16 workers)
- **Command**: `wspr-turbo -ch-host 192.168.1.90:9000 -source-dir /mnt/wspr-data -workers 16`
- **Wall time**: ~8 min on 9975WX

```sql
-- Verification
SELECT count() FROM wspr.bronze;
-- Expected: ~10,800,000,000

SELECT uniq(band) FROM wspr.bronze WHERE band BETWEEN 102 AND 111;
-- Expected: 10 (all HF bands)
```

### `solar.bronze` — ~17.8K rows, 868 KiB

Daily/3-hourly SSN, SFI, and Kp from GFZ Potsdam (2000–present).

- **Source**: GFZ Potsdam FTP (downloaded by tool)
- **Tool**: `solar-backfill`
- **Command**: `solar-backfill -ch-host 192.168.1.90:9000`
- **Wall time**: <1s

```sql
-- Verification
SELECT count() FROM solar.bronze;
-- Expected: ~17,840

SELECT min(date), max(date) FROM solar.bronze;
-- Expected: 2000-01-01 to ~today
```

### `rbn.bronze` — 2.18B rows, 45.3 GiB

Reverse Beacon Network CW/RTTY spots from daily ZIP archives.

- **Source**: `/mnt/rbn-data/*.zip`
- **Tool**: `rbn-ingest`
- **Command**: `rbn-ingest -host 192.168.1.90:9000 -src /mnt/rbn-data`
- **Wall time**: ~3m30s (10.15 Mrps)

```sql
-- Verification
SELECT count() FROM rbn.bronze;
-- Expected: ~2,180,000,000
```

### `contest.bronze` — 232.6M rows, 4.1 GiB

Parsed QSO records from CQ and ARRL Cabrillo log files.

- **Source**: `/mnt/contest-logs/` (491K files across 15 contests)
- **Tool**: `contest-ingest`
- **Command**: `contest-ingest -host 192.168.1.90:9000 -src /mnt/contest-logs -enrich`
- **Wall time**: ~24 min (with enrichment)

```sql
-- Verification
SELECT count() FROM contest.bronze;
-- Expected: ~232,600,000

SELECT contest, count() FROM contest.bronze GROUP BY contest ORDER BY count() DESC;
```

### `wspr.callsign_grid` — ~38.5K rows

Callsign-to-grid Rosetta Stone populated by contest enrichment (HQ-GRID-LOCATOR headers).

- **Source**: contest logs with grid data (derived via `contest-ingest -enrich`)
- **Tool**: `contest-ingest -enrich` populates during contest ingest; full population from WSPR data is a separate step
- **Wall time**: included in contest-ingest run

```sql
-- Verification
SELECT count() FROM wspr.callsign_grid FINAL;
-- Expected: ~38,500 (contest-enrichment only; full WSPR-derived population is a separate step)
```

### `wspr.silver` — 4.4B rows, 41 GiB

Float4 embeddings generated by the CUDA bulk-processor from spots + solar data.

- **Source**: `wspr.bronze` + `solar.bronze` (derived)
- **Tool**: `bulk-processor` (CUDA, RTX PRO 6000)
- **Command**: `bulk-processor --host 192.168.1.90`
- **Wall time**: ~45 min on 9975WX

!!! warning "Requires NVIDIA GPU"
    The bulk-processor requires an NVIDIA GPU with sufficient VRAM. The RTX PRO 6000 (96 GB) processes all 10.8B spots in a single pass.

```sql
-- Verification
SELECT count() FROM wspr.silver;
-- Expected: ~4,430,000,000
```

## Derived Tables

These tables are built from bronze tables using SQL queries or population scripts in `ki7mt-ai-lab-core/scripts/`.

### `wspr.signatures_v1` — 93.8M rows, 2.3 GiB

Median-bucketed WSPR signatures — 115:1 compression from raw spots.

- **Prerequisites**: `wspr.bronze`, `solar.bronze`
- **Script**: `scripts/populate_signatures.sh`
- **Command**: `bash populate_signatures.sh` (or `CH_HOST=10.60.1.1 bash populate_signatures.sh`)
- **Wall time**: ~3 min 10s on 9975WX

```sql
-- Verification
SELECT count() FROM wspr.signatures_v1;
-- Expected: ~93,800,000
```

### `wspr.gold_stratified` — 10M rows, 167 MiB

SSN-stratified training set (200K per band x quintile).

- **Prerequisites**: `wspr.bronze`, `solar.bronze`
- **Script**: `scripts/populate_stratified.sh`
- **Command**: `bash populate_stratified.sh`
- **Wall time**: ~10 min

```sql
SELECT count() FROM wspr.gold_stratified;
-- Expected: 10,000,000
```

### `wspr.gold_continuous` — 10M rows, 218 MiB

IFW-weighted training set (1M per band, Efraimidis-Spirakis sampling).

- **Prerequisites**: `wspr.bronze`, `solar.bronze`
- **Script**: `scripts/populate_continuous.sh`
- **Command**: `bash populate_continuous.sh`
- **Wall time**: ~15 min

```sql
SELECT count() FROM wspr.gold_continuous;
-- Expected: 10,000,000
```

### `wspr.gold_v6` — 10M rows, 240 MiB

Phase 6 training set: `gold_continuous` + `kp_penalty` constraint column.

- **Prerequisites**: `wspr.gold_continuous` (must be populated first)
- **Script**: `scripts/populate_v6_clean.sh`
- **Command**: `bash populate_v6_clean.sh`
- **Wall time**: <30s

```sql
SELECT count() FROM wspr.gold_v6;
-- Expected: 10,000,000

-- Verify kp_penalty range
SELECT min(kp_penalty), max(kp_penalty) FROM wspr.gold_v6;
-- Expected: ~0.0 to 1.0
```

### `wspr.v_quality_distribution` (Materialized View)

Automatically populated as rows are inserted into `wspr.silver`. No manual population needed.

```sql
SELECT count() FROM wspr.v_quality_distribution;
-- Expected: ~6,100,000
```

## Full Stack Build Order

To reproduce the entire bronze stack from scratch:

```text
Phase 1: DDL
  Apply all /usr/share/ki7mt-ai-lab-core/ddl/*.sql in order (01-15)

Phase 2: Bronze Ingest
  2a. solar-backfill           →  solar.bronze        (~1s)
  2b. wspr-turbo               →  wspr.bronze           (~8m)  ⚠ RUN SOLO (16 workers, OOM risk if concurrent)
  2c. rbn-ingest               →  rbn.bronze            (~3m30s)
  2d. contest-ingest -enrich   →  contest.bronze             (~24m)

Phase 3: Derived from bronze + solar (sequential)
  3a. bulk-processor (CUDA)    →  wspr.silver      (~45m)
      (also auto-populates v_quality_distribution via MV)
  3b. callsign_grid population →  wspr.callsign_grid       (~2m)
  3c. populate_signatures.sh   →  wspr.signatures_v1       (~3m)

Phase 4: Training tables (sequential)
  4a. populate_stratified.sh   →  wspr.gold_stratified (~10m)
  4b. populate_continuous.sh   →  wspr.gold_continuous  (~15m)
  4c. populate_v6_clean.sh     →  wspr.gold_v6   (<30s)
```

**Total wall time**: ~2h on 9975WX (Threadripper 9975WX, 128 GB DDR5, RTX PRO 6000)

## Training Table Lineage

!!! info "V1–V5 were iterative development tables"
    Training tables V1 through V5 were development/testing iterations that did not survive:

    - **V1** (`training_set_v1`): First attempt at gold-standard dataset from `silver`. Dropped — solar backfill didn't exist yet, so embeddings had zeroed solar features.
    - **V2–V3**: Experimental sampling strategies (uniform random, distance-weighted). Never formalized as tables.
    - **V4** (`gold_stratified`): SSN-stratified quintile bins. Retained — useful for ablation studies but superseded for production training.
    - **V5** (`gold_continuous`): IFW-weighted continuous sampling. Current production training source.
    - **V6** (`gold_v6`): V5 + `kp_penalty` constraint column. Used for Phase 6+ training (Kp inversion fix).

    The CSV artifact `data/gold_v6.csv` (878 MB, 10M rows) is a valid export of `wspr.gold_v6` used for M3 training. It is not needed for reproduction — regenerate with `clickhouse-client --query "SELECT * FROM wspr.gold_v6 FORMAT CSV" > gold_v6.csv`.
