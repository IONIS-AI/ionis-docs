# Contest & RBN Tools

Four Go binaries for downloading and ingesting amateur radio contest logs
and Reverse Beacon Network spot data.

## contest-download

Downloads public Cabrillo logs from CQ and ARRL contest websites. Supports
15 contest series with configurable year/mode filtering and rate limiting.
Part of `ionis-apps` (Go binary).

```text
contest-download v3.0.2 — Contest Log Downloader

Usage: contest-download [flags]

Downloads public Cabrillo logs from CQ and ARRL contest websites.
Good neighbor: sequential requests, configurable delay, resume-friendly.

  -contest string
    	Contest key (use --list to see options, or 'all') (default "all")
  -delay duration
    	Delay between HTTP requests (default 3s)
  -dest string
    	Destination directory (default "/mnt/contest-logs")
  -dry-run
    	Fetch indexes and build manifests only, no log downloads
  -list
    	List available contests and exit
  -mode string
    	Download only this mode: ph, cw (empty = all modes)
  -refresh
    	Re-fetch index pages even if manifest exists
  -timeout duration
    	HTTP request timeout (default 1m0s)
  -year int
    	Download only this year (0 = all years)

Contests:
  cq-ww            CQ WW          CQ     modes: ph, cw         years: 2005-2025
  cq-wpx           CQ WPX         CQ     modes: ph, cw         years: 2008-2025
  cq-ww-rtty       CQ WW RTTY     CQ     modes: (single mode)  years: 2009-2024
  cq-wpx-rtty      CQ WPX RTTY    CQ     modes: (single mode)  years: 2012-2025
  cq-160           CQ 160         CQ     modes: ph, cw         years: 2022-2025
  ww-digi          WW Digi        CQ     modes: (single mode)  years: 2019-2025
  arrl-dx-cw       ARRL DX CW     ARRL   modes: (single mode)  years: 2018-2025
  arrl-dx-ph       ARRL DX Phone  ARRL   modes: (single mode)  years: 2018-2025
  arrl-10m         ARRL 10m       ARRL   modes: (single mode)  years: 2018-2024
  arrl-160m        ARRL 160m      ARRL   modes: (single mode)  years: 2018-2024
  arrl-ss-cw       ARRL SS CW     ARRL   modes: (single mode)  years: 2018-2024
  arrl-ss-ph       ARRL SS Phone  ARRL   modes: (single mode)  years: 2018-2024
  arrl-rtty        ARRL RTTY RU   ARRL   modes: (single mode)  years: 2018-2025
  arrl-digi        ARRL Digital   ARRL   modes: (single mode)  years: 2022-2025
  iaru-hf          IARU HF        ARRL   modes: (single mode)  years: 2018-2025

Examples:
  contest-download --list
  contest-download --contest cq-ww --year 2024 --mode cw
  contest-download --contest arrl-dx-cw --year 2024
  contest-download --dry-run
  contest-download --delay 5s
```

## contest-ingest

Walks contest log directories, parses Cabrillo V2/V3 headers and QSO lines,
normalizes bands via ADIF lookup, and bulk-inserts into `contest.bronze`.
Optionally enriches `wspr.callsign_grid` with grid locators.
Part of `ionis-apps` (Go binary).

```text
contest-ingest v3.0.2 — Parse Cabrillo contest logs into ClickHouse

Usage: contest-ingest [flags]

Walks --src/{contest}/{yearmode}/*.log, parses Cabrillo headers
and QSO lines, normalizes band via ADIF lookup, and inserts into
ClickHouse using ch-go native protocol with LZ4 compression.

  -batch int
    	Rows per INSERT batch (default 100000)
  -contest string
    	Process only this contest key (empty = all)
  -db string
    	ClickHouse database (default "contest")
  -enrich
    	Also insert GRID-LOCATOR into wspr.callsign_grid
  -host string
    	ClickHouse host:port (default "192.168.1.90:9000")
  -src string
    	Source directory with {contest}/{yearmode}/*.log (default "/mnt/contest-logs")
  -table string
    	ClickHouse table (default "bronze")
  -workers int
    	Parallel file workers (default 8)

Examples:
  contest-ingest --contest cq-ww --workers 4
  contest-ingest --enrich
  contest-ingest --src /mnt/contest-logs --host 10.60.1.1:9000
```

## rbn-download

Downloads daily ZIP archives of CW/RTTY spots from the Reverse Beacon Network.
Covers the full archive from 2009 to present (~6,183 files, ~21 GB).
Part of `ionis-apps` (Go binary).

```text
rbn-download v3.0.2 — Reverse Beacon Network Archive Downloader

Usage: rbn-download [flags]

Downloads daily ZIP archives of CW/RTTY spots from the RBN.
Each ZIP contains a CSV with 13 columns (callsign, freq, SNR, etc.).
Good neighbor: sequential requests, configurable delay, resume-friendly.

  -delay duration
    	Delay between HTTP requests (default 3s)
  -dest string
    	Destination directory (default "/mnt/rbn-data")
  -dry-run
    	Show what would be downloaded, don't fetch
  -from string
    	Start date (YYYY-MM-DD) (default "2009-02-21")
  -list
    	List available year ranges and estimated sizes
  -timeout duration
    	HTTP request timeout (default 2m0s)
  -to string
    	End date (YYYY-MM-DD, default: yesterday)
  -year int
    	Download only this year (0 = all years)

Data source: https://data.reversebeacon.net/rbn_history/
Archive range: 2009-02-21 to present (~6,183 files, ~21 GB)

Examples:
  rbn-download --list
  rbn-download --year 2024
  rbn-download --from 2024-01-01 --to 2024-12-31
  rbn-download --dry-run
  rbn-download --delay 5s
```

## rbn-ingest

Streams RBN daily ZIP archives into ClickHouse. Handles all three CSV format
eras (11-column 2009–2010, 13-column 2011+) with automatic detection.
Part of `ionis-apps` (Go binary).

```text
rbn-ingest v3.0.2 — Stream RBN ZIP archives into ClickHouse

Usage: rbn-ingest [flags]

Reads daily ZIP files from --src/{year}/*.zip, parses CSV,
normalizes band via ADIF lookup, and inserts into ClickHouse
using ch-go native protocol with LZ4 compression.

Handles all three RBN CSV format eras:
  2009-2010: 11 columns (no speed/tx_mode)
  2011+:     13 columns (speed + tx_mode)

  -batch int
    	Rows per INSERT batch (default 100000)
  -db string
    	ClickHouse database (default "rbn")
  -host string
    	ClickHouse host:port (default "192.168.1.90:9000")
  -src string
    	Source directory with {year}/*.zip (default "/mnt/rbn-data")
  -table string
    	ClickHouse table (default "bronze")
  -workers int
    	Parallel ZIP workers (default 8)
  -year int
    	Process only this year (0 = all)

Examples:
  rbn-ingest --year 2024 --workers 4
  rbn-ingest --workers 8
  rbn-ingest --src /mnt/rbn-data --host 10.60.1.1:9000
```
