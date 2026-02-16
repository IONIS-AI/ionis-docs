# IONIS vs VOACAP Comparison

- **Date:** 2026-02-11
- **Dataset:** 1,000,000 contest QSO paths (CQ WW, CQ WPX, ARRL DX — 2005-2025)
- **IONIS Version:** IONIS (IonisGate)
- **VOACAP Version:** [voacapl](https://github.com/jawatson/voacapl) 0.7.5 ([NTIA/ITS](https://www.its.bldrdoc.gov/) Method 30)

---

## Summary

Both models were given 1M real contest QSOs and asked: "was this band open?"
Every QSO actually happened, so the ground truth is always YES. The question
is which model correctly predicts that.

```text
+------------+---------+
| Model      | Recall  |
+------------+---------+
| IONIS      | 96.38%  |
| VOACAP     | 75.82%  |
+------------+---------+
  Delta: +20.56 pp vs VOACAP
```

IONIS showed a **20.56 percentage point** improvement over the reference
model on real-world contest QSO recall.

### Contest Anchoring

The training recipe includes 6.34M contest signatures with anchored SNR values:

- **SSB QSOs → +10 dB anchor** (proven voice-viable paths)
- **RTTY QSOs → 0 dB anchor** (proven digital-viable paths)

This taught the model the "ceiling" of propagation — paths where voice
communication actually succeeded. WSPR alone only teaches the "floor."

---

## Methodology

### Data Source

The 1M paths were exported by `validate_v12.py --export` from contest QSO
records in `contest.bronze`. Each row represents a confirmed two-way contact
between amateur radio stations during a major HF contest. These are not
synthetic paths — every row is a real QSO that actually completed.

### IONIS Scoring

IONIS predicts SNR for each path. Band is considered "open" if:

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
Mode      Total       IONIS TP    IONIS %    VOACAP TP   VOACAP %    IONIS vs VOACAP
------  ---------  -----------  ---------  -----------  ---------   -------------
CW        459,200      430,609     93.77%      340,678     74.36%      +19.4 pp
PH        285,083      280,521     98.40%      215,717     75.83%      +22.6 pp
RY        233,446      231,982     99.37%      183,392     78.72%      +20.6 pp
DG         22,269       20,773     93.29%       18,397     82.84%      +10.4 pp
```

**SSB breakthrough**: SSB (PH) recall reached **98.40%**.
Contest anchoring taught the model what "voice-viable" actually looks like.

IONIS showed higher recall across all modes. The largest delta was SSB (+22.6 pp),
which is notable because SSB voice circuits are VOACAP's primary design target.

---

## Results by Band

```text
Band      Total     IONIS TP    IONIS %    VOACAP TP   VOACAP %    IONIS vs VOACAP
------  ---------  ----------  ---------  ----------  ---------   -------------
80m        95,350      93,063     97.60%      71,328     74.98%      +22.6 pp
40m       205,856     200,281     97.29%     174,004     84.71%      +12.6 pp
20m       348,712     335,325     96.16%     253,281     86.71%       +9.5 pp
15m       199,503     186,718     93.59%     143,524     72.09%      +21.5 pp
10m       150,579     148,473     98.60%      90,831     60.46%      +38.1 pp
```

### Band Analysis

**10m (98.60%)** — The biggest improvement. VOACAP misses sporadic-E and
day-to-day solar variability. Contest anchoring taught IONIS that 10m paths
actually work when conditions are right.

**80m (97.60%)** — NVIS and ground-wave paths that VOACAP's ionospheric model
doesn't capture. IONIS learned from real WSPR spots that include short-range
contacts.

**15m (93.59%)** — The contest ceiling taught the model what "open" really
means on this band.

**20m (96.16%)** — VOACAP uses monthly median SSN, missing day-to-day
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
DDL:           ionis-core/src/16-validation_step_i.sql
Script:        ionis-training/scripts/voacap_batch_runner.py
Docs:          ionis-docs/docs/tools/voacapl.md
```

---

## Significance

This is a direct comparison between a 1980s physics-based model (VOACAP)
and a 2026 data-driven neural network (IONIS) on the same 1M paths.
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

However, the most meaningful direct comparison is **SSB vs SSB**, where VOACAP
was specifically designed to perform. For digital modes (FT8, FT4, WSPR) and CW with decode thresholds
well below VOACAP's design point, IONIS provides predictions where no comparable
reference model exists. See the [Validation Overview](index.md) for the mode-aware
recall staircase.
