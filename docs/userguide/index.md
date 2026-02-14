# Getting Started

## What IONIS Predicts

IONIS (Ionospheric Neural Inference System) predicts HF radio signal-to-noise
ratio (SNR) for any transmitter-receiver path given geographic coordinates,
frequency, time of day, and solar conditions.

The model learns from 13B+ real-world amateur radio observations — WSPR beacons,
Reverse Beacon Network spots, and contest QSOs — combined with solar flux and
geomagnetic indices. Unlike traditional tools such as VOACAP, IONIS captures
empirical propagation patterns directly from observed data.

**Key metrics (V20 Production):**

| Metric | IONIS V20 | VOACAP |
|--------|-----------|--------|
| Pearson correlation | **+0.4879** | +0.0218 |
| PSK Reporter recall | **84.14%** | — |
| Training data | 31M signatures | Physics model |

## Installation

IONIS packages are available from the COPR repository for Rocky Linux 9 /
RHEL 9 / Fedora.

### Enable the COPR Repository

```bash
sudo dnf copr enable ki7mt/ionis-ai
```

### Install Packages

```bash
# Core schemas and configuration
sudo dnf install ionis-core

# Pipeline apps (ingesters, downloaders, validators)
sudo dnf install ionis-apps

# CUDA embedding engine (requires NVIDIA GPU)
sudo dnf install ionis-cuda
```

### Verify Installation

```bash
# Load environment variables
source ionis-env

# Check ClickHouse connectivity
clickhouse-client --query "SELECT 1"

# List installed DDL files
ls /usr/share/ionis-core/ddl/
```

## Quick Start

After installing the RPMs and setting up ClickHouse:

```bash
# 1. Source the environment
source ionis-env

# 2. Apply database schemas
for f in /usr/share/ionis-core/ddl/*.sql; do
    clickhouse-client --multiquery < "$f"
done

# 3. Verify tables exist
clickhouse-client --query "SHOW TABLES FROM wspr"
clickhouse-client --query "SHOW TABLES FROM solar"

# 4. Check table counts (after data is loaded)
db-validate --all
```

## What's Next

- **Full pipeline setup**: See the [Pipeline Runbook](../devops/pipeline-runbook.md)
  for step-by-step instructions from clean slate to training-ready
- **Hardware planning**: See [Hardware Requirements](../devops/index.md) for
  minimum specs and the reference build
- **Running predictions**: See [Running Predictions](predictions.md) for
  using the trained model
- **Operations**: See [Operations & Maintenance](../devops/maintenance.md) for
  cron jobs and health checks
