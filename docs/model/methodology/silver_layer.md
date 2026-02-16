# Silver Layer

Derived tables built from the bronze stack. The silver layer transforms raw
spots into embeddings and aggregated signatures for downstream analysis and
model training.

## Prerequisites

- Bronze stack fully populated (see [Bronze Stack](bronze_stack.md))
- `solar.bronze` populated (required for all JOINs)

## Step 1: Generate CUDA Embeddings

The bulk-processor generates float4 embeddings from WSPR spots joined with
solar indices, stored in `wspr.silver`.

```bash
bulk-processor --host 192.168.1.90
```

!!! warning "Requires NVIDIA GPU"
    The bulk-processor requires an NVIDIA GPU with sufficient VRAM.
    The RTX PRO 6000 (96 GB) processes all 10.8B spots in a single pass.

!!! note "Not in RPM"
    `bulk-processor` is not yet packaged in the `ionis-cuda` RPM.
    Build locally: `cd ionis-cuda && mkdir build && cd build && cmake .. && make`

Verification:

```bash
clickhouse-client --query "SELECT count() FROM wspr.silver"
# Expected: ~4,430,000,000
```

The `v_quality_distribution` materialized view auto-populates as rows are
inserted into `wspr.silver`:

```bash
clickhouse-client --query "SELECT count() FROM wspr.v_quality_distribution"
# Expected: ~6,100,000
```

## Step 2: Build Aggregated Signatures

Signatures compress 10.8B raw spots into ~93M median-bucketed entries — a
115:1 compression ratio that strips site-level noise and reveals the
atmospheric transfer function.

See [Aggregated Signatures](step_f_signatures.md) for full methodology
and per-band distribution.

```bash
bash /usr/share/ionis-core/scripts/populate_signatures.sh
# Or with custom host:
# CH_HOST=10.60.1.1 bash /usr/share/ionis-core/scripts/populate_signatures.sh
```

Verification:

```bash
clickhouse-client --query "SELECT count() FROM wspr.signatures_v2_terrestrial"
# Expected: ~93,600,000
```

## QA Actuals

Clean-slate rebuild on 9975WX (2026-02-07):

```text
Table                   Rows            Time
----------------------  --------------  ---------
wspr.silver             4,430,000,000   ~45 min
wspr.signatures_v2_terrestrial  93,600,000      3m31s
v_quality_distribution  ~6,100,000      (auto)
```

## Next Steps

- **Gold layer**: See [Gold Layer](gold_layer.md) for training tables and CSV export
- **Training**: See [Training](training.md) for model architecture and training methodology
