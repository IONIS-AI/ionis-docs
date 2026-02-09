# D to Z: The Digital Twin Roadmap

The mission: build a Digital Twin of the ionosphere from real-world data that
consistently outperforms the ITS/NTIA reference model (VOACAP).

Inspired by CDS (Critical Dimension Scatterometry) in semiconductor metrology:
measure the signature, search the library, reconstruct what you can't see.

## The Three Advantages

| # | Advantage | VOACAP Equivalent |
|---|-----------|-------------------|
| 1 | **13.2B real observations** (WSPR + RBN + contests) — not theory | Monthly median ionosonde models from the 1960s |
| 2 | **195M contest QSOs** — proof the band delivered | Nothing — VOACAP has no ground truth |
| 3 | **Continuous ingest** — new data every 2 minutes, forever | Frozen. Never learns. |

## Data Layers

| Source | Role | CDS Analogy | Volume |
|--------|------|-------------|--------|
| **WSPR** | Signal floor, raw attenuation | Diffraction signature (metrology) | 10.8B spots |
| **RBN** | Traffic density, CW/RTTY coverage | Intermediate inspection | 2.18B spots |
| **Contest Logs** | Binary proof: band was usable | Yield measurement | 195M QSOs (491K files) |
| **Solar Indices** | Environmental conditions | Chamber conditions (temp, pressure) | 76K rows, 2000-2026 |

---

## The Steps

### Step D — Where We Are Now

**Status: COMPLETE**

What's built:

- Data pipeline: 10.8B WSPR spots in ClickHouse, solar backfill (2000-2026)
- CUDA signature engine: 4.4B float4 embeddings in `wspr.silver`
- Neural model: IONIS V12 Signatures, correct physics (SFI+, Kp-, geography, gates)
- Infrastructure: M3 Ultra + 9975WX + DAC link + ClickHouse on NVMe

What was not yet working (at time of Step D completion):

- Signature library has no search layer
- No contest log data ingested — **now 225.7M QSOs in `contest.bronze` (Step H)**
- No RBN data ingested — **now 2.18B spots in `rbn.bronze`**
- Two complementary pieces aren't connected

---

### Step E — The Golden Burn

**Status: COMPLETE** (2026-02-08)

Trained V12 Signatures model on 20M aggregated signature rows from `wspr.signatures_v1`.
100 epochs, ~2h on M3 Ultra. Full reproducibility validation from fresh bronze pipeline.

**Results:**

| Metric | Value |
|--------|-------|
| RMSE | 2.03 dB |
| Pearson | +0.3153 |
| SFI benefit | +0.79 dB (70→200) |
| Kp storm cost | +1.92 dB (0→9) |
| Gates | Sun 1.83, Storm 1.50 |

**Physics Test Grades:**

| Test | Description | Result | Grade |
|------|-------------|--------|-------|
| TST-201 | SFI 70→200 | +2.1 dB | B |
| TST-202 | Kp 0→9 storm cost | +4.0 dB | A |
| TST-203 | D-layer absorption | +0.0 dB | C |
| TST-204 | Polar storm | +2.5 dB | B |
| TST-205 | 10m SFI sensitivity | +2.0 dB | C |
| TST-206 | Grey line twilight | +0.2 dB | C |

**Scripts:**

- `scripts/train_v12_signatures.py` — training on aggregated signatures
- `scripts/test_v12_signatures.py` — sensitivity analysis with gate decomposition
- `scripts/verify_v12_signatures.py` — physics pass/fail verification
- `scripts/oracle_v12.py` — production inference + 35-test suite

**Artifacts:**

- Checkpoint: `models/ionis_v12_signatures.pth`
- Test Spec: `docs/V12_TEST_SPECIFICATION.md`

**Pass criteria:**

- [x] SFI 70→200 benefit: +0.79 dB (positive — correct physics)
- [x] Kp 0→9 storm cost: +1.92 dB (positive — correct physics)
- [x] Gates within [0.5, 2.0] on all inputs
- [x] Pearson +0.3153 (32.7% improvement over V11's +0.2376)
- [x] RMSE 2.03 dB (18% improvement over V11's 2.48 dB)
- [x] Reproducibility validated: fresh bronze → identical results (2026-02-08)

**V13 Improvement Targets (Grade C items):**

- D-layer absorption: need frequency-aware sun sidecar
- 10m SFI sensitivity: need band×SFI interaction term
- Grey line twilight: need hour×longitude feature engineering

**Does not break:** V10/V11 checkpoints preserved. V12 is new production model.

---

### Step F — Aggregated Signatures

**Status: COMPLETE** (2026-02-05)

Built `wspr.signatures_v1` — 93.8M aggregated signatures in ClickHouse (2.3 GiB).
V12 was trained on 20M rows sampled from this table (Step E), confirming the
aggregation approach works.

**Table schema** (13 columns):

- Group by: `tx_grid_4`, `rx_grid_4`, `band`, `hour`, `month`
- Output: `median_snr`, `spot_count`, `snr_std`, `reliability`, `avg_sfi`, `avg_kp`, `avg_distance`, `avg_azimuth`
- Minimum 5 spots per bucket (noise filter)

**Results:**

- V12 trained on aggregated signatures: Pearson +0.3153 (vs V11's +0.2376 on raw spots)
- RMSE 2.03 dB against median SNR per bucket
- Physics preserved: SFI +0.79 dB, Kp +1.92 dB cost (both monotonic)

**Pass criteria:**

- [x] Aggregated table built in ClickHouse — `wspr.signatures_v1`, 93.4M rows
- [x] Retrain on buckets — Pearson +0.3153 (32.7% improvement over V11)
- [x] RMSE against median SNR per bucket: 2.03 dB
- [x] Physics still correct (SFI+, Kp-, both monotonic)

**Does not break:** Step E checkpoint preserved. New training is separate.

---

### Step G — Signature Search Layer

**Status: COMPLETE** (2026-02-08)

Built kNN search over 93.4M aggregated signatures using pure SQL (no FAISS).
Weighted distance metric: geography 60%, hour 20%, month 10%, SFI 5%, Kp 5%.
Band is an exact match filter (can't interpolate across bands).

**Results:**

| Metric | Value |
|--------|-------|
| Query latency | 50-94 ms |
| Physics tests | 7/7 PASS |

**Physics Tests:**

- Day ≥ Night: PASS (day SNR higher than night)
- SFI positive: PASS (high SFI improves SNR)
- D-layer absorption: PASS (160m worse than 20m)
- Polar storm sensitivity: PASS (high lat more affected)
- Sparse path handling: PASS (graceful degradation)
- Query latency: PASS (<1 sec)
- Reference validation: PASS (FN31→JO21, 20m, 14 UTC, June → -21.0 dB)

**Scripts:**

- `scripts/signature_search.py` — kNN search with weighted distance

**Pass criteria:**

- [x] Query: "FN31 to JO21, 20m, 12 UTC, SFI 150, Kp 2" returns top-K matches
- [x] Results include: matched SNR values, spot count, date range of matches
- [x] Query latency < 1 second for single path lookup (50-94 ms achieved)
- [x] Median of K-nearest SNR values is a reasonable prediction

**Does not break:** Steps E and F — search is a new layer, not a replacement.

---

### Step H — Contest Log Ingest

**Status: COMPLETE** (2026-02-08)

Go ingester built for Cabrillo log files. Full download and parsing complete.
QSOs stored in `contest.bronze` (ClickHouse).

**What's done:**

- `contest-download`: 491K Cabrillo files downloaded across 15 contests (3.5 GB)
- `contest-ingest`: V3 parser handles Cabrillo v2 and v3 formats
- 195M QSOs parsed into `contest.bronze` (4.1 GiB in ClickHouse)
- 98.5% of ARRL logs include `HQ-GRID-LOCATOR` headers
- Rate-limited downloads (2-3s delays, max 3 concurrent ARRL streams)
- 15 contests: CQ WW, WPX, WW-RTTY, WPX-RTTY, 160, WW-Digi + ARRL DX CW/Ph, SS CW/Ph, 10m, 160m, RTTY, Digi, IARU HF

**What remains:**

- Callsign-to-grid mapping expansion (Rosetta Stone integration)
- Grid coverage currently 24% for RBN callsigns via `wspr.callsign_grid`
- Cross-source validation rules (contest grids vs WSPR grids vs RBN grids)

**Pass criteria:**

- [x] Cabrillo parser handles CQ WW, CQ WPX, ARRL formats (15 contests)
- [x] QSOs stored with: timestamp, band, mode, both callsigns
- [x] All contest years 2005-2025 ingested (195M QSOs)
- [ ] Grid mapping coverage > 80% of unique callsigns (future enhancement)

**Does not break:** Everything prior — this is new data, additive only.

---

### Step I — Ground Truth Validation

**Status: COMPLETE** (2026-02-08)

The acid test. Compare IONIS and VOACAP predictions against contest log ground truth.
For every contest QSO: the model should predict the band was open.

**Head-to-Head Results (1M QSOs):**

| Model | Recall | Delta |
|-------|--------|-------|
| **IONIS** | **90.42%** | — |
| VOACAP | 75.98% | -14.4 pts |

**IONIS by Mode:**

| Mode | Recall |
|------|--------|
| CW | 99.17% |
| Digital | 100.00% |
| RTTY | 87.28% |
| Phone (SSB) | 78.16% |

**IONIS by Band:**

| Band | IONIS | VOACAP | Notes |
|------|-------|--------|-------|
| 160m | 99.86% | 45.13% | VOACAP misses NVIS/ground-wave |
| 80m | 98.62% | 74.98% | |
| 40m | 96.52% | 84.71% | |
| 20m | 87.87% | 86.71% | VOACAP's best band (F2 physics) |
| 15m | 84.97% | 72.09% | |
| 10m | 85.59% | 60.46% | VOACAP misses sporadic-E |

**Grey Line Analysis:**
- During transition: 84.96%
- Normal conditions: 91.07%
- Gap: -6.11% (confirms V13 target for hour×longitude features)

**Key Insight:** VOACAP excels at classic F2 propagation (20m). IONIS captures
NVIS (160m) and sporadic-E (10m) because the training data includes those openings.
Complementary strengths — different physics models.

**Scripts:**
- `scripts/validate_v12.py` — IONIS validation with mode-weighted thresholds
- `scripts/voacap_batch_runner.py` — VOACAP batch processing (9975)

**Data:**
- `validation.step_i_paths` — 1M test paths with IONIS predictions
- `validation.step_i_voacap` — VOACAP predictions for same paths

**Pass criteria:**

- [x] 1M contest QSOs validated
- [x] For each QSO, query IONIS: "was this band open for this path at this time?"
- [x] Band-open accuracy > 85% (IONIS: 90.42%)
- [x] Compare same question against VOACAP prediction (VOACAP: 75.98%)
- [x] Measure where each tool excels (VOACAP: 20m F2 | IONIS: 160m NVIS, 10m Es)

**V13 Improvement Targets:**
- Phone (SSB) recall: 78% → 85%+
- Grey line gap: -6% → 0% (hour×longitude features)

**Does not break:** Nothing — this is measurement only.

---

### V13 Combined Model — DXpedition Synthesis

**Status: COMPLETE** (2026-02-09)

Addressed the coverage gap: WSPR doesn't reach rare DXCC entities. Solution:
cross-reference GDXF Mega DXpeditions catalog (468 DXpeditions) with RBN
skimmer data to extract real propagation signatures from rare locations.

**Data Synthesis:**

| Source | Signatures | Coverage |
|--------|------------|----------|
| WSPR | 20M (sampled from 93.4M) | Common paths |
| RBN DXpedition | 91K × 50 (upsampled) | 152 rare DXCC entities |

**Key Innovation:** Per-source per-band Z-score normalization removes the ~35 dB
offset between WSPR weak-signal (-18 dB mean) and RBN high-power (+17 dB mean).
Model learns relative propagation quality, not absolute power levels.

**Results:**

| Metric | Value |
|--------|-------|
| RMSE | 0.60σ (~4.0 dB) |
| Pearson | +0.2865 |
| SFI benefit (70→200) | +5.2 dB |
| Kp storm cost (0→9) | +10.4 dB |
| Storm/Sun ratio | 4.0:1 |

**Physics Tests:** 4/4 PASS (storm sidecar, sun sidecar, gate range, decomposition)

**Rare DXCC Coverage (examples):**

- Bouvet Island (3Y)
- Heard Island (VK0H)
- South Sandwich (VP8)
- Peter I Island (3Y0)
- Navassa Island (KP1)

**Scripts:**

- `scripts/train_v13_combined.py` — WSPR + RBN DXpedition training
- `scripts/test_v13_combined.py` — sensitivity analysis (Z-normalized)
- `scripts/verify_v13_combined.py` — physics verification (4/4 pass)

**Artifacts:**

- Checkpoint: `models/ionis_v13_combined.pth`
- GDXF catalog: `shared-context/gdxf/gdxf-catalog.json`
- RBN signatures: `rbn.dxpedition_signatures` (91,301 rows)

**Note:** Pearson is lower than V12 (+0.2865 vs +0.3153) — expected when
learning from heterogeneous data with different physics regimes. The win
is **coverage**: 152 rare DXCC entities that WSPR never reaches.

**Does not break:** V12 checkpoint preserved. V13 is new production model.

---

### Steps J through Y — The Long Road

These steps evolve based on what we learn. Current priorities:

**Step J — Unified Oracle Interface** (Next)

Combine neural oracle + signature search into single prediction tool:

- Single CLI/module: path + conditions → neural prediction + historical evidence
- Confidence weighting: oracle better on unseen paths, signatures on dense paths
- Output: combined SNR, condition, agreement score, top matching signatures

**V14 Strategy — Contest + RBN Synthesis**

Fill the gap between common paths (WSPR) and rare DXpeditions (RBN DX):

- Contest logs have useless 599 RST reports — no SNR truth
- RBN skimmers run at maximum speed during contests — real SNR measurements
- Cross-reference: contest QSOs with RBN spots (same callsign, band, ±5 min)
- Result: SNR-enriched contest QSOs for semi-rare grids (active contest stations)

**Other Directions:**

- **Coverage Analysis**: Map observation density across all 32,400 possible
  Maidenhead grids. Quantify permanent gaps (ocean, uninhabited), sparse regions,
  and high-density coverage. Use interpolation distance as a confidence metric.
  See [Coverage & Confidence](../methodology/coverage.md).
- **Feature expansion**: geomagnetic latitude, MUF proxy, ionospheric tilt
- **PSK Reporter ingest**: FT8 data for denser coverage (live only, no bulk historical)
- **Temporal refinement**: 15-minute prediction windows instead of hourly
- **Mode prediction**: not just "band open" but "open for SSB vs CW vs FT8"
- **Edge deployment**: quantized model for offline/portable use
- **Feedback loop**: live contest data correcting predictions in real-time
- **Solar cycle coverage**: validate across full solar min-to-max range

Each step gets defined when the previous step is done and we know what
the data is telling us.

---

### Step Z — The Goal

IONIS consistently outperforms the reference model on a standardized test:

- Take 100 real paths across multiple bands
- Run both predictions for multiple days across different solar conditions
- Compare against actual WSPR/contest observations

**Pass criteria:**

- [ ] Pearson r (IONIS vs actual) > Pearson r (reference vs actual)
- [ ] RMSE (IONIS) < RMSE (reference)
- [ ] Band-open accuracy (IONIS) > Band-open accuracy (reference)
- [ ] IONIS shows improvement on > 90% of test paths
- [ ] Results are reproducible and documented

---

## Rules of the Road

1. **Each step has pass/fail tests.** No moving forward without passing.
2. **Each step must not break prior steps.** Regression = stop and fix.
3. **Checkpoints are sacred.** Never overwrite a working model.
4. **The path is not a straight line.** Steps may change. The goal doesn't.
5. **Plain language.** If it can't be explained simply, it's not understood yet.

---

*Last updated: 2026-02-09*
