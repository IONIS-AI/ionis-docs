---
description: >-
  How IONIS replaces empirical VOACAP physics with physics-constrained PyTorch
  neural networks trained on 13 billion real amateur radio observations. V20
  results, ongoing refinements, and the path toward IRI-derived features.
---

# From Empirical Physics to Neural Prediction

**While legacy tools like VOACAP rely on empirical formulas derived from 1960s
ionospheric measurement campaigns, IONIS uses physics-constrained PyTorch
neural networks to predict HF path viability from first principles of observed
behavior. Trained on over 13 billion real amateur radio observations from WSPR,
the Reverse Beacon Network, and contest logs, IONIS captures nonlinear
ionospheric behaviors — sporadic-E openings, real-time solar variability,
grey-line enhancement — that traditional mathematical models miss. On 1 million
real contest paths, IONIS achieves 96.38% recall versus VOACAP's 75.82%.**

VOACAP (Voice of America Coverage Analysis Program) has been the standard HF
propagation prediction tool since the 1980s. Built on decades of ionospheric
research at NTIA/ITS, it uses empirical ionospheric coefficients and ray-tracing
geometry to estimate circuit reliability for voice communication.

IONIS takes a fundamentally different approach: learn propagation behavior
directly from 13 billion real radio observations, constrained by known physics.

This page documents where we are, what we've proven, and what we're still
working on.

## Validating Neural Networks vs. VOACAP (V20 Baseline)

IONIS V20 was the first production model validated against both historical
contest data and live PSK Reporter observations. The results established that
a physics-constrained neural network can outperform empirical models on real
amateur radio paths.

### Head-to-Head: 1 Million Contest Paths

Both models were given 1M real contest QSOs (CQ WW, CQ WPX, ARRL DX — 2005
to 2025) and asked: "was this band open?" Every QSO actually happened, so the
ground truth is always YES.

| Model | Recall | Delta |
|-------|--------|-------|
| IONIS V20 | **96.38%** | — |
| VOACAP 0.7.5 | 75.82% | -20.56 pp |

The gap was largest on **10m (+38.1 pp)** where VOACAP misses sporadic-E and
day-to-day solar variability, and on **SSB (+22.6 pp)** — the mode VOACAP was
specifically designed for.

See [IONIS vs VOACAP Comparison](validation/step_i_voacap_comparison.md) for
full results by mode and band.

### Independent Live Validation

V20 achieved **84.14% recall** on 100K live PSK Reporter spots the model had
never seen during training. This confirmed that IONIS generalizes to
independent real-time data, not just historical patterns.

### Physics Constraints Hold

The architecture enforces two non-negotiable ionospheric laws through monotonic
neural network sidecars:

- **Sun sidecar**: Higher solar flux (SFI) always improves propagation (+0.482σ, ~3.2 dB)
- **Storm sidecar**: Higher geomagnetic activity (Kp) always degrades propagation (+3.487σ, ~23.4 dB)

These constraints cannot be overridden by the DNN trunk. See
[Monotonic Sidecars](architecture/sidecars.md) for the full design.

## Refining the Deep Learning Architecture: Auroral Zones and Day/Night Physics

V20 proved the architecture works. The ongoing refinement series focuses on
giving the model better tools to distinguish *when* and *where* propagation
behaves differently — auroral zone vulnerability, band-specific day/night
behavior, and the separation of storm physics from temporal artifacts.

### Modeling Auroral Zone Vulnerability for Polar HF Paths

**Problem**: V20 treated all paths equally during geomagnetic storms. In
reality, a path crossing the auroral zone (high latitude) is far more
vulnerable to storm absorption than an equatorial path at the same Kp.

**Solution**: `vertex_lat` — the latitude of the highest point on the great
circle path. Computed from TX/RX grids via spherical trigonometry:

```
vertex_lat = arccos(|sin(bearing) * cos(tx_lat)|)
```

High vertex latitude means the path crosses the polar region where storm
particles precipitate. Low vertex latitude means the path stays in the
mid-latitudes where storms have minimal effect. This gives the Kp sidecar
path-specific context instead of treating storms as a global scalar.

### The 10 MHz Pivot: Mathematically Modeling Day and Night HF Bands

**Problem**: Darkness helps low-band propagation (160m, 80m, 40m) but kills
high-band propagation (10m, 15m, 17m, 20m). The crossover is around 10 MHz
(30m band). V20 had no way to express this — the model could learn that
darkness matters, but not that it matters *in opposite directions* depending
on frequency.

**Solution**: Solar depression angles at both TX and RX locations, combined
with frequency-centered cross-products:

- `tx_solar_dep`, `rx_solar_dep` — continuous day/night indicators (positive = daylight, negative = darkness depth)
- `freq_centered = (freq_mhz - 10.0) / scale` — centers frequency around the 10 MHz ionospheric crossover
- `freq_x_tx_dark`, `freq_x_rx_dark` — cross-products that flip sign at the pivot

When the cross-product is positive (high band + darkness, or low band +
daylight), propagation is degraded. When negative (high band + daylight, or
low band + darkness), propagation is enhanced. The model learns the magnitude;
the math enforces the direction.

### Isolating Geomagnetic Storm Physics from Temporal Artifacts

An unexpected discovery during V21 training: the V20 storm sidecar's +3.49σ
cost was approximately 60% temporal contamination. The sidecar had been
compensating for missing time-of-day features — storms correlate with certain
hours, and without explicit day/night tools, the Kp sidecar absorbed that
temporal signal.

Adding solar depression angles gave the DNN trunk its own time-of-day tools.
The Kp sidecar shed its temporal weight and distilled down to pure geomagnetic
storm physics. This is the correct behavior: the sidecar should model
absorption and fading, not sunrise timing.

The SFI/Kp asymmetry (~3:1 ratio in sigma) is itself physically meaningful.
Solar flux acts like a power plant — it lifts the MUF with diminishing returns
as ionization saturates. Geomagnetic storms act like a governor — D-layer
absorption is violent and nonlinear with no ceiling. Building is bounded;
destroying is not.

### Scaling Training Data: Integrating 2 Billion CW/RTTY Observations

V17–V19 failed when RBN data (2.18B CW/RTTY spots) was added to training.
The post-mortem revealed this wasn't because RBN data was poison — the
architectural constraints were incomplete. With the V16 Physics Laws intact
plus the frequency pivot, V22 tests whether the "container" is now strong
enough to hold the full dataset.

RBN provides critical low-band coverage: 3.18M 160m signatures (nearly 2x
WSPR's 1.69M on that band) and 16.3% low-band concentration versus WSPR's
8.1%. If the model needs to learn 160m behavior, it needs RBN data to learn
from.

## Where VOACAP Still Has Physics We Don't

VOACAP's empirical coefficients encode 60 years of ionospheric measurement
campaigns. Some of that physics is not yet available to IONIS:

**Path-specific ionospheric state**: VOACAP uses ionospheric models to compute
the critical frequency (foF2) and peak height (hmF2) at each point along the
path. IONIS receives only a global solar flux index — two paths at the same
SFI can have wildly different ionospheric conditions depending on latitude,
local time, season, and magnetic geometry.

**MUF estimation**: VOACAP computes the Maximum Usable Frequency for each
circuit. IONIS infers this indirectly from frequency, distance, and solar
features. A direct MUF signal would tell the model immediately whether the
operating frequency can propagate.

**D-layer absorption**: VOACAP models absorption through the D and E layers
explicitly. IONIS handles this through the Kp sidecar globally, without
path-specific absorption context.

These gaps point directly to the next phase of model development.

## Next: Physics Model Integration

Two open-source tools fill the gaps between what IONIS has learned and what
ionospheric physics can provide:

**dvoacap-python** (pure Python VOACAP port) enables systematic comparison:
generate VOACAP predictions for every path in the validation set, then build a
diagnostic matrix showing where IONIS succeeds and VOACAP fails, where VOACAP
succeeds and IONIS fails, and where both struggle. The paths where VOACAP is
right and IONIS is wrong point to known physics we haven't captured yet.

**PyIRI** (pure Python IRI-2020) provides the path-specific ionospheric
features IONIS currently lacks. IRI computes foF2, hmF2, and foE for any
location, date, and solar activity level — covering the full training dataset
from 1958 to present with no coverage gaps. The foF2/frequency ratio is
particularly valuable: it tells the model directly whether the operating
frequency is above or below the MUF at each point along the path.

These features would replace the global SFI scalar with a path-specific
ionospheric scalpel — giving the model the same physics VOACAP has, plus
everything it learns from 13 billion observations that VOACAP has never seen.

## The Larger Picture

Empirical models like VOACAP represent the ceiling of what physics alone can
predict from averaged ionospheric measurements. Neural networks like IONIS
represent what machine learning can extract from billions of individual
observations. Neither approach is complete on its own.

The path forward combines both: use physics models to diagnose where the neural
network is weak, use ionospheric models to provide features the neural network
can't derive from radio data alone, and use the neural network to capture
patterns that no empirical model can express — sporadic-E openings,
trans-equatorial propagation, grey-line enhancement, and the thousands of
subtle effects buried in 13 billion data points.

The logs were speaking for decades. Now we're listening — and teaching a model
to understand what they're saying.

## Project Resources

- **Validation Suite**: [ionis-validate on PyPI](https://pypi.org/project/ionis-validate/) — run the 62-test physics battery locally
- **Live Predictions**: [ham-stats.com](https://ham-stats.com) — band conditions and IONIS predictions updated every 3 hours
- **Source Code**: [IONIS-AI on GitHub](https://github.com/IONIS-AI) — all repos, open source, GPLv3
- **VOACAP Comparison Data**: [Full results by mode and band](validation/step_i_voacap_comparison.md)
- **Model Architecture**: [IonisGate](architecture/ionisgate.md) and [Monotonic Sidecars](architecture/sidecars.md)
