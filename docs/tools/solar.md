# Solar Pipeline Tools

Three Go binaries and three shell scripts for downloading and ingesting
solar flux, geomagnetic, and X-ray data.

## solar-download

Multi-source downloader covering 10 NOAA, SIDC, and GOES endpoints. Downloads
daily/monthly sunspot numbers, F10.7 flux, Kp indices, and X-ray flux.
Part of `ki7mt-ai-lab-apps` (Go binary).

```text
solar-download v2.3.0 - Solar Data Downloader

Usage: solar-download [OPTIONS]

Downloads solar flux data from NOAA and SIDC sources.

  -dest string
    	Destination directory (default "/mnt/ai-stack/solar-data/raw")
  -list
    	List available data sources
  -source string
    	Source to download (or 'all') (default "all")
  -timeout duration
    	HTTP timeout per download (default 1m0s)

Data Sources:
  sidc_daily      SIDC daily sunspot numbers (1818-present)
  sidc_monthly    SIDC monthly sunspot numbers (1749-present)
  noaa_sfi        NOAA solar cycle indices (F10.7 flux, SSN)
  noaa_predicted  NOAA predicted solar cycle
  penticton_daily Penticton 10.7cm daily flux
  noaa_sfi_summary NOAA 10.7cm solar flux summary (live)
  noaa_sfi_30day  NOAA 10.7cm solar flux (30-day history)
  noaa_kp         NOAA planetary K-index (3-hourly geomagnetic)
  goes_xray       GOES X-ray flux (6-hour rolling window)
  goes_xray_7day  GOES X-ray flux (7-day history for training)
```

## solar-ingest

Parses and ingests SIDC CSV, NOAA JSON, and GOES JSON files into ClickHouse
`solar.bronze`. Supports truncate-and-reload for clean refreshes.
Part of `ki7mt-ai-lab-apps` (Go binary).

```text
solar-ingest v2.3.0 - Solar Flux Data Ingester

Usage: solar-ingest [OPTIONS] [files...]

Ingests solar flux data from NOAA/SIDC/GOES sources into ClickHouse.

Supported formats:
  - SIDC CSV (sidc_*.csv): Daily sunspot numbers
  - SFI JSON (sfi_daily_flux.txt): NOAA solar flux indices
  - Kp JSON (noaa_kp_index.json): Planetary K-index (3-hourly)
  - X-ray JSON (goes_xray_flux.json): GOES X-ray flux (6-hour)

  -ch-db string
    	ClickHouse database (default "solar")
  -ch-host string
    	ClickHouse address (default "127.0.0.1:9000")
  -ch-table string
    	ClickHouse table (default "bronze")
  -source-dir string
    	Solar data source directory (default "/mnt/ai-stack/solar-data/raw")
  -truncate
    	Truncate table before insert
```

## solar-backfill

Downloads and parses the GFZ Potsdam composite file containing SSN, SFI (F10.7),
and 3-hourly Kp/ap indices from 1932 to present. Inserts into `solar.bronze`.
Part of `ki7mt-ai-lab-apps` (Go binary).

```text
solar-backfill v2.3.0 — Historical Solar Index Backfill (GFZ Potsdam)

Downloads SSN, SFI (F10.7), and 3-hourly Kp/ap from GFZ Potsdam
and inserts into ClickHouse solar.bronze.

Source: https://kp.gfz-potsdam.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt

Usage: solar-backfill [OPTIONS]

  -ch-db string
    	ClickHouse database (default "solar")
  -ch-host string
    	ClickHouse native protocol address (default "127.0.0.1:9000")
  -ch-table string
    	ClickHouse table (default "bronze")
  -dry-run
    	Parse only, no ClickHouse insert
  -end string
    	End date (default: today)
  -file string
    	Local GFZ file (skip download)
  -start string
    	Start date (YYYY-MM-DD) (default "2020-01-01")
  -timeout int
    	HTTP download timeout (seconds) (default 120)

Examples:
  solar-backfill -ch-host 192.168.1.90:9000 -start 2020-01-01
  solar-backfill -file /tmp/Kp_ap_Ap_SN_F107_since_1932.txt -dry-run
```

## solar-refresh

Full refresh pipeline: downloads fresh solar/geomagnetic data, truncates
`solar.bronze`, and reloads all sources.
Part of `ki7mt-ai-lab-core` (Shell script).

```text
solar-refresh v2.0.5 - Solar Data Refresh Utility

Usage: solar-refresh [OPTIONS]

Downloads fresh solar/geomagnetic data and performs a clean reload
into ClickHouse (truncate + ingest).

Options:
  -d, --dest DIR     Destination directory (default: /mnt/ai-stack/solar-data/raw)
  -n, --no-truncate  Append instead of truncate + reload
  -q, --quiet        Suppress output
  -h, --help         Show this help message

Environment:
  SOLAR_DATA_DIR     Override default data directory

Examples:
  solar-refresh                 # Full refresh (truncate + reload)
  solar-refresh -n              # Append new data only
  solar-refresh -d /tmp/solar   # Use alternate directory
```

## solar-live-update

Lightweight updater for the Now-Casting pipeline. Designed for 15-minute cron
intervals to keep near-real-time solar indices current.
Part of `ki7mt-ai-lab-core` (Shell script).

```text
Usage: solar-live-update [--refresh]
  --refresh    Run solar-download first
```

## solar-history-load

Training data loader for the historical solar index pipeline. Designed for
6-hour cron intervals to keep training datasets aligned with latest observations.
Part of `ki7mt-ai-lab-core` (Shell script).

```text
Usage: solar-history-load [--download]
  --download    Download fresh data from NOAA SWPC first

Without --download, uses existing files in /mnt/ai-stack/solar-data/raw
```
