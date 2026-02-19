# Operations & Maintenance

Scheduled jobs, health checks, and common operational procedures for a
running IONIS installation.

## Cron Schedule

Seven automated jobs keep solar indices and propagation data current.
Downloaders write to disk; ingesters read from disk into ClickHouse.

| Job | Schedule | Command | Purpose |
|-----|----------|---------|---------|
| `solar-live-update` | Every 15 min | `solar-live-update` | Real-time solar indices → `wspr.live_conditions` |
| `solar-history-load` | Every 6 hours | `solar-history-load` | Training-quality solar data → `solar.bronze` |
| `pskr-ingest` | Hourly at H+5 | `pskr-ingest` | JSONL files → `pskr.bronze` (watermark: `pskr.ingest_log`) |
| `rbn-download` | 16:00 UTC daily | `rbn-download` | Daily RBN ZIP archive → `/mnt/rbn-data` |
| `rbn-ingest` | 16:30 UTC daily | `rbn-ingest` | RBN ZIPs → `rbn.bronze` (watermark: `rbn.ingest_log`) |
| `wspr-download` | 18:00 UTC daily | `wspr-download` | Daily WSPR archive → `/mnt/wspr-data` |
| `wspr-turbo` | 19:00 UTC daily | `wspr-turbo` | WSPR archives → `wspr.bronze` (watermark: `wspr.ingest_log`) |

!!! note "Solar data freshness"
    `solar.bronze` (GFZ Potsdam source) lags ~1 day behind real-time. For
    live prediction and validation, use `wspr.live_conditions` which updates
    every 15 minutes from NOAA SWPC. SFI is published once daily (~20:00 UTC
    from Penticton); Kp updates every 3 hours.

## Daemons

### pskr-collector

The PSK Reporter MQTT collector runs as a systemd service, streaming ~300
HF spots/sec (~26M spots/day) to hourly-rotated gzip JSONL files.

```bash
# Check status
systemctl status pskr-collector

# View recent logs
journalctl -u pskr-collector --since "1 hour ago" --no-pager

# Restart after config change
sudo systemctl restart pskr-collector
```

Output files: `/mnt/pskr-data/YYYY/MM/DD/spots-HHMMSS.jsonl.gz`

## Health Checks

### Solar Data Freshness

```sql
-- Most recent solar record (should be within ~1 day)
SELECT max(date) FROM solar.bronze;

-- Live conditions (should be within ~15 min)
SELECT max(timestamp) FROM wspr.live_conditions;
```

### PSK Reporter Collection

```bash
# Service running?
systemctl is-active pskr-collector

# Today's spot count
clickhouse-client --query "
    SELECT count()
    FROM pskr.bronze
    WHERE toDate(timestamp) = today()
"
```

### ClickHouse Disk Usage

```sql
SELECT
    name,
    formatReadableSize(free_space) AS free,
    formatReadableSize(total_space) AS total,
    round(free_space / total_space * 100, 1) AS pct_free
FROM system.disks;
```

### Table Integrity

```bash
db-validate --all
```

## Common Operations

### Full Solar Refresh

Re-download and reload all historical solar data from GFZ Potsdam:

```bash
solar-backfill -ch-host 192.168.1.90:9000
```

This is idempotent — existing rows are replaced by primary key.

### Re-download a Contest Year

```bash
# Download a specific contest/year
contest-download -contest CQWW-SSB -year 2024 -dest /mnt/contest-logs

# Re-ingest (idempotent insert)
contest-ingest -host 192.168.1.90:9000 -src /mnt/contest-logs -enrich
```

### Replay PSKR Files After Schema Change

If the `pskr.bronze` schema changes, replay collected JSONL files:

```bash
# Stop the collector to avoid conflicts
sudo systemctl stop pskr-collector

# Full re-ingest (ignores watermark, reloads all files)
pskr-ingest --full --src /mnt/pskr-data --host 192.168.1.90:9000

# Restart collector
sudo systemctl start pskr-collector
```

### Watermark Bootstrap (New Install or Schema Change)

After a fresh install or schema change, bootstrap watermarks so
incremental mode knows what's already loaded:

```bash
# Prime all four ingest_log tables (marks files as loaded, row_count=0)
pskr-ingest --prime --src /mnt/pskr-data --host 192.168.1.90:9000
rbn-ingest --prime --src /mnt/rbn-data --host 192.168.1.90:9000
wspr-turbo --prime --source-dir /mnt/wspr-data --ch-host 192.168.1.90:9000
contest-ingest --prime --src /mnt/contest-logs --host 192.168.1.90:9000

# Verify watermark counts
clickhouse-client --query "
SELECT 'pskr' AS src, count() FROM pskr.ingest_log FINAL
UNION ALL SELECT 'rbn', count() FROM rbn.ingest_log FINAL
UNION ALL SELECT 'wspr', count() FROM wspr.ingest_log FINAL
UNION ALL SELECT 'contest', count() FROM contest.ingest_log FINAL
ORDER BY 1
FORMAT PrettyCompact
"
```

After priming, subsequent cron runs will only load new files.

### Full Re-ingest (Any Source)

All watermark-enabled ingesters support `--full` for complete reload:

```bash
rbn-ingest --full --src /mnt/rbn-data --host 192.168.1.90:9000
wspr-turbo --full --source-dir /mnt/wspr-data --ch-host 192.168.1.90:9000
contest-ingest --full --src /mnt/contest-logs --host 192.168.1.90:9000
```

`--full` drops partitions before reload and updates watermark entries.
Use `--dry-run` to preview what would be processed.

### Manual Solar Backfill

For periods where the automated cron missed updates:

```bash
solar-backfill -ch-host 192.168.1.90:9000
```

### Regenerate Signatures

After a bronze re-ingest or schema change, rebuild derived tables:

```bash
bash /usr/share/ionis-core/scripts/populate_callsign_grid.sh
bash /usr/share/ionis-core/scripts/populate_signatures.sh
bash /usr/share/ionis-core/scripts/populate_rbn_signatures.sh
bash /usr/share/ionis-core/scripts/populate_contest_signatures.sh
```
