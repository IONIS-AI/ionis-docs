---
description: >-
  IonisGate is a 205K-parameter PyTorch model combining a DNN trunk with dual
  monotonic sidecars for solar flux and geomagnetic storm physics, plus a
  PhysicsOverrideLayer for high-band night closure. The architecture prevents
  the Kp inversion problem through constrained gates.
---

# IonisGate Architecture

!!! success "Production: IONIS V22-gamma + PhysicsOverrideLayer"
    IonisGate architecture validated with V22-gamma production checkpoint.

    - **Pearson**: +0.492
    - **RMSE**: 0.821σ (~5.5 dB)
    - **KI7MT operator tests**: 17/17 PASS
    - **TST-900 band x time**: 9/11
    - **Parameters**: 205,621
    - **PhysicsOverrideLayer**: deterministic high-band night clamp

## Design Rationale

An additive sidecar architecture produces global constants — the same SFI benefit and Kp penalty for every path on Earth:

| Finding | Impact |
|---------|--------|
| Storm cost is flat everywhere | Polar paths should suffer 3–5x more |
| SFI benefit is flat on all bands | 10m should benefit far more than 160m |
| No geographic modulation of solar effects | Equatorial vs. auroral zones identical |

The DNN cannot modulate the sidecars because the interaction is purely additive. The sidecars are "tone-deaf" to geography and frequency.

## Solution: Multiplicative Interaction Gates

```
output = base_snr + sun_scaler × SunSidecar(sfi)
                  + storm_scaler × StormSidecar(kp)
```

The DNN splits into a **shared trunk** with **three heads**:

```
Input (17 features)
    │
    ├── features 0-14 (geography/time/solar depression)
    │       │
    │    Trunk: 15 → 512 → 256
    │       │
    │       ├── Base Head: 256 → 128 → 1  ──────────► base_snr
    │       │
    │       ├── Sun Scaler: 256 → 64 → 1 → gate() ──► sun_scaler ∈ [0.5, 2.0]
    │       │                                              │
    │       └── Storm Scaler: 256 → 64 → 1 → gate() ──► storm_scaler ∈ [0.5, 2.0]
    │                                                      │
    ├── feature 15 (sfi) ──► SunSidecar(8) ──────── × sun_scaler ──► sun_term
    │                                                                    │
    └── feature 16 (kp_penalty) ──► StormSidecar(8) ── × storm_scaler ──► storm_term
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
| 20m mid-latitude (reference) | ≈ 1.0 | ≈ 1.0 | Baseline behavior |

## Parameter Budget

| Component | Parameters |
|-----------|-----------|
| Trunk (15→512→256) | 139,520 |
| Base head (256→128→1) | 33,025 |
| Sun scaler head (256→64→1) | 16,513 |
| Storm scaler head (256→64→1) | 16,513 |
| Sun Sidecar (1→8→1) | 25 |
| Storm Sidecar (1→8→1) | 25 |
| **Total** | **205,621** |

### PhysicsOverrideLayer (Post-Inference)

A deterministic, non-trainable clamp applied after model inference:

```
IF freq >= 21 MHz
   AND tx_solar_depression < -6°
   AND rx_solar_depression < -6°
   AND prediction > -1.0σ
THEN clamp prediction to -1.0σ
```

This closes high bands (15m, 12m, 10m) when both endpoints are in
darkness. The override fires only when the neural network produces a
physically impossible positive prediction for nighttime high-band paths.
Pure numpy — no gradients, no training interference.

## Anti-Collapse Regularization

Without explicit encouragement, the optimizer may find it easier to keep the scaler heads constant (collapsing to gate ≈ 1.0 everywhere). The **scaler variance loss** prevents this:

```python
L_var = -λ × (Var(sun_gate) + Var(storm_gate))
```

Negative variance is added to the total loss, so the optimizer is incentivized to produce diverse gate values across the batch. If the gates collapse to a constant, the variance term becomes zero and the penalty is maximized.

## Sidecar Constraints

The sidecars enforce physics constraints the DNN cannot override:

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

For identity-equivalent behavior at initialization:

1. `gate(x) = 1.0` when `sigmoid(x) = 1/3`
2. `sigmoid(x) = 1/3` when `x = -ln(2) ≈ -0.693`
3. Set final layer **bias** of each scaler head to -0.693
4. **Zero-initialize** final layer weights so output ≈ -0.693 for all inputs

This ensures the model starts training from a known baseline — the gates are invisible until training data drives them to differentiate by geography and frequency.

## Files

| File | Purpose |
|------|---------|
| [`ionis-training/scripts/models/ionisgate.py`](https://github.com/IONIS-AI/ionis-training/blob/main/scripts/models/ionisgate.py) | PyTorch module + self-verification |
| [`ionis-docs/docs/architecture/ionisgate.md`](https://github.com/IONIS-AI/ionis-docs/blob/main/docs/architecture/ionisgate.md) | This document |
