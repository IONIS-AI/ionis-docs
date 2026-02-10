# Step F — Aggregated Signatures

**Status**: COMPLETE (2026-02-05)
**Roadmap Step**: F — Metrology Noise Rejection
**Executed on**: Threadripper 9975WX (64 threads, ClickHouse on dedicated NVMe)

---

## Objective

Transform 10.8B individual WSPR spots into a high-precision signature library
by aggregating reports into median-based physical buckets. This strips
site-level noise (local QRM, antenna inefficiency, ground fading) and reveals
the atmospheric transfer function.

## Table: `wspr.signatures_v1`

### Dimensions

| Column | Type | Description |
|--------|------|-------------|
| `tx_grid_4` | FixedString(4) | 4-char TX Maidenhead grid (field level) |
| `rx_grid_4` | FixedString(4) | 4-char RX Maidenhead grid (field level) |
| `band` | Int32 | ADIF band ID (102-111) |
| `hour` | UInt8 | Hour of day UTC (0-23) |
| `month` | UInt8 | Month (1-12) |

### Metrics

| Column | Type | Description |
|--------|------|-------------|
| `median_snr` | Float32 | quantile(0.5)(snr) — site entropy filter |
| `spot_count` | UInt32 | Number of spots in bucket (minimum 5) |
| `snr_std` | Float32 | SNR standard deviation (dB) |
| `reliability` | Float32 | Fraction of spots with SNR > -20 dB |
| `avg_sfi` | Float32 | Average Solar Flux Index for bucket |
| `avg_kp` | Float32 | Average Kp index for bucket |
| `avg_distance` | UInt32 | Average great-circle distance (km) |
| `avg_azimuth` | UInt16 | Average azimuth (degrees) |

**ORDER BY**: `(band, hour, tx_grid_4, rx_grid_4)` for fast training access.

## V11 Feature Derivation

All 13 IONIS V11 features are derivable from the signature table:

| V11 Feature | Source |
|---|---|
| distance | `avg_distance` |
| freq_log | Derived from `band` → frequency mapping |
| hour_sin / hour_cos | Derived from `hour` |
| az_sin / az_cos | Derived from `avg_azimuth` |
| lat_diff | Computed from grid centroids |
| midpoint_lat | Computed from grid centroids |
| season_sin / season_cos | Derived from `month` |
| day_night_est | Derived from `hour` + grid longitude |
| sfi (sidecar) | `avg_sfi / 300` |
| kp_penalty (sidecar) | `1 - avg_kp / 9` |

## Filters Applied

| Filter | Value | Rationale |
|--------|-------|-----------|
| Band | 102-111 | HF amateur only |
| Distance | >= 500 km | Ground-wave contamination rejection |
| Spot count | >= 5 | Noise floor rejection |
| Median (quantile 0.5) | — | Outlier-resistant central tendency |

## Aggregation Method

Per-band `INSERT INTO ... SELECT` from `wspr.bronze` joined with
`solar.bronze` on date + 3-hour Kp bucket. Processing is sequential
by band to stay within memory limits (quantile computation stores all values
per group).

## Results

| Metric | Value |
|--------|-------|
| **Total signatures** | **93,785,013** |
| **Processing time** | 3 min 10 sec (10 bands sequential) |
| **Compression ratio** | 115:1 (10.8B → 93.8M) |
| **Average bucket size** | 96 spots |
| **Zero SFI buckets** | 25,433 (0.03%) |
| **NaN values** | 0 |

### Per-Band Distribution

| Band | ID | Buckets | Total Spots | Avg Median SNR | Avg Reliability |
|------|-----|---------|-------------|----------------|-----------------|
| 160m | 102 | 1.69M | 116M | -18.1 dB | 0.477 |
| 80m | 103 | 5.85M | 532M | -17.9 dB | 0.495 |
| 60m | 104 | 0.91M | 81M | -17.6 dB | 0.499 |
| 40m | 105 | 21.67M | 2.80B | -17.4 dB | 0.537 |
| 30m | 106 | 15.98M | 1.62B | -18.1 dB | 0.497 |
| 20m | 107 | 27.59M | 2.74B | -17.5 dB | 0.533 |
| 17m | 108 | 6.35M | 373M | -18.4 dB | 0.477 |
| 15m | 109 | 6.26M | 360M | -18.3 dB | 0.480 |
| 12m | 110 | 2.12M | 104M | -18.8 dB | 0.453 |
| 10m | 111 | 5.37M | 267M | -17.9 dB | 0.505 |

20m and 40m dominate (as expected — most active WSPR bands).

### Sanity Check: FN31 → JO21 (20m)

The reference path (Connecticut to Belgium, ~5,900 km) shows a smooth,
physically consistent diurnal curve:

- SNR peaks at 15-18 UTC (late afternoon, path fully sunlit)
- SNR drops overnight (02-04 UTC)
- Summer months show extended propagation windows into evening
- Winter months concentrate propagation into midday hours
- Reliability tracks SNR — higher during peak propagation

No stair-step artifacts. The median successfully strips individual spot
noise and reveals the atmospheric transfer function.

## ClickHouse Performance Settings

```sql
SETTINGS
    max_threads = 64,
    max_memory_usage = 80000000000,
    max_bytes_before_external_group_by = 20000000000,
    join_use_nulls = 0
```

!!! note "Memory Limit"
    A single-pass aggregation of all 10 bands exceeded 74.5 GiB memory
    due to `quantile(0.5)` storing all values per group. Per-band processing
    reduces peak memory to ~8 GiB per band.

## Signatures V2 — Balloon-Filtered (2026-02-09)

Training from V14 onward uses `wspr.signatures_v2_terrestrial` (93.3M rows) which
excludes balloon and telemetry contamination identified by the V2 detection system.

- **V1 balloon filter** (deprecated): flagged 276M spots (2.56%) — 99.7% false positives
- **V2 balloon filter** (current): date-level velocity detection + full Rosetta Stone (3.64M callsigns) — 1,443 entries, 950K spots (0.009%) — surgical

The V2 filter correctly excludes only confirmed high-altitude balloon transmissions
while preserving legitimate ground station data. The difference is quantified in the
V14-TP vs V14-TP-v2 A/B comparison (+1.3 pp Pearson improvement from corrected filter).

DDL: `21-balloon_callsigns_v2.sql`, `19-signatures_v2_terrestrial.sql`

## DDL Location

`/usr/share/ki7mt-ai-lab-core/ddl/12-signatures_v1.sql`
