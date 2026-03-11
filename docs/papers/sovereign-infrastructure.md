---
title: "Sovereign Infrastructure for Citizen Science"
subtitle: "Building a Self-Hosted Research Lab for Radio Propagation Analysis"
author:
  - "Greg Beam, KI7MT"
affiliation: "KI7MT Sovereign AI Lab"
date: "February 26, 2026"
version: "1.1"
status: "RELEASE"
abstract: |
  This paper documents the design, implementation, and benchmarking of a self-hosted research computing infrastructure for HF radio propagation prediction. The system ingests 10.9 billion WSPR observations, 2.26 billion Reverse Beacon Network spots, and 552 million PSK Reporter spots, correlates them with solar indices from 10 NOAA/SIDC endpoints, and trains neural network models entirely on local hardware—14.68 billion rows totaling 263 GiB on disk. We demonstrate that a carefully architected home lab can achieve 24.67 million rows per second ingestion, 60 GB/s analytical query throughput, and 30 tokens/second local LLM inference—performance sufficient for serious scientific research without cloud dependencies. The total hardware investment of approximately $28,000 provides capabilities that would cost $40,000–214,000 annually in cloud compute. This infrastructure enables the IONIS (Ionospheric Neural Inference System) project, which applies machine learning to one of the largest curated amateur radio propagation datasets we are aware of.
keywords:
  - Amateur radio
  - HF propagation
  - WSPR
  - ClickHouse
  - Self-hosted infrastructure
  - Citizen science
  - Machine learning
toc: true
---

## 1. Introduction

### 1.1 Motivation

Amateur radio propagation prediction has traditionally relied on theoretical models like VOACAP and ICEPAC, which use simplified ionospheric physics (Davies, 1990) with monthly medians and smoothed parameters (Lane et al., 1993). These models miss real-world phenomena: Sporadic-E openings, gray-line enhancement, geomagnetic storm impacts, and intra-day variability.

The WSPR (Weak Signal Propagation Reporter) network, created by Joe Taylor (K1JT), provides a fundamentally different approach: empirical observation at global scale. Since 2008, WSPR has accumulated over 10 billion machine-decoded propagation observations with calibrated signal-to-noise ratios, precise timestamps, and geographic coordinates for both transmitter and receiver.

This dataset represents an unprecedented resource for data-driven propagation prediction. However, working with 10+ billion rows requires serious computing infrastructure—infrastructure that historically meant expensive cloud services or institutional computing clusters.

This paper demonstrates that a self-hosted "sovereign" infrastructure can process this data at scale, enabling individual researchers and small teams to conduct serious scientific work without external dependencies or recurring cloud costs.

### 1.2 Design Philosophy

The infrastructure follows three core principles:

1. **Sovereignty**: No cloud dependencies for core research capabilities. All data, models, and inference run on local hardware. This eliminates recurring costs, ensures data privacy, and enables operation during network outages.

2. **Performance at Scale**: The system must handle 10+ billion rows efficiently—not just storage, but analytical queries, feature engineering, and model training at interactive speeds.

3. **Reproducibility**: Every data pipeline, training run, and validation test is deterministic and auditable. Configuration lives in version control. Results are reproducible across hardware.

### 1.3 Contributions

This paper makes the following contributions:

- **Architecture documentation** for a multi-node research computing cluster using commodity hardware
- **Benchmarking methodology** with reproducible results for ingestion, query, and inference workloads
- **Cost analysis** comparing self-hosted infrastructure to equivalent cloud services
- **Practical guidance** for amateur radio operators and citizen scientists building similar systems

---

## 2. Hardware Architecture

### 2.1 System Overview

The infrastructure consists of three primary compute nodes connected by a dedicated 10 Gbps direct-attach network:

| Node | Role | Primary Workload |
|------|------|------------------|
| **Control Node** (Threadripper 9975WX) | Ingestion, database, inference | ClickHouse, GPU inference |
| **Sage Node** (Mac Studio M3 Ultra) | Model training | PyTorch MPS backend |
| **Forge Node** (EPYC 7302P) | Backup, validation, VM host | Proxmox, replica services |

### 2.2 Control Node: Threadripper 9975WX

The primary compute node handles data ingestion, analytical queries, and large language model inference.

**Specifications:**

| Component | Details |
|-----------|---------|
| CPU | AMD Threadripper PRO 9975WX (32C/64T, Zen 5, 5.3 GHz boost) |
| Memory | 128 GB DDR5 (8-channel, ~384 GB/s bandwidth) |
| GPU | NVIDIA RTX PRO 6000 Blackwell (96 GB VRAM) |
| Storage | Micron 7450 PRO 960 GB (OS) + 2× Samsung 9100 PRO 4 TB (data) + HighPoint Rocket 1504 with 4× Samsung 990 PRO 4 TB (archive) |
| Network | 10 GbE (motherboard), Intel x710-DA4 (quad SFP+) |
| PSU | Seasonic Prime TX-1600 (1600W Titanium, ATX 3.1) |
| OS | Rocky Linux 9.7 |

**Storage Layout:**

The critical insight for high-throughput ingestion is I/O decoupling. Source files and database writes use separate NVMe devices:

| Device | Model | Mount | Size | Purpose |
|--------|-------|-------|------|---------|
| nvme5n1 | Micron 7450 PRO | `/` (boot/OS) | 960 GB | Operating system |
| nvme0n1 | Samsung SSD 9100 PRO | `/data/working` | 3.6 TB | Source files, working data |
| nvme1n1 | Samsung SSD 9100 PRO | `/var/lib/clickhouse` | 3.6 TB | ClickHouse data |
| nvme2-6 | Samsung 990 PRO × 4 | ZFS pool | 14.4 TB raw | Archive storage (via HighPoint Rocket 1504) |

The Samsung 9100 PRO (PM9E1) enterprise drives handle the hot read/write paths. The critical insight for high-throughput ingestion is I/O decoupling — source files and database writes use separate NVMe devices, eliminating I/O contention and enabling the system to sustain 24.67 Mrps ingestion rates.

**Archive Storage (HighPoint Rocket 1504 + 4× Samsung 990 PRO 4TB):**

A ZFS pool on the HighPoint NVMe adapter provides compressed archival storage:

| Dataset | Compression | Content |
|---------|-------------|---------|
| `wspr-data` | lz4 | WSPR CSV archives (185 GB compressed) |
| `contest-logs` | zstd-9 | CQ contest Cabrillo logs |
| `rbn-data` | lz4 | Reverse Beacon Network archives |
| `pskr-data` | lz4 | PSK Reporter live collection |

### 2.3 Sage Node: Mac Studio M3 Ultra

The training node runs PyTorch model development using Apple's Metal Performance Shaders (MPS) backend.

**Specifications:**

| Component | Details |
|-----------|---------|
| SoC | Apple M3 Ultra (24-core CPU, 76-core GPU) |
| Memory | 96 GB unified memory |
| Storage | 2 TB internal SSD |
| Network | Thunderbolt 4 (10 Gbps to Control Node) |
| OS | macOS 15 |

The M3 Ultra's unified memory architecture eliminates CPU-GPU data transfer overhead, making it efficient for iterative model development. Training runs of 100 epochs on 38 million samples complete in approximately 4 hours.

### 2.4 Forge Node: EPYC 7302P

The backup and validation node runs Proxmox for virtualization and provides replica services.

**Specifications:**

| Component | Details |
|-----------|---------|
| Motherboard | ASRock Rack ROME8D-2T (dual-socket EPYC) |
| CPU | AMD EPYC 7302P (16C/32T, 3.0 GHz base) |
| Memory | 128 GB DDR4-3200 ECC (8-channel) |
| GPU | NVIDIA RTX 5080 (16 GB VRAM) |
| Boot | Micron 7450 PRO (enterprise NVMe) |
| NVMe Pool | 4× Samsung 970 EVO Plus 1TB (2× mirror, 1.76 TB) |
| SAS HBA | LSI 9300-8i |
| SSD Pool | 8× Samsung 870 EVO 2TB (RAIDZ2, 10.8 TB) |
| Network | Intel x710-DA4, Mellanox dual-port 25 GbE |
| OS | Proxmox VE 9.1 |

### 2.5 Network Architecture

All inter-node communication uses direct-attach cables with jumbo frames (MTU 9000), eliminating switch latency:

| Link | Cable Type | Subnet | Latency |
|------|------------|--------|---------|
| 9975WX ↔ M3 Ultra | Thunderbolt 4 | Subnet A | 0.19 ms |
| 9975WX ↔ Proxmox | SFP+ AOC | Subnet B | 0.12 ms |
| 9975WX ↔ TrueNAS | SFP+ AOC | Subnet C | 0.03 ms |

This "DAC Network" (Direct Attach Copper) provides 10 Gbps point-to-point bandwidth with sub-millisecond latency. Training scripts on the M3 query ClickHouse on the 9975WX at `<control-node>:8123` with negligible network overhead.

---

## 3. Software Stack

### 3.1 ClickHouse: Analytical Database

ClickHouse v26.1 serves as the primary data store and analytical engine. Key configuration:

- **Engine**: MergeTree family with month-based partitioning
- **Compression**: LZ4 for hot data, ZSTD for archives
- **Memory**: 64 GB allocated to query cache
- **Threads**: 32 background merge threads

The database stores 14.68 billion rows across 263 GiB on disk. Principal tables:

| Table | Rows | Size | Description |
|-------|------|------|-------------|
| `wspr.bronze` | 10.96B | 193.7 GiB | Raw WSPR observations (2008–2026) |
| `rbn.bronze` | 2.26B | 46.8 GiB | Reverse Beacon Network CW/RTTY/PSK31 spots |
| `pskr.bronze` | 552M | 7.6 GiB | PSK Reporter FT8/WSPR spots (live MQTT) |
| `contest.bronze` | 234M | 4.1 GiB | CQ contest SSB/RTTY QSOs |
| `solar.iri_lookup` | 331M | 3.7 GiB | Pre-computed IRI-2020 ionospheric parameters (Bilitza et al., 2017) |
| `wspr.signatures_v2_terrestrial` | 93.6M | 2.3 GiB | Aggregated WSPR training signatures |
| `rbn.signatures` | 67.3M | 1.3 GiB | Aggregated RBN training signatures |
| `solar.bronze` | 77K | <1 MiB | Solar indices (1932–present) |
| `solar.dscovr` | 56K | 1.4 MiB | DSCOVR L1 solar wind (Bz, speed, density) |

### 3.2 Ingestion Pipeline

Custom Go tools (ionis-apps) handle high-performance data ingestion:

| Tool | Input | Protocol | Performance |
|------|-------|----------|-------------|
| `wspr-turbo` | .csv.gz | ch-go native | 24.67 Mrps (16–24 workers) |
| `wspr-shredder` | .csv | ch-go native | 21.81 Mrps |
| `rbn-ingest` | .zip (daily) | ch-go native | 2.26B rows in ~20 min |
| `contest-ingest` | Cabrillo logs | ch-go native | 234M rows from 120 log sets |
| `pskr-collector` | MQTT (live) | JSON stream | ~300 spots/sec (~26M/day) |
| `solar-download` | HTTP | REST | 10 NOAA/SIDC endpoints |
| `solar-backfill` | HTTP | GFZ Potsdam | SSN/SFI/Kp 1932–present |
| `dscovr-ingest` | HTTP | DSCOVR L1 | Solar wind Bz/speed/density, 15-min cron |

All ingestion tools use:
- `ch-go` native protocol (not HTTP) for maximum throughput
- LZ4 wire compression
- Vectorized columnar parsing (no row structs)
- Double-buffering with sync.Pool for zero-allocation hot paths
- `CGO_ENABLED=0` for static binaries

### 3.3 Training Pipeline

PyTorch models train on the M3 Ultra using:

- **Python 3.10** (UV-managed virtual environment)
- **PyTorch 2.x** with MPS backend
- **Data loading**: Streaming from ClickHouse over DAC network
- **Checkpointing**: SafeTensors format with JSON metadata

Training scripts query ClickHouse directly:

```python
import clickhouse_connect
client = clickhouse_connect.get_client(host='<control-node>', port=8123)
df = client.query_df("SELECT * FROM wspr.signatures_v2_terrestrial LIMIT 10000000")
```

### 3.4 Local LLM Inference

The RTX PRO 6000 Blackwell (96 GB VRAM) runs large language models locally via llama.cpp:

| Model | Quantization | VRAM | Throughput |
|-------|--------------|------|------------|
| AstroSage-70B (sovereign) | Q5_K_M | 50.4 GB | **~30 tok/s** |
| DeepSeek-R1-Distill-Llama-70B | FP8 | 72 GB | ~15 tok/s |
| Llama-3.1-70B | Q5_K_M | ~50 GB | ~30 tok/s |

llama.cpp with Q5_K_M quantization on Blackwell achieves double the throughput of SGLang with FP8. This enables:
- Analysis of query results by domain-specialized LLMs
- Multi-agent workflows for architecture review
- No API costs or rate limits

---

## 4. Benchmark Methodology

### 4.1 Test Conditions

All benchmarks follow a consistent methodology:

1. **Cold cache**: `echo 3 > /proc/sys/vm/drop_caches` between runs
2. **Isolated workload**: No concurrent processes
3. **Thermal stability**: 10-minute warmup period
4. **Multiple runs**: Minimum 3 runs, median reported
5. **Full dataset**: 10.8B rows unless otherwise noted

### 4.2 Ingestion Benchmarks

**wspr-turbo** (streaming from compressed .gz archives):

| Workers | Time | Throughput | I/O Rate | Memory |
|---------|------|------------|----------|--------|
| 16 | 7m54s | 22.77 Mrps | 399 MB/s | 45.3 GB |
| **24** | **7m18s** | **24.67 Mrps** | **433 MB/s** | 71.5 GB |

**Key finding**: "Compression is free"—decompression overhead is hidden by the ClickHouse merge wall at ~3.5 GB/s sustained writes. wspr-turbo (reading 185 GB compressed) outperforms wspr-shredder (reading 878 GB uncompressed) because both hit the same database bottleneck.

**Cross-system comparison** (wspr-turbo, 16 workers):

| System | Time | Throughput | Speedup |
|--------|------|------------|---------|
| Threadripper 9975WX | 7m18s | 24.67 Mrps | **2.79×** |
| Ryzen 9950X3D | 20m13s | 8.83 Mrps | baseline |
| EPYC 7302P | 23m27s | 7.63 Mrps | 0.86× |

The 8-channel DDR5 memory (384 GB/s bandwidth) of the 9975WX provides the critical advantage over 2-channel systems.

### 4.3 Query Benchmarks

**Aggregation query** (GROUP BY over 10.8B rows):

```sql
SELECT callsign, avg(snr) as avg_snr, count(*) as count
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

This query scans the entire WSPR corpus and returns the top transmitters in 3 seconds—interactive speed for exploratory analysis.

### 4.4 Training Benchmarks

**Model**: IonisGate (207K parameters)
**Data**: 38M samples (WSPR + DXpedition + Contest signatures)
**Device**: M3 Ultra (MPS backend)

| Metric | Result |
|--------|--------|
| Epochs | 100 |
| Time | 4h 16m |
| Samples/sec | ~2,500 |
| Final RMSE | 0.821σ |
| Final Pearson | +0.492 |

### 4.5 Inference Benchmarks

**Model**: AstroSage-70B (Q5_K_M, 49.9 GB)
**Device**: RTX PRO 6000 Blackwell (96 GB VRAM)
**Runtime**: llama.cpp

| Metric | Result |
|--------|--------|
| Generation speed | **29.7–30.8 tok/s** |
| Prompt eval speed | 177–1,100 tok/s |
| First token latency | **68–90 ms** |
| VRAM usage | 50.4 GB |
| Idle power | 78W |
| GPU temperature | 45°C |

---

## 5. Cost Analysis

### 5.1 Hardware Investment

**Control Node (Threadripper 9975WX):**

| Component | Cost (USD) |
|-----------|------------|
| AMD Threadripper PRO 9975WX | $5,000 |
| NVIDIA RTX PRO 6000 (96 GB) | $9,000 |
| ASUS Pro WS TRX50-SAGE | $1,200 |
| Storage (3× NVMe) | $2,000 |
| Intel x710-DA4 + cables | $1,000 |
| Memory (128 GB DDR5 ECC) | $800 |
| PSU, case, cooling | $800 |
| **Control Node subtotal** | **~$19,800** |

**Other Nodes:**

| Component | Cost (USD) |
|-----------|------------|
| Mac Studio M3 Ultra (96 GB) | $5,500 |
| EPYC 7302P system (refurbished) | $2,500 |
| **Total** | **~$27,800** |

Note: The EPYC system was acquired refurbished with existing components. A minimal two-node configuration (9975WX + M3 Ultra) would cost approximately $25,300.

### 5.2 Cloud Equivalent

To replicate these capabilities using major cloud providers (pricing as of February 2026):

**Workload 1: Analytical Database (ClickHouse equivalent)**

The database workload requires 32+ vCPUs, 128+ GB RAM, and high-throughput NVMe storage for 263 GiB of compressed analytical data. This maps to a memory-optimized instance class.

| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute | Memory-optimized, 32 vCPU, 256 GB RAM | $1,524 |
| Storage | High-IOPS NVMe block storage (4 TB, 16K IOPS) | $540 |
| Backup storage | Object storage (4 TB archive) | $92 |
| **Subtotal** | | **$2,156/mo** |

Note: A managed columnar database service with equivalent compute (48 vCPU, always-on) runs approximately $8,500–9,000/month. Self-managed on a VM is significantly cheaper but requires operational overhead.

**Workload 2: Model Training (GPU)**

Training requires a single high-end GPU with 80–96 GB VRAM. Our production runs take ~4 hours, but experimentation (pre-flights, sweeps, failed runs) adds up. Conservative estimate: 200 GPU-hours/month across all experimentation.

| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| GPU compute | Single 80 GB GPU instance, on-demand | $1,376 |
| | ($6.88/hr × 200 hrs/mo) | |
| Budget GPU providers | Boutique cloud, ~$2.50/GPU-hr | $500 |
| **Range** | | **$500–1,376/mo** |

Note: Major cloud providers charge $6.88/hr for a single 80 GB GPU instance (on-demand). Boutique GPU cloud providers offer the same hardware at $1.50–3.00/hr but with less availability and no SLA.

**Workload 3: LLM Inference (70B model, always-on)**

Running a 70B parameter model locally requires ~50 GB VRAM with Q5_K_M quantization (or 72+ GB with FP8). Cloud equivalent: a multi-GPU inference instance running 24/7.

| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| GPU inference | 4× 48 GB GPU instance, always-on | $7,555 |
| | ($10.49/hr × 720 hrs/mo) | |
| Alternative: API | Commercial LLM API (~30 tok/s equivalent) | $500–2,000 |
| **Range** | | **$500–7,555/mo** |

Note: Self-hosting an LLM in the cloud is extremely expensive because the instance must run continuously. Using a commercial LLM API instead reduces cost but introduces rate limits, data privacy concerns, and API dependency — exactly the constraints sovereign infrastructure eliminates.

**Workload 4: Data Storage and Transfer**

| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Object storage | 4 TB raw archives | $92 |
| Data transfer (egress) | ~500 GB/mo cross-region | $45 |
| **Subtotal** | | **$137/mo** |

**Total Cloud Cost Summary:**

| Scenario | Monthly | Annual | Notes |
|----------|---------|--------|-------|
| **Full replication** (self-managed DB, major GPU cloud, self-hosted LLM) | **$11,224** | **$134,688** | Closest to sovereign capability |
| **Budget option** (self-managed DB, boutique GPU, LLM API) | **$3,293** | **$39,516** | Compromises on LLM privacy/availability |
| **Managed services** (managed DB, major GPU, self-hosted LLM) | **$17,818** | **$213,816** | Zero operational overhead |

### 5.3 Break-Even Analysis

| Scenario | Self-Hosted Cost | Cloud Annual | Break-Even |
|----------|-----------------|--------------|------------|
| Full replication | $27,800 | $134,688 | **2.4 months** |
| Budget cloud | $27,800 | $39,516 | **8.4 months** |
| Managed services | $27,800 | $213,816 | **1.5 months** |

Even against the cheapest cloud option (boutique GPU providers, LLM API, self-managed database), the self-hosted infrastructure pays for itself in under 9 months. Against a full-capability replication with major cloud providers, break-even is under 3 months.

**Ongoing self-hosted costs** after hardware purchase:

| Item | Monthly | Annual |
|------|---------|--------|
| Electricity (~800W avg draw, $0.10/kWh) | $58 | $696 |
| Internet (existing residential) | $0 | $0 |
| Hardware replacement (amortized) | $83 | $1,000 |
| **Total operating cost** | **$141/mo** | **$1,696/yr** |

The self-hosted infrastructure operates at $1,696/year — **4.3% of the cheapest cloud equivalent** and **1.3% of the full-replication cloud cost**.

*All figures verified by independent calculation. Cloud pricing sourced February 2026.*

### 5.4 Hidden Benefits

Beyond direct cost savings:

1. **No rate limits**: Cloud GPU quotas don't constrain experimentation. We ran 15 model versions (V2–V27) in rapid succession — cloud GPU availability would have been a bottleneck.
2. **Data sovereignty**: All 14.68 billion rows stay on local NVMe. No data processing agreements, no compliance concerns, no egress charges for moving data between services.
3. **Network independence**: Research continues during internet outages. The PSKR validation pipeline (552M spots → 8.4M signatures → model scoring → analysis) ran entirely on local hardware in a single afternoon.
4. **Iteration speed**: No upload/download delays. A 10-epoch pre-flight runs in 25 seconds on local CUDA. Cloud round-trip (upload data, provision instance, run, download results) adds 15–30 minutes of overhead per iteration.
5. **Privacy**: LLM inference on local hardware means research discussions, code review, and experimental analysis never leave the premises.
6. **Predictable costs**: No surprise bills from a forgotten running instance or unexpected data transfer charges. The hardware cost is fixed and fully amortized.

---

## 6. Applications

### 6.1 IONIS: Ionospheric Neural Inference System

The primary application of this infrastructure is the IONIS project—a neural network that predicts HF propagation from WSPR observations and solar indices.

**Training data** (14.68 billion rows total, 263 GiB on disk):

| Source | Volume | Signatures | Years |
|--------|--------|------------|-------|
| WSPR | 10.96B spots | 93.6M | 2008–2026 |
| Reverse Beacon Network | 2.26B spots | 67.3M | 2009–2026 |
| CQ Contests | 234M QSOs | 5.7M | 2005–2025 |
| DXpedition | 3.9M paths | 260K | 2009–2025 |
| PSK Reporter | 552M+ (live MQTT) | 8.4M | Feb 2026+ |
| Solar/IRI | 331M IRI + 77K solar + 56K DSCOVR | — | 1932–2026 |

**Model performance** (V22-gamma, current production):

- Pearson correlation: +0.492 (SNR prediction vs. actual)
- RMSE: 0.821σ (normalized)
- 17/17 operator-grounded validation tests passing (with physics override)
- 97.86% recall on 8.4M independent PSK Reporter spots (raw model, no override)
- 9/11 TST-900 physics gate battery

### 6.2 PSKR Validation Pipeline: Infrastructure in Action

The most compelling demonstration of this infrastructure's capability came on 2026-02-26, when the PSKR validation pipeline scored the IONIS model against 8.4 million independent PSK Reporter observations:

1. **Aggregation**: 552M raw PSKR spots → 8.4M signatures via ClickHouse SQL aggregation + Python numpy (haversine distance, azimuth computation). Wall time: **31 seconds**.
2. **Scoring**: 8.4M signatures through V22-gamma model inference on RTX PRO 6000 (CUDA). Two complete runs (with and without physics override). Wall time: **~100 minutes** per run.
3. **Cross-validation**: Identical scoring on M3 Ultra (MPS backend) over the DAC network. Results matched to the last decimal — deterministic across platforms.
4. **Analysis**: 8 diagnostic queries against 16.8M scored results, returning in seconds via ClickHouse.

The entire pipeline — from raw MQTT spots to actionable failure analysis — ran on local hardware with zero cloud involvement. The result: discovery that the physics override layer was introducing 261,030 false negatives while fixing exactly zero misses, directly informing the next model architecture.

### 6.3 Real-Time Monitoring

The infrastructure supports continuous validation against live data:

- **PSK Reporter**: ~26M HF spots/day via MQTT (live since 2026-02-10)
- **WSPR**: ~3M spots/day
- **Solar indices**: 15-minute updates from NOAA SWPC
- **DSCOVR L1**: Solar wind Bz/speed/density, 15-minute cron

### 6.4 Multi-Agent Research Workflow

The local LLM capability enables multi-agent workflows where specialized AI agents analyze different aspects of the research:

| Agent | Callsign | Role | Interface | Host |
|-------|----------|------|-----------|------|
| Dr. Watson | Training Agent | Training, code | IDE | Sage Node |
| Bob | Infrastructure Agent | Infrastructure, SQL, CUDA | IDE | Control Node |
| Patton | Failure Analyst | Failure analysis, skeptical review | Desktop App | macOS |
| Einstein | Physics Consultant | Physics theory, constraints | Browser | Cloud |
| Newton | AstroSage | Sovereign local inference | llama.cpp / Open WebUI | 9975WX |
| Judge | KI7MT | Final authority, tiebreaker | Human | — |

Agents coordinate via a ClickHouse message queue (`messages.inbox`) — the same database both coding agents already query. No external Slack, no email, no new infrastructure. A simple INSERT to send, SELECT to receive. This "Dialectical Engine" approach subjects every architectural decision to multi-agent falsification testing before implementation. See *The Dialectical Engine* (companion paper) for the full methodology.

---

## 7. Lessons Learned

### 7.1 Memory Bandwidth Matters

For analytical workloads, memory bandwidth dominates performance. The Threadripper 9975WX's 8-channel DDR5 (~384 GB/s) achieves 2.79× the throughput of dual-channel systems, despite similar clock speeds. Investment in memory channels provides better returns than faster individual DIMMs.

### 7.2 I/O Decoupling is Critical

Placing source files and database writes on separate NVMe devices eliminated the primary ingestion bottleneck. This simple architectural decision enabled a 30% throughput increase at zero additional cost.

### 7.3 Compression is (Often) Free

The ClickHouse merge wall at ~3.5 GB/s becomes the bottleneck before decompression overhead matters. Reading 185 GB compressed is faster than reading 878 GB uncompressed because both hit the same database constraint.

### 7.4 Unified Memory Changes the Game

The M3 Ultra's unified memory architecture makes it surprisingly competitive for model training. Eliminating CPU-GPU transfer overhead compensates for lower peak FLOPS compared to discrete GPUs.

### 7.5 Local LLMs Enable New Workflows

Running 70B models locally (at ~30 tok/s with Q5_K_M on Blackwell) transforms what's possible for individual researchers. Multi-agent review workflows, automated analysis of experimental results, and domain-specialized inference all become practical without API costs or rate limits.

### 7.6 Process Discipline Transfers from Manufacturing

The project applies CLCA (Closed Loop Corrective Actions) — the Ford 8D / semiconductor process control methodology — to every layer of the ML pipeline. Identify the defect, measure it, action plan, fix, verify. This manufacturing quality engineering discipline, adapted from the author's background in semiconductor metrology, prevented several classes of errors that pure software engineering approaches would have missed:

- **Containment actions**: When the model couldn't close 10m paths at night, a physics override was deployed within hours as containment (D3). The PSKR validation battery then measured its collateral damage (D4), revealing 261K false negatives. The corrective action (D5) — synthetic negatives — addresses the root cause rather than patching symptoms.
- **Audit trail**: Every training run is logged to ClickHouse with configuration, epoch metrics, and final results. Failed experiments are as rigorously documented as successes, creating a traceable lineage from V2 through V27.
- **One variable at a time**: Each model version changes exactly one thing relative to its predecessor. This eliminates confounded variables and ensures that when something breaks, the root cause is identifiable.

---

## 8. Reproducibility

### 8.1 Source Code

All software is available in public repositories:

| Repository | Language | Purpose |
|------------|----------|---------|
| ionis-apps | Go | Ingestion tools |
| ionis-core | SQL/Autotools | Database schemas |
| ionis-cuda | C++/CUDA | Embedding engine |
| ionis-training | Python | Model training |
| ionis-devel | Markdown | Documentation |

### 8.2 Configuration

System configuration is documented in:
- `CLAUDE.md`: Project instructions and agent coordination
- `SOVEREIGN-STACK.md`: Hardware specifications and benchmarks
- `planning/*.md`: Architecture decisions and validation frameworks

### 8.3 Benchmark Scripts

All benchmark results can be reproduced using scripts in `ionis-apps/benchmarks/` and queries in `ionis-core/scripts/`.

---

## 9. Model Development History

The IONIS project has iterated through 15 model versions (V2–V27), with the infrastructure supporting rapid experimentation. The failure record is as valuable as the successes:

| Version | Key Change | Result | Lesson |
|---------|-----------|--------|--------|
| V16 | Contest-anchored training | Pearson +0.487, 84% live recall | Established physics constraints |
| V20 | Clean config-driven rewrite | Pearson +0.488, RMSE 0.862σ | Proved V16 constraints are complete |
| V22-gamma | Solar depression + cross-products | **Pearson +0.492, RMSE 0.821σ** | Best physics model (current production) |
| V23 | IRI-2020 ionospheric features | Record RMSE but physics gates failed | IRI creates shortcuts, bypasses learning |
| V24 | Removed sun sidecar | Both sidecars died | Architecture constraints are load-bearing |
| V25 | 2D SFI sidecar | Optimizer killed SFI dimension | Scalar SFI is vestigial (clamp floor) |
| V26 | Band-specific output heads | Learned bias, not physics | Multi-head is a dead end |
| V27 | Physics-informed loss | Fine-tuning destroyed trunk | Never fine-tune from converged checkpoint |

Eight architectural dead ends, all proven by experiment, all documented. The infrastructure's speed (10-epoch pre-flight in 25 seconds on CUDA, full training in 4 hours on MPS) made this iteration rate practical for a single researcher.

---

## 10. Conclusion

We have demonstrated that a carefully architected self-hosted infrastructure can support serious scientific research at scale. The key findings:

1. **24.67 Mrps ingestion** is achievable on commodity hardware with proper I/O architecture
2. **60 GB/s query throughput** enables interactive analysis of 10+ billion rows
3. **Local 70B LLM inference** at 30 tok/s eliminates cloud API dependencies
4. **~$28,000 one-time investment** replaces $39,500–$214,000/year in cloud costs (break-even in 2–9 months)
5. **14.68 billion rows, 263 GiB** stored and queryable on a single workstation

This infrastructure enables the IONIS project to work with one of the largest curated amateur radio propagation datasets we are aware of — 14.68 billion rows spanning 18 years of observations from five independent data sources — entirely on local hardware. The PSKR validation pipeline demonstrated the full capability: 552 million raw spots aggregated into 8.4 million signatures, scored against the production model, cross-validated on two platforms, and analyzed — all in a single afternoon, with zero cloud involvement.

For amateur radio operators, citizen scientists, and small research teams, sovereign infrastructure provides a path to serious data science without institutional resources or recurring cloud costs. The ionosphere has been writing data for 18 years. Now we have the infrastructure to read it.

---

## Data Ethics and Privacy

This project exists because of the amateur radio community. Every observation in our dataset was generated by a ham radio operator somewhere in the world, running a beacon, making a contact, or submitting a log. We treat this data with appropriate care.

**Non-Commercial, Open Source**: There is no commercial motive behind this project. There is no monetization plan. All code, tools, and models are released under the GNU General Public License v3 (GPLv3). We redistribute only derived works (trained models, aggregated signatures) — never raw data.

**Data Privacy**: We have zero interest in personal data. We study propagation paths between grid squares, not the operators who generated them. Amateur radio callsigns appear in the bronze (raw ingest) layer only for grid square resolution. By the time data reaches the model-facing layer, all callsigns have been stripped. The model receives only: grid-pair, band, time of day, month, solar flux, geomagnetic index, distance, and bearing. No callsign, no name, no personal identifier.

**Publicly Available Data**: All source data is publicly available, provided by community organizations for public use:

- **WSPR beacons** are transmitted over public radio frequencies specifically to be received and reported. Operators deliberately upload spots to WSPRNet's public database.
- **RBN spots** are machine-decoded from public radio transmissions and provided as a public service.
- **Contest logs** are submitted by operators who explicitly consent to public posting as a condition of participation (CQ WW Rules Section XIII).

Amateur radio is, by its nature, a public service. ITU Radio Regulations and national licensing authorities require operators to identify themselves during every transmission. There is no expectation of privacy for amateur radio callsigns.

**Ethical Data Stewardship**: Our ingestion tools are designed to be polite. We enforce rate limits, identify ourselves honestly in User-Agents, and respect volunteer-run servers. We archive data for long-term preservation, not just analysis.

**Attribution**: We rigorously acknowledge all data sources. When we publish results, we share findings with the data providers and the amateur radio community.

---

## Acknowledgments

This project exists because of the amateur radio community. To every operator who has ever transmitted a WSPR beacon, worked a contest, appeared on the Reverse Beacon Network, or shown up on PSK Reporter: thank you.

**Data Sources:**

- **Joe Taylor, K1JT** — Creator of WSPR, WSJT, WSJT-X, and MAP65. Nobel Laureate (Physics, 1993). The WSPR protocol that generates the observations we study is his contribution to amateur radio.
- **WSPRNet** (wsprnet.org) — The community-operated database that collects and archives WSPR spot reports from operators worldwide.
- **Reverse Beacon Network** (reversebeacon.net) — N4ZR, PY1NB, VE3NEA, and the global network of CW/RTTY skimmer operators who contribute 2.26 billion spots spanning 2009–2026.
- **PSK Reporter** (pskreporter.info) — Created by Philip Gladstone, N1DQ. MQTT real-time feed by Tom Sevart, M0LTE.
- **World Wide Radio Operators Foundation** (WWROF) — CQ WW and CQ WPX contest log archives.
- **American Radio Relay League** (ARRL) — Contest log archives from contests.arrl.org.
- **GDXF Mega DXpeditions Honor Roll** — Curated DXpedition catalog by Bernd, DF3CB.

**Solar & Geomagnetic Data:**

- **NOAA Space Weather Prediction Center** (SWPC) — Real-time F10.7 solar flux, Kp index, GOES X-ray flux.
- **SIDC, Royal Observatory of Belgium** — World Data Center for sunspot numbers (1749–present).
- **GFZ Potsdam** (Helmholtz Centre) — Definitive Kp/Ap indices, composite SSN/SFI file (1932–present).
- **Penticton / NRC Canada** — Dominion Radio Astrophysical Observatory, the world's primary 10.7 cm solar flux measurement station.
- **NOAA NCEI** — DSCOVR L1 solar wind data (Bz, speed, density).

**Software:**

- **ClickHouse** (ClickHouse Inc., originally Yandex) — Columnar database engine.
- **voacapl** — Linux port of VOACAP by James Watson, HZ1JW.
- **PyTorch** (Meta AI) — Machine learning framework.
- **llama.cpp** (Georgi Gerganov) — Local LLM inference.

---

## References

- Bilitza, D., et al. (2017). International Reference Ionosphere 2016: From ionospheric climate to real-time weather predictions. *Space Weather*, 15(2), 418-429.

- Davies, K. (1990). *Ionospheric Radio*. Peter Peregrinus Ltd.

- Lane, G., et al. (1993). *Voice of America Coverage Analysis Program (VOACAP)*. NTIA Report 93-299.

---

## Appendix A: Bill of Materials

### A.1 Control Node (Threadripper 9975WX) — ~$19,800

| Component | Model | Qty | Cost | Notes |
|-----------|-------|-----|------|-------|
| CPU | AMD Threadripper PRO 9975WX | 1 | $5,000 | 32C/64T, TRX50 |
| GPU | NVIDIA RTX PRO 6000 | 1 | $9,000 | 96 GB VRAM |
| Motherboard | ASUS Pro WS TRX50-SAGE | 1 | $1,200 | 7× PCIe 5.0 |
| Memory | DDR5-5600 ECC 16GB | 8 | $800 | 8-channel config (128 GB total) |
| NVMe (OS) | Micron 7450 PRO 960GB | 1 | — | Enterprise boot drive |
| NVMe (Data) | Samsung SSD 9100 PRO 4TB | 2 | — | ClickHouse + Working (PM9E1) |
| NVMe Adapter | HighPoint Rocket 1504 | 1 | — | PCIe Gen4 ×16, 4-port NVMe |
| NVMe (Archive) | Samsung 990 PRO 4TB | 4 | $2,000 | ZFS archive pool |
| NIC | Intel x710-DA4 | 1 | $1,000 | Quad SFP+ (+ AOC cables) |
| PSU | Seasonic Prime TX-1600 | 1 | — | 1600W Titanium, ATX 3.1, PCIe 5.1 |
| Case | Corsair 9000D | 1 | — | Full tower |
| Fans | Noctua NF-A12x25 120mm | 16 | — | Positive pressure config |

### A.2 Sage Node (Mac Studio M3 Ultra)

| Component | Model | Notes |
|-----------|-------|-------|
| System | Mac Studio M3 Ultra | 96 GB unified memory |
| Storage | 2 TB SSD | Internal |
| Network | Thunderbolt 4 | 10 Gbps to Control Node |

### A.3 Networking

| Component | Model | Qty |
|-----------|-------|-----|
| SFP+ AOC | FS.com 10G-AOC-3M | 3 |
| Thunderbolt 4 cable | Apple 3m | 1 |

---

## Appendix B: Benchmark Raw Data

### B.1 wspr-turbo 24-Worker Run (2026-02-01)

```
Start time: 2026-02-01T14:23:17Z
End time:   2026-02-01T14:30:35Z
Duration:   7m18s

Files processed:  2,847
Total rows:       10,956,387,569
Throughput:       24.67 Mrps
I/O Rate:         433 MB/s (compressed)
Effective Rate:   1.88 GB/s (uncompressed)

Memory (sys):     71.5 GB
GC cycles:        432
Peak CPU:         100% (64 threads)
Temperature:      74°C
```

### B.2 ClickHouse Aggregation Query (2026-02-01)

```sql
SELECT callsign, avg(snr), count(*)
FROM wspr.bronze
GROUP BY callsign
ORDER BY count() DESC
LIMIT 10

-- Execution stats:
-- Elapsed: 3.050 sec
-- Rows read: 10,956,387,569
-- Bytes read: 183.57 GiB
-- Rows/sec: 3.54 billion
-- Bytes/sec: 60.19 GB
-- Peak memory: 828.79 MiB
```
