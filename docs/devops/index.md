# Hardware Requirements

This page describes the hardware needed to reproduce the IONIS pipeline,
from minimum viable to the reference build currently in production.

## Minimum Recommended

These specs support the full pipeline end-to-end: ingest, embeddings,
training, and inference.

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 16 cores (Zen 3+) | 32+ cores (Threadripper/EPYC) |
| RAM | 64 GB | 128 GB (`wspr-turbo` uses ~80 GB at 16 workers) |
| GPU | NVIDIA 8+ GB VRAM | NVIDIA 24+ GB VRAM |
| ClickHouse storage | 2 TB NVMe | 4 TB NVMe (separate from OS) |
| Archive storage | 2 TB | 4+ TB (ZFS recommended) |
| OS | RHEL 9 / Rocky 9 / Fedora | Rocky Linux 9.7 |

!!! note "GPU is optional"
    GPU is only required for the silver layer (CUDA embeddings via
    `bulk-processor`). Training runs on Mac or Linux with PyTorch (CPU or
    MPS). You can skip straight from bronze to gold if you don't need
    embeddings.

## Reference Build

The production IONIS infrastructure uses three nodes connected by direct-attach
10 Gbps links with no switches.

### Compute Nodes

| Node | Role | CPU | RAM | GPU | OS |
|------|------|-----|-----|-----|-----|
| **9975WX** (Control) | Ingestion, ClickHouse, CUDA | Threadripper PRO 9975WX (32C/64T, Zen 5) | 128 GB DDR5 8-ch | RTX PRO 6000 (96 GB) | Rocky Linux 9.7 |
| **M3 Ultra** (Sage) | Model training, evaluation | Apple M3 Ultra | 96 GB unified | Integrated (MPS) | macOS |
| **EPYC 7302P** (Forge) | Proxmox VM/app server, backup | EPYC 7302P (16C/32T) | 128 GB DDR4 ECC | RTX 5080 (16 GB) | Proxmox VE |

### DAC Network (Direct Attach Copper/Optical)

All inter-node links are point-to-point with jumbo frames (MTU 9000).

| Link | Cable | Subnet | Host A | Host B | Latency |
|------|-------|--------|--------|--------|---------|
| Thunderbolt 4 | USB4/TB4 | `10.60.1.0/24` | 9975WX `.1` | M3 Ultra `.2` | ~0.19 ms |
| x710 SFP+ AOC | FS.com 10G | `10.60.2.0/24` | 9975WX `.1` | Proxmox `.2` | ~0.12 ms |
| x710 SFP+ AOC | FS.com 10G | `10.60.3.0/24` | 9975WX `.1` | TrueNAS `.2` | ~0.03 ms |

Training scripts target `10.60.1.1:8123` (HTTP) / `10.60.1.1:9000` (native)
for ClickHouse queries over the DAC link.

### Storage Layout (9975WX)

Source data and ClickHouse are on separate NVMe drives to decouple read and
write I/O during ingestion.

| Drive | Mount | Size | Purpose |
|-------|-------|------|---------|
| nvme2n1 | `/` (LVM) | ~1 TB | OS (150 GB root, 4 GB swap, 739 GB home) |
| nvme0n1 | `/var/lib/clickhouse` | 3.6 TB | ClickHouse data (~200 GB used) |
| nvme1n1 | `/mnt/ai-stack` | 3.6 TB | Working data (repos, scripts) |

### ZFS Archive Pool

Raw source archives live on a mirrored ZFS pool (`archive-pool`, 7.12 TB
usable on Samsung 990 Pro SSDs). Compression varies by content:

| Dataset | Mountpoint | Compression | Purpose |
|---------|------------|-------------|---------|
| `archive-pool/wspr-data` | `/mnt/wspr-data` | lz4 | WSPR raw CSV archives (.csv.gz) |
| `archive-pool/contest-logs` | `/mnt/contest-logs` | zstd-9 | CQ contest Cabrillo logs |
| `archive-pool/rbn-data` | `/mnt/rbn-data` | lz4 | RBN daily ZIP archives |
| `archive-pool/pskr-data` | `/mnt/pskr-data` | lz4 | PSK Reporter MQTT collection |

### Benchmark Actuals

Performance verified on the 9975WX reference build (2026-02-07):

| Operation | Throughput | Wall Time |
|-----------|-----------|-----------|
| WSPR ingest (`wspr-turbo` @ 16 workers) | 21.91 Mrps | 8 min |
| RBN ingest (`rbn-ingest`) | 10.30 Mrps | 3 min 32 s |
| Contest ingest (`contest-ingest`) | -- | 21 min 32 s |
| ClickHouse scan (10.8B rows) | 60 GB/s | 0.64 s |
| CUDA embeddings (`bulk-processor`) | -- | ~45 min |
| V20 training (100 epochs, MPS) | -- | 4 h 16 min |
| **Full pipeline** (clean slate to training-ready) | -- | **~2 hours** |
