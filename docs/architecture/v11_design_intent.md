# IONIS V11/V12 "Gatekeeper" — Architecture

!!! success "Status: COMPLETE"
    V11 trained and validated. V12 (production) trained on aggregated signatures.

    - **V12 RMSE**: 2.03 dB
    - **V12 Pearson**: +0.3153
    - **Physics Score**: 74.2/100 (Grade C)
    - **Test Suite**: 35/35 PASS

## Problem Statement

V10 validation tests (POL-01 and FREQ-01) revealed a fundamental limitation of the additive sidecar architecture:

```
V10: output = DNN(geo) + SunSidecar(sfi) + StormSidecar(kp)
```

The sidecars produce **global constants** — the same SFI benefit and Kp penalty for every path on Earth:

| Finding | Test | Impact |
|---------|------|--------|
| Storm cost is flat +1.12 dB everywhere | POL-01 | Polar paths should suffer 3–5x more |
| SFI benefit is flat +0.92 dB on all bands | FREQ-01 | 10m should benefit far more than 160m |
| No geographic modulation of solar effects | Both | Equatorial vs. auroral zones identical |

The DNN cannot modulate the sidecars because the interaction is purely additive. The sidecars are "tone-deaf" to geography and frequency.

## Solution: Multiplicative Interaction Gates

```
V11: output = base_snr + sun_scaler × SunSidecar(sfi)
                       + storm_scaler × StormSidecar(kp)
```

The DNN splits into a **shared trunk** with **three heads**:

```
Input (13 features)
    │
    ├── features 0-10 (geography/time)
    │       │
    │    Trunk: 11 → 512 → 256
    │       │
    │       ├── Base Head: 256 → 128 → 1  ──────────► base_snr
    │       │
    │       ├── Sun Scaler: 256 → 64 → 1 → gate() ──► sun_scaler ∈ [0.5, 2.0]
    │       │                                              │
    │       └── Storm Scaler: 256 → 64 → 1 → gate() ──► storm_scaler ∈ [0.5, 2.0]
    │                                                      │
    ├── feature 11 (sfi) ──► SunSidecar(8) ──────── × sun_scaler ──► sun_term
    │                                                                    │
    └── feature 12 (kp_penalty) ──► StormSidecar(8) ── × storm_scaler ──► storm_term
                                                                          │
                                                Output = base_snr + sun_term + storm_term
```

### Gate Function

```python
gate(x) = 0.5 + 1.5 × sigmoid(x)
```

| Property | Value | Purpose |
|----------|-------|---------|
| Range | [0.5, 2.0] | Never zero, never too large |
| Identity | x = -ln(2) ≈ -0.693 | gate(-0.693) = 1.0 |
| Differentiable | Everywhere | Standard backprop |
| Bounded | Always | Cannot reverse sidecar direction |

The gate acts as a **volume control**: it can turn the sidecar effect up (to 2x) or down (to 0.5x), but it can never mute it entirely or reverse it. This preserves the monotonic physics guarantee.

### What the Gates Enable

| Scenario | sun_scaler | storm_scaler | Physical Meaning |
|----------|------------|-------------|------------------|
| 10m equatorial path | > 1.0 | < 1.0 | Strong SFI benefit, mild storm impact |
| 160m high-latitude path | < 1.0 | > 1.0 | Weak SFI benefit, severe storm impact |
| 20m mid-latitude (reference) | ≈ 1.0 | ≈ 1.0 | V10-equivalent baseline |

## Parameter Budget

| Component | V10 | V11 | Delta |
|-----------|-----|-----|-------|
| DNN / Trunk (11→512→256) | 170,497* | 137,472 | shared |
| Base head (256→128→1) | — | 33,025 | split from V10 DNN |
| Sun scaler head (256→64→1) | — | 16,513 | **new** |
| Storm scaler head (256→64→1) | — | 16,513 | **new** |
| Sun Sidecar (1→8→1) | 25 | 25 | 0 |
| Storm Sidecar (1→8→1) | 25 | 25 | 0 |
| **Total** | **170,547** | **203,573** | **+19.4%** |

*V10 DNN (11→512→256→128→1) is split into trunk + base_head in V11, accounting for the same layers.

## Training Strategy: Three Phases

### Phase A — V10 Warm-Start

**Goal**: Recover V10 performance with the new architecture.

1. Load V10 weights into trunk and base_head
2. Initialize scaler heads to output gate = 1.0 (bias = -0.693, weights zeroed)
3. **Freeze** both scaler heads
4. Train trunk + base_head + sidecars

**Exit criteria**: RMSE ≤ 2.50 dB (within 0.02 of V10 baseline)

### Phase B — Gate Awakening

**Goal**: Allow geographic modulation to emerge.

1. **Unfreeze** scaler heads with slow LR (1e-5)
2. Enable anti-collapse regularization (scaler variance loss, λ = 0.01)
3. Differential LR: trunk 1e-5 | base_head 1e-5 | scaler heads 1e-5 | sidecars 1e-3

**Expected signals**:

- Storm scaler variance should increase (polar vs. equatorial differentiation)
- Sun scaler should correlate with freq_log (band-dependent SFI sensitivity)
- RMSE should decrease as geographic modulation explains residual variance

### Phase C — Fine-Tuning

**Goal**: Polish the model with all components unfrozen.

1. All components unfrozen
2. Reduce λ to 0.001 (lighter regularization)
3. Standard CosineAnnealingLR schedule

**Exit criteria**: RMSE < V10, physics verification passes, gates show meaningful variance

## Anti-Collapse Regularization

Without explicit encouragement, the optimizer may find it easier to keep the scaler heads constant (collapsing to gate ≈ 1.0 everywhere). The **scaler variance loss** prevents this:

```python
L_var = -λ × (Var(sun_gate) + Var(storm_gate))
```

| Parameter | Phase B | Phase C |
|-----------|---------|---------|
| λ | 0.01 | 0.001 |
| Effect | Encourages gate diversity | Light touch |

Negative variance is added to the total loss, so the optimizer is incentivized to produce diverse gate values across the batch. If the gates collapse to a constant, the variance term becomes zero and the penalty is maximized.

## Key Constraint: Sidecars Remain Locked

The sidecars are **unchanged** from V10:

| Property | Value | Enforced by |
|----------|-------|-------------|
| Architecture | MonotonicMLP (1→8→1) | Class definition |
| Weight range | [0.5, 2.0] | Post-optimizer clamp |
| Monotonicity | Non-negative weights via abs() | Forward pass |
| fc1.bias | Frozen | requires_grad = False |
| fc2.bias | Learnable | Relief valve for calibration |
| Activation | Softplus | Smooth, always positive slope |

The DNN can only "turn up or down the volume" on the sidecar output — it cannot reverse the direction. Higher SFI always helps; storms always hurt. The gates modulate **how much**, not **whether**.

## Gate Initialization

For V10-equivalent behavior at initialization:

1. `gate(x) = 1.0` when `sigmoid(x) = 1/3`
2. `sigmoid(x) = 1/3` when `x = -ln(2) ≈ -0.693`
3. Set final layer **bias** of each scaler head to -0.693
4. **Zero-initialize** final layer weights so output ≈ -0.693 for all inputs

This ensures the model starts training from an exact V10 checkpoint equivalent — the gates are invisible until Phase B unfreezes them.

## V10 Weight Transfer Map

```
V10 IonisDualMono             →  V11 IonisV11Gate
─────────────────────            ──────────────────
dnn.0 (Linear 11→512)         →  trunk.0
dnn.1 (Mish)                  →  trunk.1
dnn.2 (Linear 512→256)        →  trunk.2
dnn.3 (Mish)                  →  trunk.3
dnn.4 (Linear 256→128)        →  base_head.0
dnn.5 (Mish)                  →  base_head.1
dnn.6 (Linear 128→1)          →  base_head.2
sun_sidecar.*                 →  sun_sidecar.*
storm_sidecar.*               →  storm_sidecar.*
(new)                         →  sun_scaler_head.*   (init gate=1.0)
(new)                         →  storm_scaler_head.* (init gate=1.0)
```

## Model Lineage

```
v2 → v6_monotonic → v7_lobotomy → v8_sidecar → v9_dual_mono → v10_final → v11_gate
```

## Files

| File | Purpose |
|------|---------|
| `ki7mt-ai-lab-training/scripts/ionis_v11_gate.py` | PyTorch module + self-verification |
| `ki7mt-ai-lab-docs/docs/architecture/v11_design_intent.md` | This document |
