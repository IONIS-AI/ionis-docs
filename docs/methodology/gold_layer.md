# Gold Layer

Training-ready tables built from bronze + solar data. The gold layer provides
balanced, weighted datasets for IONIS model training.

Gold tables are derived directly from `wspr.bronze` + `solar.bronze` — they
do **not** depend on the silver layer or CUDA embeddings.

## Prerequisites

- `wspr.bronze` fully populated (~10.8B rows)
- `solar.bronze` populated (~17.8K rows)
- Gold DDL applied (DDLs 13-15, see [Bronze Stack](bronze_stack.md))

## Step 1: Populate gold_stratified

SSN-stratified training set: 200K rows per (band x SSN quintile) = 10M total.
Ensures equal representation across solar cycle conditions.

```bash
bash /usr/share/ionis-core/scripts/populate_stratified.sh
# Or with custom host:
# CH_HOST=10.60.1.1 bash /usr/share/ionis-core/scripts/populate_stratified.sh
```

Verification:

```bash
clickhouse-client --query "SELECT count() FROM wspr.gold_stratified"
# Expected: 10,000,000
```

## Step 2: Populate gold_continuous

IFW-weighted training set using Efraimidis-Spirakis weighted reservoir
sampling against a 2D (SSN, midpoint_lat) density histogram. Eliminates
stair-step artifacts from discrete SSN quintile bins.

```bash
bash /usr/share/ionis-core/scripts/populate_continuous.sh
# Or with custom host:
# CH_HOST=10.60.1.1 bash /usr/share/ionis-core/scripts/populate_continuous.sh
```

Verification:

```bash
clickhouse-client --query "SELECT count() FROM wspr.gold_continuous"
# Expected: 10,000,000
```

## Step 3: Populate gold_v6

Phase 6 training set: `gold_continuous` + `kp_penalty` constraint column.
Used for Phase 6+ training (Kp inversion fix).

!!! note "Depends on gold_continuous"
    This step must run after Step 2 — it reads from `wspr.gold_continuous`.

```bash
bash /usr/share/ionis-core/scripts/populate_v6_clean.sh
# Or with custom host:
# CH_HOST=10.60.1.1 bash /usr/share/ionis-core/scripts/populate_v6_clean.sh
```

Verification:

```bash
clickhouse-client --query "SELECT count() FROM wspr.gold_v6"
# Expected: 10,000,000

clickhouse-client --query "SELECT min(kp_penalty), max(kp_penalty) FROM wspr.gold_v6"
# Expected: ~0.0 to 1.0
```

## Step 4: Export gold_v6.csv

Export the training set as CSV for use on the M3 Ultra (or any training host).

```bash
mkdir -p /mnt/ai-stack/ionis-ai/ionis-training/data

clickhouse-client --query "SELECT * FROM wspr.gold_v6 FORMAT CSV" \
    > /mnt/ai-stack/ionis-ai/ionis-training/data/gold_v6.csv
```

Transfer to M3 Ultra via DAC link (from 9975WX):

```bash
scp data/gold_v6.csv gbeam@10.20.1.2:workspace/ionis-ai/ionis-training/data/
```

Verification:

```bash
wc -l data/gold_v6.csv
# Expected: 10,000,000

ls -lh data/gold_v6.csv
# Expected: ~838 MB
```

## Training Table Lineage

```text
V1  training_set_v1   First attempt from silver. Dropped (no solar backfill).
V2  (experimental)    Uniform random sampling. Never formalized.
V3  (experimental)    Distance-weighted sampling. Never formalized.
V4  gold_stratified   SSN-stratified quintile bins. Retained for ablation studies.
V5  gold_continuous   IFW-weighted continuous sampling. Production training source.
V6  gold_v6           V5 + kp_penalty constraint column. Phase 6+ training.
```

## QA Actuals

Clean-slate rebuild on 9975WX (2026-02-07):

```text
Table                Rows        Time    Size
-------------------  ----------  ------  -------
wspr.gold_stratified 10,000,000  6m50s   167 MiB
wspr.gold_continuous 10,000,000  3m36s   218 MiB
wspr.gold_v6         10,000,000  <30s    240 MiB
gold_v6.csv          10,000,000  --      838 MB
```

## Full Stack Build Order

For reference, the complete pipeline from clean slate:

```text
Phase 1: DDL (see Bronze Stack)
  Apply all /usr/share/ionis-core/ddl/*.sql in order (01-15)

Phase 2: Bronze Ingest (see Bronze Stack)
  2a. solar-backfill             solar.bronze          (<1s)
  2b. wspr-turbo                 wspr.bronze           (~8m)  RUN SOLO
  2c. rbn-ingest                 rbn.bronze            (~3m30s)
  2d. contest-ingest -enrich     contest.bronze        (~24m)

Phase 3: Silver Layer (see Silver Layer)
  3a. bulk-processor (CUDA)      wspr.silver           (~45m)
  3b. populate_signatures.sh     wspr.signatures_v2_terrestrial  (~3m30s)

Phase 4: Gold Layer (this page)
  4a. populate_stratified.sh     wspr.gold_stratified  (~7m)
  4b. populate_continuous.sh     wspr.gold_continuous   (~4m)
  4c. populate_v6_clean.sh       wspr.gold_v6          (<30s)
  4d. Export gold_v6.csv         CSV for M3 training

Total wall time: ~2h on 9975WX
```
