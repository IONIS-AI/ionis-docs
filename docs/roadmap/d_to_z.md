# D to Z: The Digital Twin Roadmap

The mission: build a Digital Twin of the ionosphere from real-world data that
beats VOACAP — every time, by a substantial margin.

Inspired by CDS (Critical Dimension Scatterometry) in semiconductor metrology:
measure the signature, search the library, reconstruct what you can't see.

## The Three Advantages

| # | Advantage | VOACAP Equivalent |
|---|-----------|-------------------|
| 1 | **10.8B WSPR signatures** — real observations, not theory | Monthly median ionosonde models from the 1960s |
| 2 | **Millions of contest QSOs** — proof the band delivered | Nothing — VOACAP has no ground truth |
| 3 | **Continuous ingest** — new data every 2 minutes, forever | Frozen. Never learns. |

## Data Layers

| Source | Role | CDS Analogy | Volume |
|--------|------|-------------|--------|
| **WSPR** | Signal floor, raw attenuation | Diffraction signature (metrology) | 10.8B spots |
| **Contest Logs** | Binary proof: band was usable | Yield measurement | Millions of QSOs |
| **RBN / PSK Reporter** | Traffic density, mode coverage | Intermediate inspection | Billions of spots |
| **Solar Indices** | Environmental conditions | Chamber conditions (temp, pressure) | 76K rows, 2000-2026 |

---

## The Steps

### Step D — Where We Are Now

**Status: COMPLETE**

What's built:

- Data pipeline: 10.8B WSPR spots in ClickHouse, solar backfill (2000-2026)
- CUDA signature engine: 4.4B float4 embeddings in `wspr.model_features`
- Neural model: IONIS V12 Signatures, correct physics (SFI+, Kp-, geography, gates)
- Infrastructure: M3 Ultra + 9975WX + DAC link + ClickHouse on NVMe

What was not yet working (at time of completion):

- Signature library has no search layer
- No contest log data ingested
- Two complementary pieces aren't connected

---

### Step E — The Golden Burn

**Status: COMPLETE** (2026-02-05)

Trained V12 Signatures model on 20M aggregated signature rows from `wspr.signatures_v1`.
100 epochs, ~15 min on M3 Ultra. Full NASA-style test suite with physics scoring.

**Results:**

| Metric | Value |
|--------|-------|
| RMSE | 2.05 dB |
| Pearson | +0.3051 |
| Physics Score | 76.7/100 (Grade B) |
| Test Suite | 35/35 PASS |

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

- [x] SFI 70→200 benefit: +2.1 dB (positive — correct physics)
- [x] Kp 0→9 storm cost: +4.0 dB (positive — correct physics)
- [x] Gates within [0.5, 2.0] on all inputs
- [x] Pearson +0.3051 (29% improvement over V11's +0.2376)
- [x] RMSE 2.05 dB (17% improvement over V11's 2.48 dB)
- [x] All 35 automated tests pass
- [x] No geographic bias (EU vs Africa: 0.0 dB difference)
- [x] Zero variance on reproducibility test (100 runs)

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

- V12 trained on aggregated signatures: Pearson +0.3051 (vs V10's +0.24 on raw spots)
- RMSE 2.05 dB against median SNR per bucket
- Physics preserved: SFI +2.1 dB, Kp +4.0 dB cost

**Pass criteria:**

- [x] Aggregated table built in ClickHouse — `wspr.signatures_v1`, 93.8M rows
- [x] Retrain on buckets — Pearson +0.3051 (29% improvement over V11)
- [x] RMSE against median SNR per bucket: 2.05 dB
- [x] Physics still correct (SFI+, Kp-, all directions preserved)

**Does not break:** Step E checkpoint preserved. New training is separate.

---

### Step G — Signature Search Layer

**Status: NOT STARTED**

Build the kNN search that makes the signature library queryable.
Given current conditions (path, band, hour, SFI, Kp), find the K nearest
historical signatures and report what happened.

Options: ClickHouse vector search, FAISS on GPU, or custom ANN index.

**Pass criteria:**

- [ ] Query: "FN31 to JO21, 20m, 12 UTC, SFI 150, Kp 2" returns top-K matches
- [ ] Results include: matched SNR values, spot count, date range of matches
- [ ] Query latency < 1 second for single path lookup
- [ ] Median of K-nearest SNR values is a reasonable prediction

**Does not break:** Steps E and F — search is a new layer, not a replacement.

---

### Step H — Contest Log Ingest

**Status: NOT STARTED**

Write a Go ingester for Cabrillo log files. Parse QSO records into a new
ClickHouse table (`wspr.contest_receipts` or similar).

Key challenge: **Callsign-to-Grid mapping**. Contest logs have callsigns
and exchanges, not grid squares. Solutions:

1. Build a callsign-to-grid lookup from WSPR data (which has grids)
2. Parse contest exchanges for state/province/zone geographic boxing
3. Use external callsign databases where available

**Pass criteria:**

- [ ] Cabrillo parser handles CQ WW, CQ WPX formats
- [ ] QSOs stored with: timestamp, band, mode, both callsigns, mapped grids
- [ ] At least one contest year fully ingested
- [ ] Grid mapping coverage > 80% of unique callsigns

**Does not break:** Everything prior — this is new data, additive only.

---

### Step I — Ground Truth Validation

**Status: NOT STARTED**

The acid test. Compare IONIS predictions (model + signature search) against
contest log ground truth.

For every contest QSO: the model should predict the band was open. If it
says "closed" when a contact was made, the model is wrong.

**Pass criteria:**

- [ ] Take a contest weekend's QSOs
- [ ] For each QSO, query IONIS: "was this band open for this path at this time?"
- [ ] Band-open accuracy > 85% (IONIS correctly predicts open when QSO exists)
- [ ] Compare same question against VOACAP prediction
- [ ] IONIS accuracy > VOACAP accuracy on the same test set

**Does not break:** Nothing — this is measurement only.

---

### Steps J through Y — The Long Road

These steps are not yet defined. They depend on what we learn at Steps F
through I. Possible directions:

- **Feature expansion**: geomagnetic latitude, MUF proxy, ionospheric tilt
- **RBN/PSK Reporter ingest**: FT8 and CW skimmer data for denser coverage
- **Temporal refinement**: 15-minute prediction windows instead of hourly
- **Mode prediction**: not just "band open" but "open for SSB vs CW vs FT8"
- **Edge deployment**: quantized model for offline/portable use
- **Feedback loop**: live contest data correcting predictions in real-time
- **Solar cycle coverage**: validate across full solar min-to-max range

Each step gets defined when the previous step is done and we know what
the data is telling us.

---

### Step Z — The Goal

IONIS beats VOACAP on a standardized test:

- Take 100 real paths across multiple bands
- Run both predictions for multiple days across different solar conditions
- Compare against actual WSPR/contest observations

**Pass criteria:**

- [ ] Pearson r (IONIS vs actual) > Pearson r (VOACAP vs actual)
- [ ] RMSE (IONIS) < RMSE (VOACAP)
- [ ] Band-open accuracy (IONIS) > Band-open accuracy (VOACAP)
- [ ] IONIS wins on > 90% of test paths
- [ ] Results are reproducible and documented

---

## Rules of the Road

1. **Each step has pass/fail tests.** No moving forward without passing.
2. **Each step must not break prior steps.** Regression = stop and fix.
3. **Checkpoints are sacred.** Never overwrite a working model.
4. **The path is not a straight line.** Steps may change. The goal doesn't.
5. **Plain language.** If it can't be explained simply, it's not understood yet.

---

*Last updated: 2026-02-05*
