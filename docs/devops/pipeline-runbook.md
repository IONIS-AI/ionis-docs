# Pipeline Runbook

Step-by-step guide to build the full IONIS pipeline from a clean slate.
Each phase links to the relevant Methodology page for details — this page
is the consolidated checklist with commands, expected counts, and wall times.

**Total wall time: ~2 hours on [reference hardware](index.md#reference-build).**

## Prerequisites

- ClickHouse server running on the target host (default `192.168.1.90`)
- RPMs installed: `ionis-core` (v3.0.2+), `ionis-apps` (v3.0.1+)
- ZFS datasets mounted:
    - `/mnt/wspr-data` — WSPR raw CSV archives
    - `/mnt/contest-logs` — CQ/ARRL Cabrillo logs
    - `/mnt/rbn-data` — RBN daily ZIP archives
- Source data downloaded via `wspr-download`, `contest-download`, `rbn-download`

## Phase 1: Schema (< 1 min)

Apply all DDL files. Each is idempotent (`CREATE TABLE IF NOT EXISTS`).

```bash
for f in /usr/share/ionis-core/ddl/*.sql; do
    clickhouse-client --multiquery < "$f"
done
```

See [Bronze Stack — Step 1](../methodology/bronze_stack.md#step-1-apply-ddl-schemas) for the
full DDL file inventory.

## Phase 2: Bronze Ingest (~35 min)

Load raw data into ClickHouse. Solar must run first (downstream JOINs depend
on it). Run `wspr-turbo` solo — it uses ~80 GB RAM at 16 workers.

| Step | Command | Target Table | Expected Rows | Time |
|------|---------|-------------|---------------|------|
| 2a | `solar-backfill -ch-host 192.168.1.90:9000` | `solar.bronze` | ~17,840 | < 1 s |
| 2b | `wspr-turbo -ch-host 192.168.1.90:9000 -source-dir /mnt/wspr-data -workers 16` | `wspr.bronze` | ~10.8B | ~8 min |
| 2c | `rbn-ingest -host 192.168.1.90:9000 -src /mnt/rbn-data` | `rbn.bronze` | ~2.18B | ~3 min 30 s |
| 2d | `contest-ingest -host 192.168.1.90:9000 -src /mnt/contest-logs -enrich` | `contest.bronze` | ~234M | ~22 min |

See [Bronze Stack](../methodology/bronze_stack.md) for verification queries and details.

## Phase 3: Population Scripts (~10 min)

Derived tables built by deterministic population scripts in
`/usr/share/ionis-core/scripts/`.

| Step | Script | Target Table | Expected Rows |
|------|--------|-------------|---------------|
| 3a | `populate_callsign_grid.sh` | `wspr.callsign_grid` | ~38,600 |
| 3b | `populate_balloon_callsigns.sh` | `wspr.balloon_callsigns_v2` | ~1,443 |
| 3c | `populate_signatures.sh` | `wspr.signatures_v2_terrestrial` | ~93.6M |
| 3d | `populate_rbn_signatures.sh` | `rbn.signatures` | ~56.7M |
| 3e | `populate_contest_signatures.sh` | `contest.signatures` | ~6.3M |

Run each as:

```bash
bash /usr/share/ionis-core/scripts/populate_callsign_grid.sh
bash /usr/share/ionis-core/scripts/populate_balloon_callsigns.sh
bash /usr/share/ionis-core/scripts/populate_signatures.sh
bash /usr/share/ionis-core/scripts/populate_rbn_signatures.sh
bash /usr/share/ionis-core/scripts/populate_contest_signatures.sh
```

!!! warning "Dxpedition chain"
    The dxpedition tables (`dxpedition.catalog`, `rbn.dxpedition_paths`,
    `rbn.dxpedition_signatures`) were restored from backup and do not yet
    have reproducible population scripts. This is tracked for a future release.

## Phase 4: Silver Layer (~50 min)

Generate CUDA float4 embeddings from WSPR spots joined with solar indices.

```bash
bulk-processor --host 192.168.1.90
```

| Target Table | Expected Rows | Time |
|-------------|---------------|------|
| `wspr.silver` | ~4.43B | ~45 min |
| `wspr.v_quality_distribution` | ~6.1M | auto (MV) |

!!! note "Requires NVIDIA GPU"
    `bulk-processor` is not yet in the `ionis-cuda` RPM. Build locally:
    `cd ionis-cuda && mkdir build && cd build && cmake .. && make`

See [Silver Layer](../methodology/silver_layer.md) for details.

## Phase 5: Gold Layer (~15 min)

Build training-ready tables and export CSV for the training host.

| Step | Script | Target Table | Expected Rows | Time |
|------|--------|-------------|---------------|------|
| 5a | `populate_stratified.sh` | `wspr.gold_stratified` | 10M | ~7 min |
| 5b | `populate_continuous.sh` | `wspr.gold_continuous` | 10M | ~4 min |
| 5c | `populate_v6_clean.sh` | `wspr.gold_v6` | 10M | < 30 s |

```bash
bash /usr/share/ionis-core/scripts/populate_stratified.sh
bash /usr/share/ionis-core/scripts/populate_continuous.sh
bash /usr/share/ionis-core/scripts/populate_v6_clean.sh
```

Export CSV and transfer to the training host:

```bash
clickhouse-client --query "SELECT * FROM wspr.gold_v6 FORMAT CSV" \
    > /mnt/ai-stack/ionis-ai/ionis-training/data/gold_v6.csv

# Transfer to M3 Ultra via DAC link
scp data/gold_v6.csv gbeam@10.60.1.2:workspace/ionis-ai/ionis-training/data/
```

See [Gold Layer](../methodology/gold_layer.md) for lineage and verification.

## Phase 6: Verify

Run the validation tool and spot-check key tables:

```bash
db-validate --all
```

### Expected Row Counts

| Table | Expected |
|-------|----------|
| `solar.bronze` | ~17,840 |
| `wspr.bronze` | ~10,800,000,000 |
| `rbn.bronze` | ~2,184,000,000 |
| `contest.bronze` | ~234,000,000 |
| `wspr.callsign_grid` | ~38,600 |
| `wspr.balloon_callsigns_v2` | ~1,443 |
| `wspr.signatures_v2_terrestrial` | ~93,600,000 |
| `rbn.signatures` | ~56,700,000 |
| `contest.signatures` | ~6,300,000 |
| `wspr.silver` | ~4,430,000,000 |
| `wspr.gold_stratified` | 10,000,000 |
| `wspr.gold_continuous` | 10,000,000 |
| `wspr.gold_v6` | 10,000,000 |
