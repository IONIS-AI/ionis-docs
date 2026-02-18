# IONIS Lab

Performance benchmarks for the IONIS sovereign infrastructure — ingestion,
query, and cross-system comparisons on 10.8 billion WSPR rows.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│              IONIS SOVEREIGN AI DATA CENTER                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INGEST ────────▶ STORE ────────▶ THINK                        │
│                                                                 │
│  Threadripper       ClickHouse        DeepSeek-R1-70B          │
│  9975WX             10.8B rows        RTX PRO 6000             │
│  24.67 Mrps         ~200 GB           96 GB VRAM               │
│  3.5 GB/s writes    60 GB/s scan      ~15 tok/s                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| Layer | Component | Capacity | Verified |
|-------|-----------|----------|----------|
| **Ingest** | wspr-turbo @ 24 workers | 24.67 Mrps (3.5 GB/s) | 2026-02-01 |
| **Store** | ClickHouse (wspr.bronze) | 10.8B rows, 60 GB/s scan | 2026-02-01 |
| **Think** | DeepSeek-R1-Distill-70B (FP8) | 96 GB VRAM, ~15 tok/s | 2026-02-02 |

## Hardware

### Control Node — Threadripper 9975WX

Primary ingestion and query engine.

| Spec | Value |
|------|-------|
| **CPU** | AMD Threadripper PRO 9975WX (32C/64T, 5.3 GHz boost, Zen 5) |
| **RAM** | 128 GB DDR5 (8-channel, ~384 GB/s bandwidth) |
| **GPU** | NVIDIA RTX PRO 6000 Blackwell (96 GB VRAM) |
| **Storage** | 3x NVMe — 1 TB OS, 3.6 TB ClickHouse, 3.6 TB working data |
| **OS** | Rocky Linux 9.7 |

I/O is decoupled: source files on one NVMe, ClickHouse writes to a separate
NVMe. No contention during ingestion.

### Sage Node — Mac Studio M3 Ultra

Model training and evaluation.

| Spec | Value |
|------|-------|
| **SoC** | Apple M3 Ultra |
| **RAM** | 96 GB unified memory |
| **Backend** | PyTorch MPS |
| **Role** | V20 training (100 epochs in 4h 16m) |

### Forge Node — EPYC 7302P

Backup, replica, and VM host (Proxmox).

| Spec | Value |
|------|-------|
| **CPU** | AMD EPYC 7302P (16C/32T, 3.0 GHz base, Zen 2) |
| **RAM** | 128 GB DDR4-3200 ECC (8-channel, ~204 GB/s bandwidth) |
| **GPU** | NVIDIA RTX 5080 (16 GB VRAM) |
| **Storage** | 4x Samsung 970 EVO Plus 1 TB (NVMe mirror), 8x Samsung 870 EVO 2 TB (RAIDZ2) |

### Storage Node — TrueNAS

NAS for bulk archive storage.

| Spec | Value |
|------|-------|
| **CPU** | AMD Ryzen 9 5950X (16C/32T, Zen 3) |
| **RAM** | 128 GB DDR4 ECC |
| **Storage** | 8x Seagate IronWolf Pro 14 TB (3-way + 4-way mirror, ~28 TB usable) |

### DAC Network

All inter-node links are direct-attach 10 Gbps point-to-point with jumbo
frames (MTU 9000). No switches.

| Link | Subnet | Endpoints | Latency |
|------|--------|-----------|---------|
| Thunderbolt 4 | `10.60.1.0/24` | 9975WX — M3 Ultra | ~0.19 ms |
| x710 SFP+ AOC | `10.60.2.0/24` | 9975WX — Proxmox/EPYC | ~0.12 ms |
| x710 SFP+ AOC | `10.60.3.0/24` | 9975WX — TrueNAS | ~0.03 ms |

### ZFS Archive Pool

HighPoint NVMe carrier with 4x Samsung 990 Pro 4 TB in a 2x2 ZFS mirror
(~7.12 TB usable) on the 9975WX.

| Dataset | Compression | Purpose |
|---------|-------------|---------|
| `wspr-data` | lz4 | WSPR raw CSV archives (.csv.gz) |
| `contest-logs` | zstd-9 | CQ contest Cabrillo logs |
| `rbn-data` | lz4 | RBN daily ZIP archives |
| `pskr-data` | lz4 | PSK Reporter MQTT collection (live) |

## Ingestion Benchmarks

All benchmarks on 10.8 billion WSPR rows using ch-go native protocol with
LZ4 wire compression.

### Threadripper 9975WX — Champion Results

**wspr-turbo (streaming from .gz archives):**

| Workers | Time | Throughput | I/O Rate | Effective Write | Memory |
|---------|------|------------|----------|-----------------|--------|
| 16 | 7m 54s | 22.77 Mrps | 399 MB/s | 1.74 GB/s | 45.3 GB |
| **24** | **7m 18s** | **24.67 Mrps** | **433 MB/s** | **1.88 GB/s** | **71.5 GB** |

**wspr-shredder (pre-decompressed CSV, 878 GB):**

| Workers | Time | Throughput | I/O Rate |
|---------|------|------------|----------|
| **24** | **8m 15s** | **21.81 Mrps** | ~1.81 GB/s |

**wspr-parquet-native (Parquet files, 109 GB):**

| Workers | Time | Throughput | I/O Rate |
|---------|------|------------|----------|
| **24** | **9m 39s** | **17.02 Mrps** | 193 MB/s |

### Ingestion Leaderboard

| Method | Throughput | Time | Bottleneck | Verdict |
|--------|------------|------|------------|---------|
| **wspr-turbo (gzip)** | **24.67 Mrps** | 7m 18s | Database merge | **Champion** |
| wspr-shredder (CSV) | 21.81 Mrps | 8m 15s | Database merge | Runner-up |
| wspr-parquet-native | 17.02 Mrps | 9m 39s | Library overhead | Slowest |

### Key Findings

- **Compression is free.** wspr-turbo (gzip) beats wspr-shredder (raw CSV)
  because both hit the same ClickHouse merge ceiling at ~3.5 GB/s sustained
  writes. Decompression overhead is invisible.
- **The 3.5 GB/s wall.** All three tools hit ClickHouse's background merge
  limit. The bottleneck is the database, not the ingester.
- **The Parquet paradox.** Parquet is faster for queries but 30% slower for
  ingestion due to parquet-go serialization overhead.
- **24 workers optimal.** 8.3% faster than 16 workers, uses ~72 GB RAM.
  32 workers exceeded 128 GB and OOM'd.
- **Thermals.** 74 C at full load (5.0 GHz sustained), no throttling.
- **LLM coexistence.** Running DeepSeek-R1-70B (SGLang) concurrently had
  less than 1% impact on ingestion throughput.

## Query Benchmarks

### Threadripper 9975WX — 10.8B Rows

```sql
SELECT callsign, avg(snr) AS avg_snr, count(*) AS count
FROM wspr.bronze
GROUP BY callsign
ORDER BY count DESC
LIMIT 10;
```

| Metric | Result |
|--------|--------|
| Time | **3.050 sec** |
| Rows processed | 10.80 billion |
| Throughput | **3.54 billion rows/s** |
| Data scanned | 183.57 GB |
| Scan rate | **60.19 GB/s** |
| Peak memory | 828.79 MiB |

**Top 5 transmitters by spot count:**

| Callsign | Avg SNR | Spots |
|----------|---------|-------|
| WW0WWV | -12.79 dB | 105.96M |
| WB6CXC | -12.47 dB | 70.83M |
| NI5F | -11.68 dB | 58.74M |
| DL6NL | -17.00 dB | 53.28M |
| TA4/G8SCU | -12.46 dB | 49.21M |

## Cross-System Comparison

### Ingestion (wspr-turbo)

| System | Workers | Time | Throughput | vs 9950X3D |
|--------|---------|------|------------|------------|
| **Threadripper 9975WX** | **24** | **7m 18s** | **24.67 Mrps** | **2.79x** |
| Threadripper 9975WX | 16 | 7m 54s | 22.77 Mrps | 2.58x |
| Ryzen 9 9950X3D | 16 | 20m 13s | 8.83 Mrps | baseline |
| EPYC 7302P | 16 | 23m 27s | 7.63 Mrps | 0.86x |

### Query (GROUP BY over 10.8B rows)

| System | Time | Scan Rate | Winner |
|--------|------|-----------|--------|
| **Threadripper 9975WX** | **3.05s** | **60.19 GB/s** | Yes |
| Ryzen 9 9950X3D | 3.88s | ~47 GB/s | |
| EPYC 7302P | 4.54s | ~40 GB/s | |

### System Specifications

| Spec | Threadripper 9975WX | 9950X3D | EPYC 7302P |
|------|---------------------|---------|------------|
| Cores / Threads | 32C/64T | 16C/32T | 16C/32T |
| Architecture | Zen 5 | Zen 5 (3D V-Cache) | Zen 2 |
| Boost clock | 5.3 GHz | 5.4 GHz | 3.0 GHz |
| RAM | 128 GB DDR5 | 64 GB DDR5-6000 | 128 GB DDR4-3200 ECC |
| Memory channels | 8 | 2 | 8 |
| Memory bandwidth | ~384 GB/s | ~96 GB/s | ~204 GB/s |

The Threadripper 9975WX dominates all workloads. Eight-channel DDR5 combined
with 32 Zen 5 cores finally unlocks the memory bandwidth needed for
analytical queries while maintaining the single-threaded performance needed
for gzip decompression.

## wspr-turbo Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  .csv.gz file   │────▶│  Stream Decomp   │────▶│  Vectorized     │
│  (on disk)      │     │  (klauspost/gzip)│     │  CSV Parser     │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  ClickHouse     │◀────│  ch-go Native    │◀────│  Double Buffer  │
│                 │     │  Blocks + LZ4    │     │  Fill A/Send B  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

- **Stream decompress**: klauspost/gzip (ASM-optimized, no disk extraction)
- **Vectorized parse**: custom scanner fills columnar slices directly (no row
  structs)
- **Double buffer**: Block A fills while Block B sends over the wire
- **Zero-alloc hot path**: sync.Pool for 1M-row column blocks (~490 GC cycles
  for 10B rows)
- **Native protocol**: proto.ColUInt64, proto.ColDateTime — binary wire format
  with LZ4 compression

## End-to-End Pipeline Comparison

**Threadripper 9975WX:**

| Pipeline | Steps | Total Time | Temp Disk | Throughput |
|----------|-------|------------|-----------|------------|
| **wspr-turbo streaming** | Stream from .gz | **7m 18s** | **0 GB** | **24.67 Mrps** |
| pigz + wspr-shredder | Decompress + ingest | 9m 31s | 878 GB | 21.81 Mrps |
| pigz + parquet-native | Decompress + convert + ingest | ~12m | 987 GB | 17.02 Mrps |

wspr-turbo requires zero intermediate storage. The "compression is free"
finding means there is no benefit to pre-decompressing archives — the
ClickHouse merge wall is the bottleneck, not gzip decompression.
