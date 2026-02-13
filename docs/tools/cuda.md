# CUDA Engine

!!! note "Local Build Only"
    `bulk-processor` is **not included in the `ionis-cuda` RPM**. COPR build
    servers do not have NVIDIA GPUs or the CUDA toolkit, so this binary must be built
    locally on a host with a supported GPU and CUDA 13.1+.

## bulk-processor

GPU-accelerated float4 embedding generator for the WSPR silver layer. Reads
date-ranged batches from `wspr.bronze`, JOINs with `solar.bronze` for solar/geomagnetic
context, computes signature embeddings on the GPU, and writes results to `wspr.silver`.
Part of `ionis-cuda` (CUDA binary).

```text
┌─────────────────────────────────────────────────────────────┐
│  Bulk Embedding Processor - Blackwell sm_120                │
│  ionis-cuda v2.3.1                                   │
└─────────────────────────────────────────────────────────────┘

Usage: bulk-processor --start YYYY-MM-DD --end YYYY-MM-DD [options]

Required:
  --start DATE      Start date (inclusive)
  --end DATE        End date (inclusive)

Options:
  --host ADDR       ClickHouse host (default: $CH_HOST or 192.168.1.90)
  --port N          ClickHouse port (default: $CH_PORT or 9000)
  --hourly          Process hour-by-hour (default: daily)
  --band N          Filter by ADIF band ID (0 = all bands)
  --dry-run         Count rows only, don't process
  --batch-size N    Max rows per GPU batch (default: 1000000)
  -h, --help        Show this help

Example:
  bulk-processor --start 2025-01-01 --end 2025-12-31 --hourly
```

### Building from Source

**Requirements:**

- CUDA Toolkit 13.1+ with `nvcc`
- CMake 3.20+
- C++20 compiler
- `clickhouse-cpp` v2.5.1 (fetched automatically by CMake if not installed)
- NVIDIA GPU (built for sm_120 / Blackwell by default)

**Build steps:**

```bash
cd ionis-cuda
mkdir build && cd build
cmake ..
cmake --build . -j$(nproc)
```

The binary is produced at `build/bulk-processor`.

**Install to user PATH:**

```bash
cp build/bulk-processor ~/.local/bin/bulk-processor
```

### Supported Architectures

The CMake build targets sm_120 (Blackwell). The alternative Makefile produces a
fat binary covering multiple generations:

| Flag | Architecture | GPUs |
|------|-------------|------|
| sm_80 | Ampere | A100 |
| sm_86 | Ampere | RTX 30xx |
| sm_89 | Ada Lovelace | RTX 40xx |
| sm_100 | Blackwell | RTX 50xx |
| sm_120 | Blackwell refresh | RTX PRO 6000 |
| compute_120 | PTX JIT | Future GPUs |
