# Step I: IONIS vs VOACAP Head-to-Head

- **Date:** 2026-02-08
- **Dataset:** 1,000,000 contest QSO paths (CQ WW, CQ WPX, ARRL DX — 2005-2025)
- **IONIS Version:** V12 Signatures
- **VOACAP Version:** voacapl 0.7.5 (NTIA/ITS Method 30)

---

## Summary

Both models were given 1M real contest QSOs and asked: "was this band open?"
Every QSO actually happened, so the ground truth is always YES. The question
is which model correctly predicts that.

```text
+--------+---------+
| Model  | Recall  |
+--------+---------+
| IONIS  | 90.42%  |
| VOACAP | 75.98%  |
+--------+---------+
  Delta:  +14.44 pp
```

IONIS V12 outperforms VOACAP by **14.4 percentage points** on real-world
contest QSO recall.

---

## Methodology

### Data Source

The 1M paths were exported by `validate_v12.py --export` from contest QSO
records in `contest.bronze`. Each row represents a confirmed two-way contact
between amateur radio stations during a major HF contest. These are not
synthetic paths — every row is a real QSO that actually completed.

### IONIS Scoring

IONIS V12 predicts SNR for each path. Band is considered "open" if:

```text
predicted_snr >= mode_threshold
```

Mode thresholds: DG/CW = -22.0 dB, RY/PH = -21.0 dB.

### VOACAP Scoring

Each path is converted to a VOACAP input card and run through `voacapl`
(Method 30, CCIR coefficients). The same mode thresholds are applied to
VOACAP's predicted SNR:

```text
voacap_snr >= mode_threshold
```

VOACAP parameters:

- TX Power: 0.01 kW (10W) via ANTENNA card
- Antenna: const17.voa (17 dBi omnidirectional)
- Coefficients: CCIR
- Method: 30 (complete system performance)
- All 24 hours predicted per circuit; matched to QSO hour

### Execution

- Unique circuits: 965,161 (from 1M rows with dedup ratio 1.04x)
- Workers: 32 (ProcessPoolExecutor on Threadripper 9975WX)
- Throughput: ~370 circuits/sec
- Total time: ~43 minutes
- Errors: 0

Results stored in `validation.step_i_voacap` (ClickHouse) for reproducible
querying by either the 9975WX or M3 agent.

---

## Results by Mode

```text
Mode      Total       IONIS TP    IONIS %    VOACAP TP   VOACAP %
------  ---------  -----------  ---------  -----------  ---------
CW        459,200      416,780     90.76%      340,678     74.36%
PH        285,083      253,900     89.06%      215,717     75.83%
RY        233,446      214,476     91.87%      183,392     78.72%
DG         22,208       20,753     93.45%       18,397     82.84%
```

IONIS leads in every mode. The gap is widest for CW (+16.4 pp) and narrowest
for DG (+10.6 pp). Digital modes (DG, RY) have the lowest thresholds, so both
models find them easier to predict.

---

## Results by Band

```text
Band      Total     VOACAP TP   VOACAP %    Why
------  ---------  ----------  ---------   --------------------------------
160m       55,879      25,217     45.13%    NVIS/ground wave — VOACAP weakest
80m        95,126      71,328     74.98%    Night-only propagation
40m       205,415     174,004     84.71%    Reliable DX band
20m       292,087     253,281     86.71%    VOACAP's best band
15m       199,096     143,524     72.09%    MUF-limited, sporadic-E gaps
10m       150,223      90,831     60.46%    Highly solar-dependent
```

### Band Analysis

**160m (45.13%)** — VOACAP's worst band. 160m propagation is dominated by
NVIS (Near Vertical Incidence Skywave) and ground-wave paths under 500 km.
VOACAP's ionospheric model doesn't capture these mechanisms well. IONIS,
trained on real WSPR spots that include short-range 160m contacts, learns
the actual propagation patterns.

**10m (60.46%)** — VOACAP uses monthly median SSN, missing day-to-day
variability and sporadic-E openings that account for many contest QSOs on
10m, especially at solar minimum. IONIS captures these from the training
data distribution.

**40m (84.71%)** and **20m (86.71%)** — VOACAP's strongest bands. These are
the classic F2-layer DX bands where VOACAP's ionospheric model is most
accurate. The remaining gap vs IONIS comes from edge cases: grey line
enhancement, unusual propagation modes, and paths near the MUF limit.

---

## Comparison Query

Both tables live in ClickHouse and can be queried from either agent:

```sql
SELECT
    p.mode,
    count() AS total,
    sum(p.band_open) AS ionis_open,
    sum(v.voacap_band_open) AS voacap_open,
    round(sum(p.band_open) / count() * 100, 2) AS ionis_pct,
    round(sum(v.voacap_band_open) / count() * 100, 2) AS voacap_pct
FROM validation.step_i_paths p
JOIN validation.step_i_voacap v
    USING (tx_lat, tx_lon, rx_lat, rx_lon, freq_mhz, year, month, hour_utc)
GROUP BY p.mode
ORDER BY p.mode
```

---

## Infrastructure

```text
Source table:  validation.step_i_paths   (1,000,000 rows)
Result table:  validation.step_i_voacap  (1,000,000 rows)
DDL:           ki7mt-ai-lab-core/src/16-validation_step_i.sql
Script:        ki7mt-ai-lab-training/scripts/voacap_batch_runner.py
Docs:          ki7mt-ai-lab-docs/docs/tools/voacapl.md
```

---

## Significance

This is a direct comparison between a 1980s physics-based model (VOACAP)
and a 2026 data-driven neural network (IONIS V12) on the same 1M paths.
IONIS's advantage comes from:

1. **Training on real propagation data** — 10.8B WSPR spots capture actual
   ionospheric behavior including sporadic-E, grey line effects, and
   short-range NVIS that physics models miss
2. **Continuous solar features** — IONIS uses actual SFI/Kp values rather
   than monthly median SSN
3. **Learned geography** — the DNN trunk learns path-specific propagation
   patterns (e.g., trans-equatorial, polar) from data rather than relying
   on simplified ionospheric layer models

VOACAP remains a valuable independent baseline: its 76% recall confirms
that the contest QSO dataset is physically reasonable (these paths really
were open), and the band-by-band pattern matches expected ionospheric physics.

### A Note on Mode Context

VOACAP was designed for **SSB voice circuits** — its prediction algorithms,
noise models, and reliability metrics assume analog telephony. The comparison
above uses contest QSOs across all modes (CW, SSB, RTTY, Digital) with uniform
thresholds, which is useful for overall benchmarking.

However, the most meaningful head-to-head is **SSB vs SSB**, where VOACAP is on
its home turf. For digital modes (FT8, FT4, WSPR) and CW with decode thresholds
well below VOACAP's design point, IONIS provides predictions where no comparable
reference model exists. See the [Validation Overview](index.md) for the mode-aware
recall staircase.
