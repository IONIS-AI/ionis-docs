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
- Neural model: IONIS V11, correct physics (SFI+, Kp-, geography, gates)
- Infrastructure: M3 Ultra + 9975WX + DAC link + ClickHouse on NVMe

What's not working:

- Model Pearson +0.24 (explains 6% of variance) — not useful alone
- Signature library has no search layer
- No contest log data ingested
- Two complementary pieces aren't connected

---

### Step E — The Golden Burn

**Status: COMPLETE** (2026-02-05)

Trained V11 Gatekeeper from scratch. 100 epochs, 10M rows, ~12 min on M3 Ultra.
Results: RMSE 2.48 dB, Pearson +0.2376. All physics tests passed.

**Scripts:**

- `scripts/train_v11_final.py` — training (100 epochs, ~12 min on M3 Ultra)
- `scripts/test_v11_final.py` — sensitivity analysis with gate decomposition
- `scripts/verify_v11_final.py` — physics pass/fail verification

**Results:** See `IONIS_V11_FINAL_REPORT.md` for full model card.

**Pass criteria:**

- [x] SFI 70 to 200 benefit: +0.96 dB (positive — correct physics)
- [x] Kp 0 to 9 storm cost: +2.84 dB (positive — correct physics)
- [x] Gates within [0.5, 2.0] on all inputs (verified on 1000 random samples)
- [x] Decomposition math: base + sun_contrib + storm_contrib = predicted (exact)
- [x] Pearson +0.2376 (>= +0.24 threshold — effectively equivalent to V10)

**Does not break:** Nothing before this — fresh training from scratch.

---

### Step F — Aggregated Signatures

**Status: NOT STARTED**

The single biggest improvement: stop predicting individual spot SNR and start
predicting **median SNR per path/band/hour/condition bucket**.

Build an aggregated view in ClickHouse:

- Group by: grid pair + band + hour-of-day + month + SFI range + Kp range
- Output: median SNR, spot count, SNR std, reliability (% spots > -20 dB)

Train the neural model on these buckets instead of raw spots. The antenna
noise, QRM, and multipath average out. Pearson should jump significantly.

**Pass criteria:**

- [ ] Aggregated table built in ClickHouse
- [ ] Retrain on buckets — Pearson improves over Step E
- [ ] RMSE against median SNR per bucket < 2.0 dB
- [ ] Physics still correct (SFI+, Kp-, all directions preserved)

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
