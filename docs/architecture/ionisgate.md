# IonisGate Architecture

!!! success "Production: V20 Golden Master"
    IonisGate architecture validated with V20 production checkpoint.

    - **Pearson**: +0.4879
    - **RMSE**: 0.862σ (~5.8 dB)
    - **SFI benefit**: +0.482σ (~3.2 dB), monotonic
    - **Kp storm cost**: +3.487σ (~23.4 dB), monotonic
    - **Test Suite**: 62/62 PASS

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
| 20m mid-latitude (reference) | ≈ 1.0 | ≈ 1.0 | Baseline behavior |

## Parameter Budget

| Component | Parameters |
|-----------|-----------|
| Trunk (11→512→256) | 137,472 |
| Base head (256→128→1) | 33,025 |
| Sun scaler head (256→64→1) | 16,513 |
| Storm scaler head (256→64→1) | 16,513 |
| Sun Sidecar (1→8→1) | 25 |
| Storm Sidecar (1→8→1) | 25 |
| **Total** | **203,573** |

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
