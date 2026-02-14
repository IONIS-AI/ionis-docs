# Operations & Maintenance

Scheduled jobs, health checks, and common operational procedures for a
running IONIS installation.

## Cron Schedule

Five automated jobs keep solar indices and propagation data current.

| Job | Schedule | Command | Purpose |
|-----|----------|---------|---------|
| `solar-live-update` | Every 15 min | `solar-live-update` | Real-time solar indices → `wspr.live_conditions` |
| `solar-history-load` | Every 6 hours | `solar-history-load` | Training-quality solar data → `solar.bronze` |
| `pskr-ingest` | Hourly at H+5 | `pskr-ingest` | JSONL files → `pskr.bronze` |
| `rbn-download` | 16:00 UTC daily | `rbn-download` | Daily RBN ZIP archive → `/mnt/rbn-data` |
| `wspr-download` | 18:00 UTC daily | `wspr-download` | Daily WSPR archive → `/mnt/wspr-data` |

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

# Re-ingest from stored files
pskr-ingest -src /mnt/pskr-data -host 192.168.1.90:9000

# Restart collector
sudo systemctl start pskr-collector
```

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
