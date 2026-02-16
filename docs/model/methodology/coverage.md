# Coverage & Confidence

> *Garbage in, garbage out. If we don't have coverage, we don't have a
> high-confidence model.*

## The Problem

IONIS learns from real observations. But the ionosphere doesn't care about
our data collection — paths exist whether anyone is listening or not. The
model can only be as good as the data that feeds it.

**32,400 possible grids.** The Maidenhead grid system has 18 longitude fields
(A-R) × 18 latitude fields × 10 longitude squares × 10 latitude squares =
32,400 unique 4-character grid locators.

Not all grids are equal:

- **Dense coverage**: FN31 (Northeast US), JN48 (Central Europe) — thousands
  of active stations, high observation counts
- **Sparse coverage**: Remote land areas with few stations — limited observations
- **Permanent gaps**: Mid-ocean grids, Antarctica, uninhabited regions — no
  stations possible (but propagation still happens)

## Interpolation vs Observation

When IONIS has direct observations for a path (e.g., FN31→JN48 on 20m at 14 UTC),
confidence is high. The model learned from actual measurements.

When IONIS has no observations for a path, it must interpolate from nearby grids,
similar hours, adjacent bands. The further the interpolation, the lower the
confidence should be.

**Analogy**: Weather forecasts are more accurate where there are weather stations.
Predictions for the middle of the ocean rely on satellite data and models, not
ground truth. Same principle here.

## Coverage as a Confidence Metric

A coverage analysis would provide:

1. **Observation density map**: For each of the 32,400 grids, count observations
   (as TX, as RX, or both). Visualize as a heatmap.

2. **Gap classification**:
   - **Permanent gaps**: Ocean, uninhabited — mark as "interpolation only"
   - **Sparse coverage**: < N observations — mark as "low confidence"
   - **Dense coverage**: > M observations — mark as "high confidence"

3. **Interpolation distance**: For any query path, calculate the "distance" to
   the nearest observed signatures. Longer distance = lower confidence.

4. **Per-band breakdown**: 10m coverage differs from 40m coverage. Report
   confidence per band.

## Why This Matters

When IONIS predicts "20m open from FN31 to JN48 at 14 UTC with SNR -8 dB",
a coverage metric could add:

- **Confidence: HIGH** — 50,000 observations for this path/band/hour combination
- **Confidence: MEDIUM** — 500 observations, reliable pattern
- **Confidence: LOW** — 5 observations, use with caution
- **Confidence: INTERPOLATED** — No direct observations, prediction based on
  nearby grids

This helps users understand when to trust the prediction and when to be skeptical.

## Implementation Notes

The coverage analysis is a roadmap candidate, not yet implemented. When built:

- Query `wspr.signatures_v2_terrestrial` for grid observation counts
- Cross-reference with RBN and contest data for additional coverage
- Generate static heatmaps for documentation
- Consider adding confidence scores to IONIS inference output

## Related

- [Aggregated Signatures](step_f_signatures.md) — how observations become signatures

---

*Last updated: 2026-02-08*
