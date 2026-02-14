# PSK Reporter Tools

Real-time MQTT spot collector for PSK Reporter reception data.

PSK Reporter ([pskreporter.info](https://pskreporter.info)) is the largest
real-time amateur radio reception report network, created by **Philip
Gladstone, N1DQ**. Over 27,000 active monitors contribute millions of
FT8/FT4/WSPR spots daily. The MQTT real-time feed is provided by **Tom
Sevart, M0LTE**.

## pskr-collector

Long-running MQTT daemon that subscribes to the PSK Reporter feed, parses
JSON spots, normalizes bands via ADIF lookup, and writes hourly-rotated
gzip JSONL files to `/mnt/pskr-data`. Part of `ionis-apps` (Go binary).

This is stage 1 of a two-stage pipeline:

1. **Collect** (this tool): MQTT &rarr; gzip JSONL files on ZFS
2. **Ingest** (`pskr-ingest`): JSONL &rarr; ClickHouse `pskr.bronze`

Both stages are live. `pskr-ingest` runs hourly via cron, using a watermark
table (`pskr.ingest_log`) to track loaded files for incremental processing.

The disk-first design provides durability (no data loss if ClickHouse is
down), replayability (re-ingest after schema changes), and consistency
with the WSPR/RBN/contest pipeline pattern.

```text
pskr-collector v3.0.2 — PSK Reporter MQTT real-time spot collector

Usage: pskr-collector [flags]

Subscribes to PSK Reporter MQTT feed and writes hourly-rotated
gzip JSONL files to --outdir/YYYY/MM/DD/spots-HHMMSS.jsonl.gz.

This is a long-running daemon. Use Ctrl+C or SIGTERM for graceful shutdown.

  -broker string
    	MQTT broker address (default "mqtt.pskreporter.info:1883")
  -buffer int
    	Channel buffer size (default 100000)
  -client-id string
    	MQTT client ID (default: auto-generated)
  -hf-only
    	Filter to HF bands only (160m-10m) (default true)
  -outdir string
    	Output directory for JSONL files (default "/mnt/pskr-data")
  -rotate duration
    	File rotation interval (default 1h0m0s)
  -stats duration
    	Stats reporting interval (default 1m0s)
  -topic string
    	MQTT topic filter (default "pskr/filter/v2/#")

Examples:
  pskr-collector
  pskr-collector --hf-only=false
  pskr-collector --rotate 30m --outdir /tmp/pskr-test
  pskr-collector --topic 'pskr/filter/v2/20m/#'
```

### Output Format

Hourly-rotated gzip JSONL files organized by date:

```
/mnt/pskr-data/
└── 2026/
    └── 02/
        └── 09/
            ├── spots-150000.jsonl.gz
            ├── spots-160000.jsonl.gz
            └── ...
```

Each line is a JSON object:

```json
{"ts":"2026-02-09T22:42:30Z","sc":"K1UHF","sg":"FN42","rc":"EA8BFK","rg":"IL38bo","f":7076312,"band":105,"mode":"FT8","snr":-12}
```

| Field | Description |
|-------|-------------|
| `ts` | Timestamp (UTC, ISO 8601) |
| `sc` | Sender callsign |
| `sg` | Sender grid (4-6 char Maidenhead, empty if unavailable) |
| `rc` | Receiver callsign |
| `rg` | Receiver grid (4-6 char Maidenhead) |
| `f` | Frequency in Hz |
| `band` | ADIF band ID (102-111 for HF) |
| `mode` | Mode (FT8, FT4, WSPR, JS8, CW, etc.) |
| `snr` | Signal-to-noise ratio in dB (machine-decoded) |

### Observed Data Quality

From a 30-second test run (7,607 spots):

| Metric | Value |
|--------|-------|
| Throughput | ~300 HF spots/sec sustained |
| SNR range | -34 to +38 dB (mean -9.5) |
| Non-zero SNR | 95.8% |
| Sender grids present | 14.7% |
| Receiver grids present | 28.0% |

Mode distribution: 88.7% FT8, 9.1% WSPR, 1.5% FT4, 0.5% JS8, 0.1% CW.
All 10 HF bands represented (160m through 10m).

### MQTT Details

- **Broker**: `mqtt.pskreporter.info:1883` (anonymous, no auth)
- **Protocol**: MQTT v3.1.1, QoS 0 (at-most-once)
- **Topic**: `pskr/filter/v2/{band}/{mode}/{sendercall}/{receivercall}/{senderlocator}/{receiverlocator}/{sendercountry}/{receivercountry}`
- **Wildcard**: `pskr/filter/v2/#` subscribes to all spots
- **Auto-reconnect**: Built-in with exponential backoff (1s to 60s)

### Running as a Service

A systemd unit file is provided in `ionis-apps/scripts/pskr-collector.service`:

```bash
# Install the service
sudo cp scripts/pskr-collector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pskr-collector

# Check status
systemctl status pskr-collector

# Follow logs
journalctl -u pskr-collector -f

# Stop collection
sudo systemctl stop pskr-collector
```

The unit runs as `ki7mt:ki7mt`, restarts on failure (30s delay), uses `SIGTERM` for
graceful shutdown (flushes buffers), and is hardened with `ProtectSystem=strict` and
`ReadWritePaths=/mnt/pskr-data`.

Alternatively, for quick testing via tmux:

```bash
tmux new-session -d -s pskr 'pskr-collector 2>&1 | tee /var/log/pskr-collector.log'
```

### Estimated Collection Rates

At ~300 HF spots/sec: **~26M spots/day**, **~780M spots/month**.
At ~19 bytes/spot compressed: **~15 GB/year** on ZFS (lz4).
With `--hf-only=false`: higher volume including VHF/UHF/microwave.

### ClickHouse Schema

The `pskr.bronze` table is defined in `ionis-core/src/22-pskr_schema_v1.sql`:

```sql
CREATE TABLE IF NOT EXISTS pskr.bronze (
    timestamp      DateTime,
    sender_call    String,
    sender_grid    String,
    receiver_call  String,
    receiver_grid  String,
    frequency      UInt64,
    band           Int32,
    mode           LowCardinality(String),
    snr            Int16
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (band, timestamp, sender_grid, receiver_grid);
```

### Data Source Attribution

PSK Reporter is created and operated by **Philip Gladstone, N1DQ**.
The MQTT real-time feed is provided by **Tom Sevart, M0LTE**.
We gratefully acknowledge their contributions to the amateur radio community.
