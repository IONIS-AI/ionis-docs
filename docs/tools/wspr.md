# WSPR Ingestion Apps

Four Go binaries for downloading and ingesting WSPR spot data into ClickHouse.

## wspr-turbo

The primary ingestion engine. Streams tar.gz/csv.gz archives directly into ClickHouse
using zero-copy decompression and double-buffered native blocks — no intermediate disk I/O.
Part of `ionis-apps` (Go binary).

```text
wspr-turbo v3.0.2 - Zero-Copy Streaming Pipeline

Usage: wspr-turbo [OPTIONS] [archives...]

Streams tar.gz/csv.gz directly to ClickHouse Native Blocks.
No intermediate disk I/O - bypasses the 'File Penalty'.

Architecture:
  - Stream decompression (klauspost/gzip, ASM-optimized)
  - Vectorized CSV parsing (columnar buffers)
  - Double-buffering (fill while sending)
  - sync.Pool (zero allocation after warmup)
  - ch-go native protocol with LZ4

  -block-size int
    	Rows per native block (default 1000000)
  -ch-db string
    	ClickHouse database (default "wspr")
  -ch-host string
    	ClickHouse address (default "127.0.0.1:9000")
  -ch-table string
    	ClickHouse table (default "bronze")
  -report-dir string
    	Report output directory (default "/mnt/ai-stack/wspr-data/reports-turbo")
  -source-dir string
    	Archive source directory (default "/scratch/ai-stack/wspr-data/archives")
  -workers int
    	Parallel archive workers (default 16)
```

## wspr-shredder

Maximum throughput ingester for uncompressed CSV files. Uses 1 MB read buffers and
zero-allocation CSV parsing to saturate PCIe 5.0 lanes.
Part of `ionis-apps` (Go binary).

```text
wspr-shredder v3.0.2 - Maximum Throughput WSPR Ingester

Usage: wspr-shredder [OPTIONS] [path|files...]

If no paths specified, uses -source-dir default.

Optimizations:
  - ch-go native protocol (fastest ClickHouse client)
  - 1MB read buffers (bufio.NewReaderSize)
  - csv.Reader with ReuseRecord (zero-allocation)
  - Per-file workers to saturate PCIe 5.0 lanes

  -ch-db string
    	ClickHouse database (default "wspr")
  -ch-host string
    	ClickHouse address (default "127.0.0.1:9000")
  -ch-table string
    	ClickHouse table (default "bronze")
  -report-dir string
    	Report output directory (default "/mnt/ai-stack/wspr-data/reports-shredder")
  -source-dir string
    	Default CSV source directory (default "/scratch/ai-stack/wspr-data/csv")
  -workers int
    	Number of parallel file workers (default 16)
```

## wspr-parquet-native

Native Go Parquet reader for ingesting Parquet-format WSPR data. Avoids ClickHouse
`file()` function restrictions by reading client-side with `parquet-go`.
Part of `ionis-apps` (Go binary).

```text
wspr-parquet-native v3.0.2 - Native Go Parquet Ingester

Usage: wspr-parquet-native [OPTIONS] [path|files...]

If no paths specified, uses -source-dir default.

Features:
  - Native Go Parquet reading (parquet-go)
  - ch-go native protocol with LZ4
  - No ClickHouse file() restrictions
  - Parallel file processing

  -ch-db string
    	ClickHouse database (default "wspr")
  -ch-host string
    	ClickHouse address (default "127.0.0.1:9000")
  -ch-table string
    	ClickHouse table (default "bronze")
  -report-dir string
    	Report output directory (default "/mnt/ai-stack/wspr-data/reports-parquet-native")
  -source-dir string
    	Default Parquet source directory (default "/scratch/ai-stack/wspr-data/parquet")
  -workers int
    	Number of parallel file workers (default 8)
```

## wspr-download

Parallel archive downloader for WSPR spot data from wsprnet.org. Uses ETag validation
to detect updated files and supports configurable rate limiting.
Part of `ionis-apps` (Go binary).

```text
wspr-download v3.0.2 — WSPR Archive Downloader

Usage: wspr-download [flags]

Downloads WSPR spot archives from wsprnet.org.
Archives are monthly .csv.gz files (~200MB-1GB each).
Uses ETag validation to detect updated files (e.g. end-of-month finalization).
Good neighbor: configurable workers/delay, resume-friendly.

  -delay duration
    	Delay between HTTP requests per worker (default 1s)
  -dest string
    	Destination directory (default "/mnt/wspr-data")
  -end string
    	End date (YYYY-MM, default: current month)
  -force
    	Re-download all files regardless of ETag
  -list
    	List files without downloading
  -start string
    	Start date (YYYY-MM) (default "2008-03")
  -timeout duration
    	HTTP timeout per download (default 5m0s)
  -workers int
    	Parallel download workers (default 4)

Data source: https://wsprnet.org/archive
Archive range: 2008-03 to present (~200 files)

Examples:
  wspr-download                              # Download all, skip unchanged
  wspr-download --start 2024-01 --end 2024-12  # Download 2024 only
  wspr-download --list                        # List files without downloading
  wspr-download --workers 2 --delay 3s        # Be extra polite
  wspr-download --force                       # Re-download everything
```
