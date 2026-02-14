# Bronze Stack

Reproduction guide for the IONIS bronze layer — raw data loaded into
ClickHouse from source archives on ZFS.

## Overview

The bronze stack contains raw and lightly transformed data loaded directly from
source archives. All tables are reproducible from ZFS-stored archives using
deterministic DDL and CLI tools from `ionis-core` and `ionis-apps`.

Bronze is self-contained — users who only need the dataset can stop here.

## Prerequisites

1. **ClickHouse** running on the target host (default `192.168.1.90`)
2. **ZFS datasets** mounted:
    - `/mnt/wspr-data` — WSPR raw CSV archives (.csv.gz)
    - `/mnt/contest-logs` — CQ + ARRL Cabrillo log files
    - `/mnt/rbn-data` — RBN daily ZIP archives
    - `/mnt/pskr-data` — PSK Reporter MQTT collection (gzip JSONL)
3. **RPM packages** installed (v3.0.3+):
    - `ionis-core` — DDL schemas (29 files), population scripts (12 files), and static data
    - `ionis-apps` — Go ingesters (wspr-turbo, rbn-ingest, contest-ingest, solar-backfill, pskr-ingest)

## Step 1: Apply DDL Schemas

All DDL files live in `/usr/share/ionis-core/ddl/` (installed by the
RPM). Each file is idempotent (`CREATE TABLE IF NOT EXISTS`). Apply in
numerical order:

```bash
for f in /usr/share/ionis-core/ddl/*.sql; do
    echo "Applying: $f"
    clickhouse-client --multiquery < "$f"
done
```

```text
DDL Files (29 total):

  #   File                              Database      Creates
  --  --------------------------------  -----------   ----------------------------------------
  01  wspr_schema_v2.sql                wspr          bronze, v_schema_contract, v_data_integrity
  02  solar_indices.sql                 solar         bronze
  03  solar_silver.sql                  solar         v_daily_indices
  04  data_mgmt.sql                     data_mgmt     config
  05  geo_functions.sql                 geo           v_grid_validation_example
  06  lab_versions.sql                  data_mgmt     lab_versions, v_lab_versions_latest
  07  callsign_grid.sql                 wspr          callsign_grid
  08  model_features.sql                wspr          silver
  09  quality_distribution_mv.sql       wspr          v_quality_distribution (MV → silver)
  10  rbn_schema_v1.sql                 rbn           bronze
  11  contest_schema_v1.sql             contest       bronze
  12  signatures_v1.sql                 wspr          signatures_v1
  13  training_stratified.sql           wspr          gold_stratified
  14  training_continuous.sql           wspr          gold_continuous
  15  training_v6_clean.sql             wspr          gold_v6
  16  validation_step_i.sql             validation    step_i_paths, step_i_voacap
  17  balloon_callsigns.sql             wspr          balloon_callsigns
  18  validation_quality_test.sql       validation    quality_test_paths, quality_test_voacap
  19  dxpedition_synthesis.sql          dxpedition    catalog; rbn.dxpedition_paths
  20  signatures_v2_terrestrial.sql     wspr          signatures_v2_terrestrial
  21  balloon_callsigns_v2.sql          wspr          balloon_callsigns_v2
  22  pskr_schema_v1.sql                pskr          bronze
  23  contest_signatures.sql            contest       signatures
  24  rbn_signatures.sql                rbn           signatures
  25  live_conditions.sql               wspr          live_conditions
  26  validation_model_results.sql      validation    model_results
  27  mode_thresholds.sql               validation    mode_thresholds
  28  pskr_ingest_log.sql               pskr          ingest_log
  29  rbn_dxpedition_signatures.sql     rbn           dxpedition_signatures
```

!!! note "DDL 09 depends on DDL 08"
    The `v_quality_distribution` materialized view reads from `wspr.silver`.
    DDL 08 must be applied first. Sequential numbering handles this
    automatically.

## Step 2: Load Solar Data

Load historical SSN, SFI, and Kp from GFZ Potsdam. This must run before
WSPR so that solar indices are available for downstream JOINs.

```bash
solar-backfill -start 2000-01-01
clickhouse-client --query "OPTIMIZE TABLE solar.bronze FINAL"
```

!!! note "Additional solar sources"
    `solar-backfill` loads GFZ Potsdam historical data only (~76K rows).
    Additional data comes from `solar-history-load` (NOAA, 6-hour cron)
    and `solar-live-update` (SWPC, 15-min cron). Run those manually or
    wait for cron cycles to fully populate `solar.bronze` and
    `wspr.live_conditions`.

Verification:

```bash
clickhouse-client --query "SELECT count() FROM solar.bronze"
# Expected: ~76,000 (GFZ only; grows with NOAA cron)

clickhouse-client --query "SELECT min(date), max(date) FROM solar.bronze"
# Expected: 2000-01-01 to ~today
```

## Step 3: Load WSPR Data

Stream all WSPR CSV archives into ClickHouse. This is the largest ingest
and uses 16 workers — run it alone to avoid OOM.

```bash
wspr-turbo -ch-host 192.168.1.90:9000 -source-dir /mnt/wspr-data -workers 16
```

!!! warning "Run wspr-turbo solo"
    With 16 workers, wspr-turbo consumes ~80 GB RAM. Do not run other
    ingesters concurrently.

Verification:

```bash
clickhouse-client --query "SELECT count() FROM wspr.bronze"
# Expected: ~10,800,000,000

clickhouse-client --query "SELECT uniq(band) FROM wspr.bronze WHERE band BETWEEN 102 AND 111"
# Expected: 10 (all HF bands)
```

## Step 4: Load RBN Data

Ingest Reverse Beacon Network CW/RTTY spots from daily ZIP archives.

```bash
rbn-ingest -host 192.168.1.90:9000 -src /mnt/rbn-data
```

Verification:

```bash
clickhouse-client --query "SELECT count() FROM rbn.bronze"
# Expected: ~2,180,000,000
```

## Step 5: Load Contest Data

Parse CQ and ARRL Cabrillo log files. The `-enrich` flag populates
`wspr.callsign_grid` from logs that contain grid locator headers.

```bash
contest-ingest -host 192.168.1.90:9000 -src /mnt/contest-logs -enrich
```

Verification:

```bash
clickhouse-client --query "SELECT count() FROM contest.bronze"
# Expected: ~234,000,000

clickhouse-client --query "SELECT contest, count() FROM contest.bronze GROUP BY contest ORDER BY count() DESC FORMAT PrettyCompact"

clickhouse-client --query "SELECT count() FROM wspr.callsign_grid FINAL"
# Expected: ~38,500 (from contest enrichment)
```

## Step 6: Load PSK Reporter Data

Ingest collected PSK Reporter MQTT spots from gzip JSONL files.

```bash
pskr-ingest /mnt/pskr-data/
```

Verification:

```bash
clickhouse-client --query "SELECT count() FROM pskr.bronze"
# Expected: varies (depends on collection window; ~26M spots/day since 2026-02-10)
```

## QA Actuals

Clean-slate rebuild on 9975WX (2026-02-13):

```text
Table                Rows              Time     Throughput
-------------------  ----------------  -------  ----------
solar.bronze         76,000+           <1s      --
wspr.bronze          10,798,087,395    8m13s    21.91 Mrps
rbn.bronze           2,184,591,303     3m32s    10.30 Mrps
contest.bronze       234,268,090       21m32s   --
pskr.bronze          81,000,000+       varies   --
wspr.callsign_grid   38,622            --       (contest enrichment)
-------------------  ----------------  -------  ----------
Total wall time      ~35 min (sequential, excluding pskr)
```

## Next Steps

- **Silver layer**: See [Silver Layer](silver_layer.md) for CUDA embeddings and aggregated signatures
- **Gold layer**: See [Gold Layer](gold_layer.md) for training tables and CSV export
