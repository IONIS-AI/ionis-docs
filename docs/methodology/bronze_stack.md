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
3. **RPM packages** installed (v3.0.2+):
    - `ionis-core` — DDL schemas and population scripts
    - `ionis-apps` — Go ingesters (wspr-turbo, rbn-ingest, contest-ingest, solar-backfill)

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
DDL Files (15 total):

  #   File                          Database    Creates
  --  ----------------------------  ----------  ------------------------------------
  01  wspr_schema_v2.sql            wspr        bronze, v_schema_contract, v_data_integrity
  02  solar_indices.sql             solar       bronze
  03  solar_silver.sql              solar       v_daily_indices
  04  data_mgmt.sql                 data_mgmt   config
  05  geo_functions.sql             geo         v_grid_validation_example
  06  lab_versions.sql              data_mgmt   lab_versions, v_lab_versions_latest
  07  callsign_grid.sql             wspr        callsign_grid
  08  model_features.sql            wspr        silver
  09  quality_distribution_mv.sql   wspr        v_quality_distribution (MV)
  10  rbn_schema_v1.sql             rbn         bronze
  11  contest_schema_v1.sql         contest     bronze
  12  signatures_v1.sql             wspr        signatures_v1
  13  training_stratified.sql       wspr        gold_stratified
  14  training_continuous.sql       wspr        gold_continuous
  15  training_v6_clean.sql         wspr        gold_v6
```

!!! note "DDL 09 depends on DDL 08"
    The `v_quality_distribution` materialized view reads from `silver`.
    DDL 08 must be applied first.

## Step 2: Load Solar Data

Load historical SSN, SFI, and Kp from GFZ Potsdam. This must run before
WSPR so that solar indices are available for downstream JOINs.

```bash
solar-backfill -ch-host 192.168.1.90:9000
```

Verification:

```bash
clickhouse-client --query "SELECT count() FROM solar.bronze"
# Expected: ~17,840

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

## QA Actuals

Clean-slate rebuild on 9975WX (2026-02-07):

```text
Table                Rows              Time     Throughput
-------------------  ----------------  -------  ----------
wspr.bronze          10,798,087,395    8m13s    21.91 Mrps
solar.bronze         17,840            <1s      --
rbn.bronze           2,184,591,303     3m32s    10.30 Mrps
contest.bronze       234,268,090       21m32s   --
wspr.callsign_grid   38,622            --       (contest enrichment)
-------------------  ----------------  -------  ----------
Total wall time      ~35 min (sequential)
```

## Next Steps

- **Silver layer**: See [Silver Layer](silver_layer.md) for CUDA embeddings and aggregated signatures
- **Gold layer**: See [Gold Layer](gold_layer.md) for training tables and CSV export
