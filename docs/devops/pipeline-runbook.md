# Pipeline Runbook

Step-by-step guide to build the full IONIS pipeline from a clean slate.
This is the tested, dependency-ordered sequence — proven during the v3.0
migration rebuild (2026-02-13). Each phase links to the relevant
Methodology page for detail; this page is the consolidated checklist
with commands, expected counts, and wall times.

**Total wall time: ~2 hours on [reference hardware](index.md#reference-build)
(9975WX ingest + population), plus ~4 hours training on M3 Ultra.**

---

## Phase 1: Install Packages (9975WX)

### Step 1.1: Enable COPR and install

```bash
sudo dnf copr enable ki7mt/ionis-ai
sudo dnf install ionis-core ionis-apps
```

### Step 1.2: Verify installed versions

```bash
rpm -q ionis-core ionis-apps
# Expected: ionis-core-3.0.3+, ionis-apps-3.0.1+
```

### Step 1.3: Verify DDL and scripts installed

```bash
ls /usr/share/ionis-core/ddl/*.sql | wc -l
# Expected: 29

ls /usr/share/ionis-core/scripts/*.sh | wc -l
# Expected: 12
```

---

## Phase 2: Create Database Schema (< 1 min)

All DDL files live in `/usr/share/ionis-core/ddl/`. Each is idempotent
(`CREATE TABLE/VIEW IF NOT EXISTS`). Apply in numerical order — the
sequence encodes dependencies.

### Step 2.1: Apply all DDL

```bash
ionis-db-init
```

Or manually:

```bash
for f in /usr/share/ionis-core/ddl/*.sql; do
    echo "Applying: $(basename $f)"
    clickhouse-client --multiquery < "$f"
done
```

### Step 2.2: DDL Inventory (29 files)

```text
  #   File                              Database      Creates
  --  --------------------------------  -----------   ----------------------------------------
  01  wspr_schema_v2.sql                wspr          bronze, mv_spots_daily
  02  solar_indices.sql                 solar         bronze
  03  solar_silver.sql                  solar         v_daily_indices
  04  data_mgmt.sql                     data_mgmt     config
  05  geo_functions.sql                 geo           v_grid_validation_example
  06  lab_versions.sql                  data_mgmt     lab_versions
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

### Step 2.3: Verify table count

```bash
clickhouse-client --query "
SELECT count()
FROM system.tables
WHERE database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA', 'default')
  AND engine <> ''
  AND name NOT LIKE '.inner_id%'
"
# Expected: 35
```

See [Bronze Stack — Step 1](../methodology/bronze_stack.md#step-1-apply-ddl-schemas) for
additional detail.

---

## Phase 3: Bronze Ingest (~35 min)

Order matters. Solar must run first — downstream JOINs depend on it.
Run `wspr-turbo` solo (it consumes ~80 GB RAM at 16 workers).

### Step 3.1: Solar backfill

```bash
solar-backfill -start 2000-01-01
clickhouse-client --query "OPTIMIZE TABLE solar.bronze FINAL"
```

!!! note "Additional solar sources"
    `solar-backfill` loads GFZ Potsdam historical data only. Additional
    solar data comes from `solar-history-load` (NOAA, 6-hour cron) and
    `solar-live-update` (SWPC, 15-min cron). Run those manually or wait
    for their cron cycles to fully populate `solar.bronze` and
    `wspr.live_conditions`.

### Step 3.2: WSPR ingest

```bash
wspr-turbo /mnt/wspr-data/wsprspots-*.csv.gz
```

!!! warning "Run wspr-turbo solo"
    With 16 workers, wspr-turbo consumes ~80 GB RAM. Do not run other
    ingesters concurrently.

### Step 3.3: RBN ingest

```bash
rbn-ingest /mnt/rbn-data/
```

### Step 3.4: Contest ingest

```bash
contest-ingest /mnt/contest-logs/
```

### Step 3.5: PSK Reporter ingest

```bash
pskr-ingest /mnt/pskr-data/
```

### Step 3.6: Verify all bronze tables

```bash
clickhouse-client --query "
SELECT 'solar.bronze' AS tbl, count() AS rows FROM solar.bronze
UNION ALL SELECT 'wspr.bronze', count() FROM wspr.bronze
UNION ALL SELECT 'rbn.bronze', count() FROM rbn.bronze
UNION ALL SELECT 'contest.bronze', count() FROM contest.bronze
UNION ALL SELECT 'pskr.bronze', count() FROM pskr.bronze
ORDER BY 1
FORMAT PrettyCompact
"
```

### QA Actuals

Clean-slate rebuild on 9975WX (2026-02-07):

| Table | Expected Rows | Time | Throughput |
|-------|---------------|------|------------|
| `solar.bronze` | ~76,000 | < 1 s | — |
| `wspr.bronze` | ~10,800,000,000 | ~8 min | 21.91 Mrps |
| `rbn.bronze` | ~2,184,000,000 | ~3 min 30 s | 10.30 Mrps |
| `contest.bronze` | ~234,000,000 | ~22 min | — |
| `pskr.bronze` | ~81,000,000+ | varies | — |

See [Bronze Stack](../methodology/bronze_stack.md) for per-step verification queries.

---

## Phase 4: Populate Derived Tables (~20 min)

All 12 population scripts live in `/usr/share/ionis-core/scripts/`. They
accept `CH_HOST` env var (default: `192.168.1.90`, use `10.60.1.1` for DAC).

Run in dependency order — three tiers.

### Tier 1: No dependencies beyond bronze

```bash
# 4.1 — Callsign→Grid Rosetta Stone (depends on: wspr.bronze)
bash /usr/share/ionis-core/scripts/populate_callsign_grid.sh
# Expected: ~3.6M rows in wspr.callsign_grid

# 4.2 — WSPR Signatures V1 (depends on: wspr.bronze, solar.bronze)
bash /usr/share/ionis-core/scripts/populate_signatures.sh
# Expected: ~93.8M rows in wspr.signatures_v1 (~3 min)

# 4.3 — Continuous training set (depends on: wspr.bronze, solar.bronze)
bash /usr/share/ionis-core/scripts/populate_continuous.sh
# Expected: 10M rows in wspr.gold_continuous (~4 min)

# 4.4 — Stratified training set (depends on: wspr.bronze, solar.bronze)
bash /usr/share/ionis-core/scripts/populate_stratified.sh
# Expected: 10M rows in wspr.gold_stratified (~7 min)
```

### Tier 2: Depends on Tier 1 outputs

```bash
# 4.5 — Balloon callsigns V2 (depends on: wspr.bronze, wspr.callsign_grid)
bash /usr/share/ionis-core/scripts/populate_balloon_callsigns.sh
# Expected: ~1,443 rows in wspr.balloon_callsigns_v2

# 4.6 — RBN Signatures (depends on: rbn.bronze, wspr.callsign_grid, solar.bronze)
bash /usr/share/ionis-core/scripts/populate_rbn_signatures.sh
# Expected: ~56.7M rows in rbn.signatures

# 4.7 — Contest Signatures (depends on: contest.bronze, wspr.callsign_grid, solar.bronze)
bash /usr/share/ionis-core/scripts/populate_contest_signatures.sh
# Expected: ~6.3M rows in contest.signatures

# 4.8 — Quality test paths (depends on: wspr.signatures_v1)
bash /usr/share/ionis-core/scripts/populate_quality_test_paths.sh
# Expected: 100K rows in validation.quality_test_paths

# 4.9 — V6 clean training set (depends on: wspr.gold_continuous)
bash /usr/share/ionis-core/scripts/populate_v6_clean.sh
# Expected: 10M rows in wspr.gold_v6
```

### DXpedition chain (depends on Tier 1 + rbn.bronze)

```bash
# 4.10 — DXpedition catalog (depends on: static TSV data file)
bash /usr/share/ionis-core/scripts/populate_dxpedition_catalog.sh
# Expected: 332 rows in dxpedition.catalog

# 4.11 — DXpedition paths + signatures (depends on: catalog, rbn.bronze, callsign_grid, solar.bronze)
bash /usr/share/ionis-core/scripts/populate_dxpedition_paths.sh
# Expected: ~3.9M rows in rbn.dxpedition_paths, ~260K rows in rbn.dxpedition_signatures
```

### Tier 3: Balloon-filtered signatures

```bash
# 4.12 — Signatures V2 Terrestrial (depends on: wspr.bronze, solar.bronze, balloon_callsigns_v2)
bash /usr/share/ionis-core/scripts/populate_signatures_v2_terrestrial.sh
# Expected: ~93.3M rows in wspr.signatures_v2_terrestrial
```

### Step 4.13: Verify all derived tables

```bash
clickhouse-client --query "
SELECT 'wspr.callsign_grid' AS tbl, count() AS rows FROM wspr.callsign_grid
UNION ALL SELECT 'wspr.signatures_v1', count() FROM wspr.signatures_v1
UNION ALL SELECT 'wspr.signatures_v2_terrestrial', count() FROM wspr.signatures_v2_terrestrial
UNION ALL SELECT 'wspr.balloon_callsigns_v2', count() FROM wspr.balloon_callsigns_v2
UNION ALL SELECT 'wspr.gold_continuous', count() FROM wspr.gold_continuous
UNION ALL SELECT 'wspr.gold_stratified', count() FROM wspr.gold_stratified
UNION ALL SELECT 'wspr.gold_v6', count() FROM wspr.gold_v6
UNION ALL SELECT 'rbn.signatures', count() FROM rbn.signatures
UNION ALL SELECT 'contest.signatures', count() FROM contest.signatures
UNION ALL SELECT 'dxpedition.catalog', count() FROM dxpedition.catalog
UNION ALL SELECT 'rbn.dxpedition_paths', count() FROM rbn.dxpedition_paths
UNION ALL SELECT 'rbn.dxpedition_signatures', count() FROM rbn.dxpedition_signatures
UNION ALL SELECT 'validation.quality_test_paths', count() FROM validation.quality_test_paths
ORDER BY 1
FORMAT PrettyCompact
"
```

---

## Phase 5: Silver Layer (~50 min, optional)

Generate CUDA float4 embeddings from WSPR spots joined with solar indices.

!!! note "GPU required"
    `bulk-processor` requires an NVIDIA GPU. It is not yet packaged in the
    `ionis-cuda` RPM — build locally:
    `cd ionis-cuda && mkdir build && cd build && cmake .. && make`

```bash
bulk-processor --host 192.168.1.90
```

| Target Table | Expected Rows | Time |
|-------------|---------------|------|
| `wspr.silver` | ~4.43B | ~45 min |
| `wspr.v_quality_distribution` | ~6.1M | auto (MV) |

Verification:

```bash
clickhouse-client --query "SELECT count() FROM wspr.silver"
# Expected: ~4,430,000,000
```

See [Silver Layer](../methodology/silver_layer.md) for details.

---

## Phase 6: Export Training Data

Export the gold_v6 training set as CSV and transfer to the training host.

```bash
clickhouse-client --query "SELECT * FROM wspr.gold_v6 FORMAT CSV" \
    > /mnt/ai-stack/ionis-ai/ionis-training/data/gold_v6.csv

# Transfer to M3 Ultra via DAC link
scp data/gold_v6.csv gbeam@10.60.1.2:workspace/ionis-ai/ionis-training/data/
```

Verification:

```bash
wc -l data/gold_v6.csv
# Expected: 10,000,000

ls -lh data/gold_v6.csv
# Expected: ~838 MB
```

See [Gold Layer](../methodology/gold_layer.md) for training table lineage.

---

## Phase 7: Verify Services (9975WX)

### Step 7.1: Solar live update

```bash
solar-live-update
clickhouse-client --query "SELECT * FROM wspr.live_conditions ORDER BY updated_at DESC LIMIT 1"
```

### Step 7.2: Cron jobs

```bash
crontab -l | grep -E 'solar|pskr|rbn|wspr'
```

See [Operations & Maintenance](maintenance.md) for the full cron schedule.

### Step 7.3: pskr-collector service

```bash
systemctl status pskr-collector
# Expected: active (running)
```

---

## Phase 8: M3 Ultra Setup (Sage Node)

### Step 8.1: Clone all repos

```bash
mkdir -p /Users/gbeam/workspace/ionis-ai && cd /Users/gbeam/workspace/ionis-ai
for repo in ionis-core ionis-apps ionis-cuda ionis-docs ionis-training ionis-devel ionis-tools; do
    git clone git@github.com:IONIS-AI/${repo}.git
done
```

### Step 8.2: Verify ClickHouse connectivity over DAC

```bash
clickhouse-client --host 10.60.1.1 --query "SELECT version()"
clickhouse-client --host 10.60.1.1 --query "SELECT count() FROM wspr.bronze"
```

### Step 8.3: Set up Python venv

```bash
cd /Users/gbeam/workspace/ionis-ai/ionis-training
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Phase 9: Train and Validate V20 (M3 Ultra)

### Step 9.1: Train V20

```bash
cd /Users/gbeam/workspace/ionis-ai/ionis-training
source .venv/bin/activate
python train.py --config versions/v20/config_v20.json
# Expected: ~4h 16m on M3 Ultra (MPS backend)
```

### Step 9.2: Run validation suite

```bash
python versions/v20/verify_v20.py
python versions/v20/test_v20.py
python versions/v20/validate_v20.py
```

### Step 9.3: PSK Reporter live validation

```bash
python versions/v20/validate_v20_pskr.py
# Target: > 84% recall on independent spots
```

### Step 9.4: Acceptance criteria

| Metric | Target | V20 Reference |
|--------|--------|---------------|
| Pearson | > +0.48 | +0.4879 |
| Kp sidecar | > +3.0 sigma | +3.487 sigma |
| SFI sidecar | > +0.4 sigma | +0.482 sigma |
| RMSE | < 0.87 sigma | 0.862 sigma |

---

## Summary: Full Stack Build Order

```text
Phase 1: Install Packages
  1.1  dnf install ionis-core ionis-apps
  1.2  Verify versions, DDL count (29), script count (12)

Phase 2: Schema
  2.1  ionis-db-init                                         (<1 min)
  2.2  Verify table count (35)

Phase 3: Bronze Ingest
  3.1  solar-backfill                solar.bronze             (<1s)
  3.2  wspr-turbo                    wspr.bronze              (~8m)   RUN SOLO
  3.3  rbn-ingest                    rbn.bronze               (~3m30s)
  3.4  contest-ingest                contest.bronze           (~22m)
  3.5  pskr-ingest                   pskr.bronze              (varies)

Phase 4: Population Scripts (Tier 1 → 2 → 3)
  4.1  populate_callsign_grid.sh     wspr.callsign_grid       (~3.6M)
  4.2  populate_signatures.sh        wspr.signatures_v1       (~93.8M)
  4.3  populate_continuous.sh        wspr.gold_continuous      (10M)
  4.4  populate_stratified.sh        wspr.gold_stratified      (10M)
  ── Tier 2 ──
  4.5  populate_balloon_callsigns.sh wspr.balloon_callsigns_v2 (~1.4K)
  4.6  populate_rbn_signatures.sh    rbn.signatures            (~56.7M)
  4.7  populate_contest_signatures.sh contest.signatures       (~6.3M)
  4.8  populate_quality_test_paths.sh validation.quality_test_paths (100K)
  4.9  populate_v6_clean.sh          wspr.gold_v6              (10M)
  ── DXpedition ──
  4.10 populate_dxpedition_catalog.sh   dxpedition.catalog            (332)
  4.11 populate_dxpedition_paths.sh     rbn.dxpedition_paths          (~3.9M)
                                        rbn.dxpedition_signatures     (~260K)
  ── Tier 3 ──
  4.12 populate_signatures_v2_terrestrial.sh  wspr.signatures_v2_terrestrial (~93.3M)

Phase 5: Silver Layer (optional, requires GPU)
  5.1  bulk-processor (CUDA)         wspr.silver              (~4.43B, ~45m)

Phase 6: Export Training Data
  6.1  gold_v6.csv export + SCP to M3

Phase 7: Verify Services
  7.1  solar-live-update, cron jobs, pskr-collector

Phase 8: M3 Ultra Setup
  8.1  Clone repos, venv, DAC connectivity

Phase 9: Train and Validate V20
  9.1  train.py --config versions/v20/config_v20.json        (~4h16m)
  9.2  verify_v20.py, test_v20.py, validate_v20.py
  9.3  validate_v20_pskr.py (>84% recall)
```
