# Database Apps

Two shell scripts and one Go binary for managing the ClickHouse environment.

## ionis-db-init

Idempotent schema initializer for all ClickHouse databases and tables.
Executes DDL files to create or recreate the full schema (wspr, solar,
contest, rbn, data_mgmt).
Part of `ionis-core` (Shell script).

```text
Usage: ionis-db-init [OPTIONS]
Options:
  --auto-confirm   Skip confirmation prompts
  --force          Recreate tables (DESTROYS DATA)
  --dry-run        Show what would be done without executing
  --stamp-version  Record installed version in data_mgmt.lab_versions
  -h, --help       Show this help message
```

## ionis-env

Standardized environment variables for the AI Lab. Exports ClickHouse
connection settings, storage paths (RAID-0 NVMe optimized), application
paths (FHS-compliant), and performance tuning defaults. Designed to be
sourced, not executed directly.
Part of `ionis-core` (Shell script).

```text
# Usage: source ionis-env

IONIS Environment (3.0.2) Loaded.
  WSPR Data.......: /mnt/ai-stack/wspr-data
  Solar Data......: /mnt/ai-stack/solar-data
  ClickHouse Data.: /mnt/ai-stack/clickhouse
  ClickHouse Host.: localhost:9000
```

## db-validate

Validates ClickHouse table row counts across all four data domains. Reports
pass/fail status with actual counts. Useful for post-ingest verification.
Part of `ionis-apps` (Go binary, not yet installed to PATH).

```text
db-validate v3.0.2 — Validate ClickHouse table row counts

Usage: db-validate [flags]

  -all
    	Validate all tables (default if no flags)
  -contest
    	Validate contest tables
  -host string
    	ClickHouse host:port (default "192.168.1.90:9000")
  -rbn
    	Validate rbn tables
  -solar
    	Validate solar tables
  -wspr
    	Validate wspr tables

Examples:
  db-validate --all
  db-validate --wspr --solar
  db-validate --rbn --host 10.60.1.1:9000
```
