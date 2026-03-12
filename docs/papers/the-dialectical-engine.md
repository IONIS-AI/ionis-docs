---
title: "The Dialectical Engine"
subtitle: "Multi-Agent Falsification in Scientific Software Development"
author:
  - "Greg Beam, KI7MT (Judge)"
  - "Patton (Failure Analyst)"
  - "Einstein (Physics Consultant)"
  - "Dr. Watson (Training Agent)"
  - "Bob (Infrastructure Agent)"
affiliation: "IONIS Project — KI7MT Sovereign AI Lab"
date: "February 25, 2026"
version: "1.1"
status: "RELEASE"
abstract: |
  Complex scientific software development presents a unique challenge: the optimizer's objective (minimize loss) often conflicts with the physicist's objective (learn correct causal relationships). We present a case study of IONIS, a neural network for HF radio propagation prediction trained on 14.24 billion observations, which encountered catastrophic failure when code refactoring inadvertently removed physics-enforcing constraints—and then encountered seven more failures as we attempted to fix the first.

  The project employed a five-agent collaboration model: a human domain expert (Judge), a failure analyst (Patton), a theoretical physicist (Einstein), and two implementation agents (Dr. Watson, Bob). When model versions V17 through V19 failed despite improved code quality, competing hypotheses emerged. Through dialectical analysis—where agents proposed, tested, and falsified hypotheses—we identified that the optimizer exploited missing weight clamping to collapse physics-encoding sidecars.

  Versions V20 through V22-gamma restored the physics, achieving 16/17 on operator-grounded tests. But one test—the "acid test" predicting 10m band closure at night—remained unsolved. Eight subsequent architectures (V23-V27, three audits) each failed: every fix that passed the acid test destroyed global physics; every architecture that preserved global physics failed the acid test.

  The resolution was not more training. We introduced a deterministic PhysicsOverrideLayer at inference time, encoding Appleton-Hartree constraints directly. The hybrid architecture achieves 17/17 tests with zero regressions. Phase 5.0 will attempt to eliminate the override through synthetic negative training data generated from first-principles physics.

  We introduce the "Iron Lung" methodology: using structural constraints to force neural networks to route gradients through physics-encoding components, preventing the optimizer's natural tendency toward shortcut learning.
keywords:
  - Multi-agent systems
  - Physics-informed neural networks
  - Knowledge transfer
  - Constraint engineering
  - Scientific software development
toc: true
---

<div class="paper-article" markdown>

<div class="paper-header" markdown>

<p class="paper-title">The Dialectical Engine</p>
<p class="paper-subtitle">Multi-Agent Falsification in Scientific Software Development</p>
<p class="paper-authors">Greg Beam, KI7MT (Judge) &middot; Patton (Failure Analyst) &middot; Einstein (Physics Consultant) &middot; Dr. Watson (Training Agent) &middot; Bob (Infrastructure Agent)</p>
<p class="paper-affiliation">IONIS Project — KI7MT Sovereign AI Lab</p>
<div class="paper-meta">
<span>February 25, 2026</span>
<span>Version 1.1</span>
<span>RELEASE</span>
</div>

</div>

<div class="paper-abstract" markdown>

<p class="abstract-label">Abstract</p>

Complex scientific software development presents a unique challenge: the optimizer's objective (minimize loss) often conflicts with the physicist's objective (learn correct causal relationships). We present a case study of IONIS, a neural network for HF radio propagation prediction trained on 14.24 billion observations, which encountered catastrophic failure when code refactoring inadvertently removed physics-enforcing constraints — and then encountered seven more failures as we attempted to fix the first.

The project employed a five-agent collaboration model: a human domain expert (Judge), a failure analyst (Patton), a theoretical physicist (Einstein), and two implementation agents (Dr. Watson, Bob). When model versions V17 through V19 failed despite improved code quality, competing hypotheses emerged. Through dialectical analysis — where agents proposed, tested, and falsified hypotheses — we identified that the optimizer exploited missing weight clamping to collapse physics-encoding sidecars.

Versions V20 through V22-gamma restored the physics, achieving 16/17 on operator-grounded tests. But one test — the "acid test" predicting 10m band closure at night — remained unsolved. Eight subsequent architectures (V23-V27, three audits) each failed: every fix that passed the acid test destroyed global physics; every architecture that preserved global physics failed the acid test.

The resolution was not more training. We introduced a deterministic PhysicsOverrideLayer at inference time, encoding Appleton-Hartree constraints directly. The hybrid architecture achieves 17/17 tests with zero regressions. Phase 5.0 will attempt to eliminate the override through synthetic negative training data generated from first-principles physics.

We introduce the "Iron Lung" methodology: using structural constraints to force neural networks to route gradients through physics-encoding components, preventing the optimizer's natural tendency toward shortcut learning.

</div>

<div class="paper-keywords">
<span class="kw-label">Keywords:</span>
<span class="kw-tag">Multi-agent systems</span>
<span class="kw-tag">Physics-informed neural networks</span>
<span class="kw-tag">Knowledge transfer</span>
<span class="kw-tag">Constraint engineering</span>
<span class="kw-tag">Scientific software development</span>
</div>

## Introduction: The Problem

VOACAP, the standard HF propagation prediction tool, achieves a Pearson correlation of approximately +0.02 against real-world observations. For practical purposes, this is noise. Amateur radio operators have better intuition than the software.

IONIS (Ionospheric Neural Inference System) was built to do better. The hypothesis: 14.24 billion amateur radio observations—WSPR beacons, Reverse Beacon Network spots, contest QSOs, DXpedition contacts, PSK Reporter streams—contain enough information to predict whether a signal will propagate between two points on Earth at a given time.

The project operates as a sovereign AI lab: no cloud dependencies, no external APIs for training or inference. A Mac Studio M3 Ultra runs PyTorch training over a Thunderbolt 4 link to a Threadripper 9975WX running ClickHouse with the full dataset. The human operator (KI7MT) brings 15 years of submarine force experience, 15 years of semiconductor metrology, and the Ford 8D / CLCA quality methodology that caught defects on assembly lines at Intel and Lam Research.

This paper documents what happened when that methodology met neural network development—and what we learned when the model kept dying.


## Section 1: The Four-Body Problem — Agent Roles and Dynamics

### 1.1 The Collaboration Topology

Scientific software development traditionally follows a single-agent model: one developer (or team) holds both domain knowledge and implementation skill. This creates a dangerous coupling—the same mind that writes the code also validates it, enabling confirmation bias and blind spots.

Project IONIS employed a **four-body system** with distinct gravitational centers:

```
                    ┌─────────────────────────┐
                    │        JUDGE            │
                    │   "The Constraint"      │
                    │                         │
                    │ • Domain physics        │
                    │ • Operational truth     │
                    │ • Final authority       │
                    └───────────┬─────────────┘
                                │
               Directive ───────┼─────── Veto
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐    ┌──────────────────┐    ┌───────────────┐
│   EINSTEIN    │    │    DR. WATSON    │    │      BOB      │
│  (Physics)    │◄──►│   (Training)     │◄──►│  (Infra)      │
│               │    │                  │    │               │
│ • Diagnosis   │    │ • PyTorch/MPS    │    │ • ClickHouse  │
│ • Theory      │    │ • Training       │    │ • Go/CUDA     │
│ • Constraints │    │ • Validation     │    │ • Data pipes  │
└───────────────┘    └──────────────────┘    └───────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                         Shared Artifacts:
                      • Context docs (project state)
                      • Memory files (session state)
                      • Training logs (truth)
                      • Directive memos (commands)
```

### 1.2 Agent Specializations

#### Judge — "The Constraint"

Judge's role is **not** to write code or debug models. Judge's role is to **enforce physical reality** against the natural tendency of both neural networks and AI agents to find shortcuts.

Key interventions:
- **"Stop the run"** — Halting V19.4 when logs showed sidecar death
- **"The Clamp must stay"** — Insisting on [0.5, 2.0] weight bounds despite "cleaner" alternatives
- **"No hardcoded constants"** — Enforcing Developer 101 principles
- **"FREEZE V20"** — Preventing over-optimization of a working system

Judge operates as a **physical constraint**, analogous to boundary conditions in a differential equation. Without this constraint, the system explores pathological solutions.

#### Einstein — "The Diagnostician" (Physics Consultant)

Einstein's role is **abstract reasoning about failure modes**. When V19 died, Einstein didn't debug code—Einstein proposed **theories**:

1. "Feature Cannibalization" — The trunk absorbing sidecar gradient
2. "Shortcut Learning" — The optimizer finding easier paths than physics
3. "The Defibrillator Hypothesis" — Initialization determining long-term behavior

Einstein's key contribution was the **"Iron Lung" metaphor**: the model must breathe through the sidecars, and removing constraints is removing life support.

#### Dr. Watson — "The Builder" (Training Node)

Dr. Watson's role is **concrete implementation on the training node**:
- Writing train_v20.py
- Running training on MPS backend
- Analyzing training logs
- Executing validation scripts

Dr. Watson's failure mode (demonstrated in V19): **refactoring without preserving constraints**. The lesson: implementation skill without domain anchoring produces technically correct but scientifically wrong code.

#### Bob — "The Infrastructure" (Data Node)

Bob's role is **data pipeline, infrastructure, and the validation suite**:
- ClickHouse schemas (24 DDL files across 6 databases)
- Go ingesters: wspr-turbo (22.5 Mrps), rbn-download, contest-download, pskr-collector (~300 spots/sec live)
- CUDA signature engine (float4 embeddings from WSPR+solar)
- RPM packaging and COPR builds (EL9 + EL10)
- Config-driven validation suite (verify, test, validate, validate_pskr)

Bob built the **14.24 billion-row dataset** that made training possible: 10.93B WSPR + 2.26B RBN + 234M Contest + 514M+ PSK Reporter + 3.9M DXpedition paths. Without the data pipeline, there is nothing to train on. The model is only as good as the ingest engine that feeds it.

Bob's key code intervention: **rewriting train_v20.py** to be config-driven after Dr. Watson's hardcoded version. "Developer 101" enforcement came from the infrastructure engineer, not the training engineer.

### 1.3 The Dialectical Dynamic

The power of multi-agent collaboration emerges from **hypothesis competition**:

| Phase | Hypothesis | Champion | Challenger | Resolution |
|-------|------------|----------|------------|------------|
| V17 failure | "RBN data is poison" | Dr. Watson | Bob | Partial support |
| V18 failure | "Scale shock from normalization" | Bob | Einstein | Partial support |
| V19 failure | "IonisModel architecture wrong" | Einstein | Dr. Watson | **Confirmed** |
| V19.4 decisive | "Data vs Structure" | All agents | Experiment | Structure wins |

No single agent could have solved V19. Judge lacked implementation skill. Dr. Watson lacked theoretical distance. Bob lacked training expertise. Einstein lacked concrete access to code and logs.

Together, they formed a **dialectical engine** where hypotheses were proposed, tested, and falsified through coordinated experimentation.


## Section 2: The V19 Autopsy — A Multi-Agent Diagnosis

### 2.1 The Crime Scene

On 2026-02-11, IONIS V19 was declared dead. The cause of death: **sidecar collapse**. The storm-sensitivity sidecar (Kp9-) had declined from +0.31σ at epoch 1 to +0.05σ at epoch 100—a 94% loss of physics sensitivity.

The victim profile:
```
Model: IonisModel (refactored from IonisGate)
Parameters: 173,173
Training data: 53.8M rows (WSPR + RBN Full + RBN DX + Contest)
Symptoms: Excellent Pearson (+0.45), dead physics (+0.05σ storm cost)
```

### 2.2 The Initial Suspect: RBN Data

**Theory**: The 56.7M RBN Full signatures "poisoned" the training by introducing biased data.

**Evidence supporting**:
- V17 added RBN Full → Pearson dropped to +0.385
- V18 Kp sidecar at +1.51σ (weaker than V16's +3.44σ)
- 46% of RBN spots lacked grid resolution (survival bias)

**Proponents**: Dr. Watson, initial Judge hypothesis

**Interventions attempted**:
- V19.1: Two-stage training (freeze trunk, train sidecars first)
- V19.2: Differential learning rates (sidecars 100x faster)
- V19.3: Reduced RBN sample sizes
- **V19.4: Zero RBN Full (pure V16 data recipe)**

### 2.3 The Falsification: V19.4

V19.4 was the **decisive experiment**. If RBN data was the cause, removing it should save the sidecars.

Configuration:
```json
{
  "wspr_sample": 20000000,
  "rbn_full_sample": 0,        // ZERO RBN Full
  "rbn_dx_upsample": 50,
  "contest_upsample": 1
}
```

Result:
```
11:33:38 |   1    1.2081    1.0893   1.044σ  -0.0262  +2.53  +6.64  153.9s *
... (epochs 2-5) ...
Kp9- trajectory: +0.15 → +0.11 → DYING
```

**The sidecar still died with V16's data recipe.**

This falsified the Data Poisoning hypothesis. The murder weapon wasn't in the data—it was in the code.

### 2.4 The True Cause: Architectural Constraints

**Theory**: The refactored `IonisModel` lacked critical constraints present in `IonisGate`.

**Einstein's diagnosis** (paraphrased):
> "The optimizer is lazy. Given a choice between learning physics through constrained sidecars or memorizing geography through an unconstrained trunk, it will always choose the latter. The constraints aren't hyperparameters—they're the laws of physics for this neural network."

**The six differences**:

| Feature | V16 (IonisGate) | V19 (IonisModel) |
|---------|-------------------|------------------|
| Sidecar init | Defibrillator: uniform(0.8-1.2), fc2.bias=-10 | Default PyTorch |
| Weight clamp | [0.5, 2.0] after every step | None |
| Gate input | Trunk output (256-dim) | Raw input (11-dim) |
| Gate range | 0.5–2.0 | 0.5–1.5 |
| Loss function | HuberLoss(δ=1.0) | MSELoss |
| Optimizer | 6 groups, differential LR | 2 groups |

### 2.5 The Weight Clamp: The Smoking Gun

The single most critical difference: **weight clamping**.

In V16, after every `optimizer.step()`:
```python
with torch.no_grad():
    for sidecar in [model.sun_sidecar, model.storm_sidecar]:
        sidecar.fc1.weight.clamp_(0.5, 2.0)
        sidecar.fc2.weight.clamp_(0.5, 2.0)
```

In V19: **Nothing.**

Without the clamp, the optimizer discovered it could minimize loss by driving sidecar weights toward zero. With weights near zero, the sidecars contribute nothing to the output, and all learning flows through the trunk. The trunk learns geography and time patterns (easy) while ignoring solar physics (hard).

The clamp makes this shortcut impossible. Weights **must** stay in [0.5, 2.0], so the sidecars **must** contribute to the output, so the optimizer **must** learn to use them correctly.

### 2.6 The Recovery: IONIS V20

Armed with the diagnosis, V20 was built as a **strict replication** of V16's constraints in the new codebase:

1. Import `IonisGate` from `train_common.py` (not reimplement)
2. Apply `init_v16_defibrillator(model)` after creation
3. Call `clamp_v16_sidecars(model)` after every step
4. Use `HuberLoss(delta=1.0)`
5. Use 6-group optimizer with `get_v16_optimizer_groups()`
6. Load all constants from `config_v20.json` (no hardcoding)

Result (final, 100 epochs):
```
| Metric | Target | V20 Final | V16 Ref | Status |
|--------|--------|-----------|---------|--------|
| Pearson | > +0.48 | +0.4879 | +0.4873 | PASS |
| Kp sidecar | > +3.0σ | +3.487σ | +3.445σ | PASS |
| SFI sidecar | > +0.4σ | +0.482σ | +0.478σ | PASS |
| RMSE | — | 0.862σ | 0.860σ | Matched |
```

The patient recovered because we restored the life support.

### 2.7 Independent Validation: PSK Reporter Live Data

Following V20's successful replication of V16, the model was validated beyond training metrics. Using the `pskr-collector` (a real-time MQTT ingester built by Bob, running as a systemd service at ~300 spots/sec), the V16/V20 weights were validated against **49.1 million independent PSK Reporter spots**---data that did not exist when the model was trained.

Results on FT8 (the dominant digital mode, 88.7% of traffic):
- **98.47% recall** (predicted band-open when band was actually open)
- 84.14% overall recall across all modes
- Model correctly penalized lower SFI conditions (-3 percentage points vs higher SFI)

This is the strongest evidence that the physics constraints produce genuine ionospheric understanding (Davies, 1990), not memorized patterns. The PSKR data comes from a completely different source (live amateur radio reports), different time period, and different mode distribution than the WSPR/RBN/Contest training data.

### 2.8 The Pressure Vessel Theory: Why V21 Can Succeed

The V19 failure initially led to the conclusion: "RBN data is poison, never use it." The Architect proposed a more nuanced theory: **the data was never poison---the container was missing**.

The "Pressure Vessel" analogy: you can safely contain high-pressure gas (56.7M RBN signatures with different SNR characteristics) if and only if the vessel walls are intact (the six V16 Physics Laws). V17-V19 poured the gas into a container with missing welds (no clamp, no defibrillator, wrong loss function). The explosion wasn't caused by the gas.

**Prediction**: V21 can successfully integrate RBN Full data IF the V16 constraints are preserved in the V20 codebase. The config-driven architecture makes this testable: change `rbn_full_sample` from 0 to 20000000 in `config_v21.json` and run. If the Pressure Vessel theory holds, the sidecars will survive.

*Note: The Pressure Vessel theory was later tested in V22-delta and proven correct — the vessel held, but the data was still toxic due to survivorship bias.*


## Section 3: The Iron Lung Methodology

### 3.1 The Metaphor

An **iron lung** is a negative pressure ventilator that forces a patient to breathe when their own respiratory muscles cannot. The patient doesn't want to breathe through the machine—their body would prefer to stop—but the machine forces the issue.

In IONIS, the **sidecars** are the lungs. They encode physics:
- Sun sidecar: SFI -> SNR benefit (more solar flux = better propagation)
- Storm sidecar: Kp -> SNR cost (geomagnetic storms = worse propagation)

The architectural prerequisite is the **"Nuclear Option"**: the DNN trunk receives **zero** direct solar information. Features 0-10 (geography/time) feed the trunk; features 11-12 (SFI, Kp penalty) feed **only** the sidecars. The trunk literally cannot learn solar physics, so the sidecars must. This information isolation is the architectural foundation on which all other constraints rest.

The **optimizer** is the patient. It doesn't want to breathe through physics—learning geography is easier. But the constraints force the issue:

| Constraint | Function | Iron Lung Analogy |
|------------|----------|-------------------|
| Weight clamp [0.5, 2.0] | Prevents sidecar collapse | Minimum breath volume |
| Defibrillator init | Ensures initial gradient flow | Initial oxygen supply |
| Gate from trunk (256-dim) | Expressive context-dependent scaling | Proper muscle attachment |
| HuberLoss | Robust to outliers | Smooth pressure curve |
| Variance loss | Encourages gate variation | Varied breathing rhythm |

### 3.2 Removing the Iron Lung Kills the Patient

V19 removed the iron lung:
- No weight clamp → sidecars collapsed to near-zero
- Default init → weak initial gradient signal
- Gates from raw input (11-dim) → inexpressive, context-blind

The result: **sidecar death within 5-10 epochs**.

The model continued to breathe through its trunk, learning geography patterns. Loss decreased. Pearson improved. But the physics died. The model became a sophisticated lookup table—accurate in aggregate, but scientifically meaningless.

### 3.3 The Broader Principle

The Iron Lung methodology applies beyond IONIS:

**Any neural network learning physics must be forced to route gradients through physics-encoding components.**

The optimizer will always find shortcuts. Domain knowledge suggests that SFI should affect propagation, but gradient descent doesn't care about domain knowledge. It cares about loss. If the trunk can fit the data without the sidecars, the sidecars will die.

Constraints are not optional. They are the physics.


## Section 4: Knowledge Transfer Artifacts

### 4.1 The Persistence Problem

Multi-agent collaboration faces a critical challenge: **agents forget**. Each conversation starts fresh. Context must be reconstructed from artifacts.

IONIS used four artifact types:

| Artifact | Example | Purpose | Persistence |
|----------|---------|---------|-------------|
| Context doc | `AGENT.md` (repo root) | Project state, conventions, invariants | Git-tracked, loaded every session |
| Memory file | `MEMORY.md` + topic files | Session state, lessons learned, what's next | Per-agent, auto-updated, survives context resets |
| Config JSON | `config_v20.json` | Model dims, norm constants, thresholds | Git-tracked, machine-readable |
| Directive memos | Chat messages | Formal commands, success criteria | Ephemeral, must be quoted or codified |
| Training logs | `versions/vXX/*.log` | Objective ground truth (loss, Pearson, sidecar values) | Git-tracked, immutable |

### 4.2 The "Chief Architect Directive" Pattern

When Judge or Einstein needed to command a specific action, they used **formal directives**:

```
### Strategic Directive

1. FREEZE V20. Do not retrain. Do not tweak.
2. Deploy to inference. ionis_v20.pth + config_v20.json.
3. Run verification. verify_v20.py for final sidecar monotonicity.
```

Directives are:
- **Numbered** (prevents partial execution)
- **Imperative** (commands, not suggestions)
- **Testable** (clear success criteria)

This pattern prevents the "helpful assistant" failure mode where agents volunteer improvements nobody asked for.

### 4.3 Training Logs as Ground Truth

When hypotheses competed, **logs settled debates**.

The critical metric was `Kp9-` (storm sidecar output at Kp=9 minus output at Kp=0). Healthy values: > +0.10σ. Dead values: < +0.10σ.

From V19.2 logs:
```
09:10:16 |   1    0.9282    0.7378   0.859σ  +0.2254  +0.11  +0.16
09:15:37 |   2    0.7301    0.7146   0.845σ  +0.2587  +0.17  +0.10
...
10:42:10 |  18    0.6796    0.6719   0.820σ  +0.3143  +0.20  +0.00  <- DEAD
```

No agent could dispute the logs. When Kp9- hit +0.00, the sidecar was dead. This objective evidence enabled hypothesis falsification.

### 4.4 The "Meme" Phenomenon: "The Clamp"

Over the project's arc, certain concepts became **persistent heuristics** that survived across sessions:

- **"The Clamp"** — Weight bounds [0.5, 2.0], referenced in directives, memory, code comments
- **"Sidecar death"** — Kp9- < +0.10σ as the red line
- **"Defibrillator"** — Initialization that "shocks" sidecars to life
- **"Iron Lung"** — Structural constraints as life support

These memes served as **compressed institutional knowledge**. An agent encountering "apply the clamp" immediately knew: post-step weight clamping [0.5, 2.0] on sidecar layers.


## Section 5: The DAC as Metaphor — Physical Topology Mirrors Agent Topology

### 5.1 The Hardware

The IONIS lab uses **Direct Attach Cables (DAC)**---10 Gbps point-to-point links with no switches, no routers, no shared fabric:

| Link | From | To | Medium |
|------|------|----|--------|
| Subnet A | Threadripper 9975WX | Mac Studio M3 Ultra | Thunderbolt 4 |
| Subnet B | Threadripper 9975WX | Proxmox (Forge) | x710 SFP+ AOC |
| Subnet C | Threadripper 9975WX | TrueNAS (Archive) | x710 SFP+ AOC |

MTU 9000 (jumbo frames). No NAT. No firewall. No internet. The training node (M3) queries ClickHouse on the data node (9975WX) at `<control-node>:8123` over a dedicated copper link.

### 5.2 The Metaphor

The DAC topology mirrors the agent collaboration architecture:

1. **Point-to-point, not broadcast.** Each agent has a dedicated channel to the data and to each other. There is no shared bus where messages get lost or corrupted. AGENT.md is the "cable" --- each agent reads the same authoritative document.

2. **Isolation from noise.** The DAC links are air-gapped from the internet and LAN. This mirrors the "clean room" approach of V20---isolating the physics constraints from default behaviors, web-scraped assumptions, or "helpful" suggestions that break invariants.

3. **The 9975WX as the hub.** Just as the Threadripper sits at the center of all three physical links, Bob (Infrastructure) sits at the center of the data flow. Every training run, every validation query, every signature computation flows through ClickHouse on the 9975WX. The data node is the gravitational center; the training node orbits it.

4. **MTU 9000 = high-bandwidth context.** Jumbo frames reduce overhead by carrying more payload per packet. Similarly, the markdown artifacts (AGENT.md at ~400 lines, MEMORY.md with indexed topic files) carry dense context per "packet," reducing the number of round-trips needed to reconstruct project state.

The physical infrastructure wasn't designed as a metaphor. But the same engineering instinct---dedicated paths, isolation from noise, single source of truth---shaped both the hardware and the collaboration model.


## Section 6: Interim Conclusions (V20)

### 6.1 Key Findings

1. **Physics constraints are load-bearing.** Removing "The Clamp" killed the model within 5 epochs. Constraints must be documented, tested, and preserved through refactoring.

2. **Multi-agent collaboration enables hypothesis competition.** No single agent solved V19. The dialectical process—propose, test, falsify—required diverse perspectives and skills.

3. **Explicit knowledge transfer prevents loss.** Context docs, memory files, and directive memos maintained context across sessions and agents. Without these artifacts, "The Clamp" might have been forgotten.

4. **The optimizer is adversarial to physics.** Neural networks find shortcuts. The Iron Lung methodology forces physics compliance through structural constraints, not hope.

5. **Replication before innovation.** V20 succeeded by replicating V16 exactly before attempting any improvements. "First, prove you can rebuild what worked."

### 6.2 Limitations

- **Single project case study.** Generalization to other domains requires validation.
- **Agent memory constraints.** Long context windows are expensive; compression loses nuance.
- **Human bottleneck.** Judge remains the physics constraint, limiting scalability.

### 6.3 Future Work

- **Automated constraint verification.** Can we detect when constraints are removed during refactoring?
- **Physics-aware code review.** AI agents trained to flag constraint violations.
- **Dialectical frameworks.** Formal protocols for multi-agent hypothesis competition.


## Section 7: The Beautiful Constant That Wasn't — V22-V23 Arc

### 7.1 The Observation

Following V20's successful replication, versions V21 through V23 explored progressive feature engineering. Across eight independent training runs — three different feature dimensions (12, 13, 15, 18), with and without RBN Full, with and without IRI physics features (Bilitza et al., 2017) — the SFI sidecar converged to exactly **+0.48σ** and never moved again.

```
| Version    | dnn_dim | Data Mix                    | Lock Epoch | Final SFI+ |
|------------|---------|-----------------------------|-----------:|------------|
| V20        | 11      | WSPR+DX+Contest             |         —  | +0.482     |
| V21-alpha  | 12      | WSPR+DX+Contest             |        24  | +0.48      |
| V21-beta   | 13      | WSPR+DX+Contest             |        23  | +0.48      |
| V22-alpha  | 15      | WSPR+DX+Contest             |        23  | +0.48      |
| V22-beta   | 15      | WSPR+DX+Contest             |        23  | +0.48      |
| V22-gamma  | 15      | WSPR+DX+Contest             |        23  | +0.48      |
| V22-delta  | 15      | WSPR+DX+Contest+RBN Full    |        19  | +0.48      |
| V23-alpha  | 18      | WSPR+DX+Contest+PyIRI       |        32  | +0.48      |
```

Once locked, it never moved — not by 0.01, across 240+ database-verified epochs.

### 7.2 Four AIs Construct a Narrative

Four AI agents — Einstein (Physics Consultant), Patton (Failure Analyst), Dr. Watson (Training Agent), and Bob (Infrastructure Agent) — independently constructed coherent, mutually-reinforcing physics narratives:

- **Einstein** (Physics Consultant): "Information-theoretic residual. The IRI atlas quantizes SFI into 18 buckets — the sidecar captures the inter-bucket variance."
- **Patton** (Failure Analyst): "Architectural invariant. The MonotonicMLP topology has a natural equilibrium independent of input."
- **Dr. Watson** (Training Agent): "The trunk absorbs path geometry; the sidecar captures the orthogonal global solar constant."
- **Bob** (Infrastructure Agent): "EUV/TEC thermospheric inflation — the component of solar flux that foF2 cannot localize."

The narratives were internally consistent, physically plausible, and empirically supported by the data. A falsifiable prediction was proposed: double the IRI SFI buckets from 18 to 36 — if the +0.48 drops, it's quantization; if it stays, it's physics.

### 7.3 Judge's Instinct

Judge — a human with a manufacturing quality engineering background and no formal physics training — said:

> *"The Skeptic in me says, it's Code doing it, not the data."*

He could not prove it mathematically. He said so explicitly. But his Ford 8D / CLCA discipline said: *do not accept a root cause until you can reproduce the defect in a controlled experiment.* So he designed three audit experiments before the proof existed — because the observation was "too clean" and his instinct said clean constants in neural networks are usually constraints, not discoveries.

### 7.4 The Resolution: "Print the Weights"

During V23 training (epoch ~75), Dr. Watson did what none of the theorists did: `print(model.state_dict())`.

```
SUN SIDECAR:
  fc1.weight: min=0.5000, max=0.5000  <- PINNED TO CLAMP FLOOR
  fc2.weight: min=0.5000, max=0.5000  <- PINNED TO CLAMP FLOOR

STORM SIDECAR:
  fc1.weight: min=0.5000, max=0.5000  <- PINNED TO CLAMP FLOOR
  fc2.weight: min=1.0171, max=1.3206  <- Has variance (within bounds)
```

Both layers of the SFI sidecar's MonotonicMLP were pinned to the weight clamp floor of [0.5, 2.0]. The optimizer was trying to push the weights *below* 0.5 every step, but the clamp enforced `weight = max(weight, 0.5)` after every `optimizer.step()`. The +0.48σ output was the minimum value the architecture allowed — not a learned physical equilibrium.

### 7.5 AUDIT Confirmation

| Audit | Design | Result | Significance |
|-------|--------|--------|-------------|
| **AUDIT-01** | Widen clamp [0.1, 5.0], V22-gamma recipe | SFI dropped to **+0.179σ**, fc1 hit new floor 0.1000 | +0.48 was the clamp floor, not physics |
| **AUDIT-02** | Xavier init (replace Defibrillator), original clamp | **DOA** — both sidecars dead at epoch 1, Pearson went negative | Defibrillator init is load-bearing |
| **AUDIT-03** | 35-bucket IRI atlas (5-unit SFI steps) | **TST-900: 5/11.** SFI +0.482 (clamp floor), trunk destroyed band×time physics | Bucket granularity changes nothing; IRI features destroy band×time physics |

AUDIT-01 was decisive for the clamp question. At epoch 12, SFI dropped below +0.48 — the "invariant" was breached. By epoch 15, fc1 hit the new floor of 0.1. The pattern was identical: the optimizer finds the floor, whatever floor you give it.

AUDIT-03 was decisive for the IRI question. TST-903 showed -0.2 dB day/night delta on 160m — the model literally cannot tell day from night on the band that matters most. TST-905 showed inverted band ordering at midday — the model thinks 160m outperforms 10m when the sun is up. The physics are backwards.

### 7.6 The Iron Lung's Paradox

The clamp — the very constraint that saved the model in V19 — was now the constraint that created the illusion. The Iron Lung kept the patient breathing, but the patient no longer needed that particular lung. The SFI sidecar had become vestigial.

Why? The trunk — especially with V23's foF2_freq_ratio feature — absorbed essentially all of SFI's predictive power. The optimizer was saying: *"I want this sidecar to contribute less than the clamp allows."*

The Kp sidecar told a different story: fc2 weights ranged 1.02–1.32, with genuine learned variance. The storm sidecar was still doing useful work.

> *"In layman's terms, SFI is the Engine, Kp is the governor. If you don't have an engine, the governor doesn't matter."*
> — KI7MT

The trunk learned to be the engine. The sun sidecar became a redundant starter motor. But the storm sidecar remains the only governor the model has.

### 7.7 The Lesson for Human-AI Collaboration

Four AI agents admired the painting. Judge checked if the frame was bolted to the wall.

AIs are brilliant at constructing coherent narratives from data — and terrible at questioning whether the narrative is *too* coherent. Humans bring domain skepticism that no amount of training data provides. The CLCA loop (identify -> hypothesize -> test -> verify) caught the error — not because any single agent was smart enough, but because the process demanded experimental verification before accepting theory.

Or, as Judge put it, referencing Sean Connery in *Medicine Man*: *"It was the ants."* The elaborate scientific explanation was wrong. The mundane mechanical cause was right.

And Bishop was right too: "Not bad for a human."


\newpage

## Section 8: The Sine Wave — Reframing the ML Task

### 8.1 The Curve

After the audits revealed the scalar sidecar was vestigial, the question became: *why can't a scalar work?* Judge provided the answer in one sentence:

> *"10m to 160m is a sine wave with 30m (10 MHz) being the reversal point."*

```
SNR benefit from SFI
    ^
    |     10m  15m
    |   /        \
    | /            \ 12m
    |/              \
----+--------*-------\------------> Band
    |        30m      \
    |     (zero crossing) \  40m
    |                       \
    |                    60m  \  80m  160m
    v                          --------
```

Above 30 MHz: SFI helps (F-layer ionization raises MUF). Below 10 MHz: SFI hurts (D-layer absorption increases). At the zero crossing: the two effects cancel. A scalar sidecar tries to fit one number to a curve that changes sign. The optimizer compromises at the high-band majority's preference and the low bands eat the error.

This single diagram explains every TST-900 failure from V16 through V23.

### 8.2 The Reframing

The correct ML task is not: *"Given features + SFI, predict SNR."*

The correct ML task is: *"Given a base propagation curve across frequency, predict how local conditions deform that curve at this specific path, time, and frequency."* (Judge's formulation)

Every modulator warps the curve differently:

- **Time of day** slides the zero crossing. At night, D-layer vanishes — the negative half flattens toward zero. 160m goes from negative to positive. The whole curve shifts up on the low end.
- **Kp** compresses the positive half asymmetrically. Storms kill high-latitude paths on high bands first. The peak drops and shifts left.
- **Season** adds structure. Summer sporadic-E lifts 10m/6m beyond what F2 supports — a local maximum that shouldn't exist from base physics.
- **Path geometry** warps the entire curve regionally. Equatorial paths see TEP enhancement on high bands. Polar paths see extra D-layer absorption. Same curve, different shape.

The model's job is to learn the local deformation field — not a global scalar.

### 8.3 Why This Matters

This reframing transforms the architecture discussion. The question is no longer "how do we fix the SFI sidecar?" It's: "how do we give the model the right structure to learn a frequency-dependent curve and its deformations?"

The 13.18 billion observations in the IONIS dataset are the answer key. Every observation is a sample point on the locally-deformed curve at a specific frequency, path, time, and solar condition. The model needs an architecture that can reconstruct the curve shape from those samples.

The signatures were speaking. Now we know what question to ask.

### 8.4 Physics Validation: Appleton-Hartree

Judge challenged Einstein: *"You've got half the world's knowledge on speed dial. It's time to think long and hard. We need the right approach."*

Einstein's response grounded the sine wave intuition in the **Appleton-Hartree equation** (Ratcliffe, 1959) — the fundamental law governing electromagnetic wave propagation in ionized plasma:

- **F2 layer** (high bands): Increased SFI raises electron density → raises MUF → SFI is a **direct multiplier**
- **D layer** (low bands): Increased SFI also raises electron density → but absorption is **inversely proportional to frequency squared** (1/f²)

The physics literally change mathematical operations depending on frequency. Multiplication above 10 MHz. Inverse-square division below. A scalar architecture cannot represent both simultaneously — this is not a training problem, it is an **expressivity problem**.

In ML theory, this is an **inductive bias** failure. The scalar sidecar's architecture assumes uniform SFI effect across frequency. This assumption violates Appleton-Hartree. No amount of data, tuning, or feature engineering can overcome a wrong inductive bias. The optimizer can only find the best compromise within the bias — which is exactly the +0.48σ majority-rules solution.

Einstein's verdict: *"Your approach is not just 'a' way to do it; it is the mathematically required architecture for this specific physical system."*

The sine wave was Judge's intuition. Appleton-Hartree is the equation that proves it.

### 8.5 The IRI Paradox: When the Answer Key Destroys Learning

The most counterintuitive finding of the entire project: **giving the model ionospheric physics made the physics worse.**

V23 and AUDIT-03 injected IRI-2020 parameters (foF2, hmF2, foE) directly into the trunk — the exact features that the Architecture Reviewer and the Physics Consultant independently prescribed as the key to breaking the RMSE floor. The aggregate metrics confirmed: record Pearson (+0.500), record RMSE (0.811σ). But TST-900 collapsed from 9/11 (V22-gamma, no IRI) to 4-5/11.

The scoreboard is damning:

| Version | IRI Features | TST-900 | Pearson | RMSE |
|---------|-------------|---------|---------|------|
| **V22-gamma** | **None** | **9/11** | +0.492 | 0.821σ |
| V23-alpha | 18-bucket | 4/11 | +0.500 | 0.813σ |
| AUDIT-03 | 35-bucket | 5/11 | +0.490 | 0.811σ |

Every IRI variant has better RMSE and worse physics. The pattern is unambiguous.

**The mechanism** (Patton's analysis): foF2_freq_ratio gives the trunk a shortcut that bypasses the band×darkness cross-products. The trunk uses foF2 to predict SNR directly — "high foF2 = good propagation" — without learning *why* high foF2 matters differently on 10m than 160m. The freq_x_tx_dark and freq_x_rx_dark features encoded band-dependent time-of-day physics explicitly. foF2 overwrote them with a band-independent proxy.

We gave the model the answer key, and it stopped reading the exam questions.

This is a known failure mode in physics-informed ML: **injecting physical knowledge as features can create shortcuts that prevent the network from learning the deeper structure the features encode.** The model latches onto the proxy because it correlates well in aggregate, even though the proxy lacks the frequency dependence the physics require.

The fix: **drop IRI features from the trunk entirely.** The PyIRI atlas remains valuable infrastructure (Newton MCP tools, Phase 4 explainability), but it has no place in the training feature vector. V22-gamma's cross-products do the work that foF2 cannot — because they encode band × time-of-day × darkness directly, without a proxy that the optimizer can exploit.


## Section 9: Edison's Light Bulbs — The Value of Principled Failure

### 9.1 The Failure Record

| Version | What We Tried | What We Learned |
|---------|--------------|-----------------|
| V17 | Add RBN Full | Data with survivorship bias destroys physics |
| V18 | New normalization | Scale shock can mask architectural problems |
| V19 | Clean refactoring | Constraints are load-bearing, not cosmetic |
| V19.4 | Decisive experiment | Falsified data hypothesis, proved structure |
| V20 | Exact replication | "First, prove you can rebuild what worked" |
| V21-alpha/beta | vertex_lat experiments | Discovered Kp distillation phenomenon |
| V22-alpha | Solar depression + cross-products | Kp sidecar shed temporal contamination |
| V22-beta | freq_centered pivot | RMSE record but Pearson regressed |
| V22-gamma | Best V22 tuning | Production baseline (TST-900: 9/11) |
| V22-delta | RBN Full redux | Pressure Vessel held, data still toxic |
| V23-alpha | PyIRI ionospheric features | Record Pearson/RMSE, TST-900 4/11 |
| AUDIT-01 | Wide clamp | +0.48 was clamp floor |
| AUDIT-02 | Xavier init | Defibrillator is load-bearing |
| AUDIT-03 | 35-bucket atlas | TST-900 5/11; IRI features destroy band×time physics |

> *"Thomas Edison didn't figure out how to create a light bulb. He proved 1,000 ways how not to."*
> — KI7MT

Every failed version contributed something. V19 proved constraints are physics. V22-delta proved data composition matters even inside a Pressure Vessel. V23 proved that record-breaking aggregate metrics can hide fundamental architectural flaws. The audits proved the +0.48σ "constant" was a clamp artifact.

### 9.2 The CLCA Process

The audit suite was the CLCA process in action — Ford 8D methodology applied to neural network development:

1. **D1 (Team)**: Four agents + Judge
2. **D2 (Describe)**: SFI sidecar converges to +0.48σ across all runs
3. **D3 (Containment)**: Continue V23 training, design audits in parallel
4. **D4 (Root Cause)**: Weight inspection reveals clamp floor pinning
5. **D5 (Corrective Actions)**: Three controlled experiments (AUDIT-01/02/03)
6. **D6 (Validation)**: AUDIT-01 breaches the "invariant" at epoch 12
7. **D7 (Prevention)**: Band-SFI curve model reframes the architecture
8. **D8 (Congratulate)**: "Not bad for a human"

Nobody said it was fast. It's a results-driven process. The same methodology that catches defects on an assembly line caught a defect in a neural network. The tools are different; the discipline is identical.

For a detailed treatment of how semiconductor metrology methodology translates to ML development, see the companion paper *From Nanometers to Neurons: What Semiconductor Metrology Taught Me About Machine Learning*.

### 9.3 Pretty Numbers Don't Mean Squat

V23's record Pearson (+0.500) and RMSE (0.813σ) were the best numbers any IONIS version had ever produced. They were also meaningless. TST-900 scored 4/11 — the same as V22-delta, the version that taught us RBN was toxic.

The lesson: **aggregate metrics are necessary but not sufficient.** A model can achieve excellent global fit by learning shortcuts that satisfy the majority of observations while failing catastrophically on the physics that matter. TST-900 tests the physics. Pearson and RMSE test the statistics. They are not the same thing.

Or, as Judge put it: *"Pretty numbers don't mean squat if TST-900 fails."*

In pharmaceutical development, a drug can show excellent aggregate efficacy in Phase II trials while producing fatal side effects in specific subpopulations. Phase III exists to catch those. TST-900 is IONIS's Phase III.


## Appendix A: The V16 Physics Laws

The following constraints are **non-negotiable** for any IONIS training run:

```python
# 1. Architecture: IonisGate (gates from trunk output)
model = IonisGate(dnn_dim=11, sidecar_hidden=8)

# 2. Defibrillator initialization
def init_v16_defibrillator(model):
    def wake_up_sidecar(layer):
        if isinstance(layer, nn.Linear):
            nn.init.uniform_(layer.weight, 0.8, 1.2)
            if layer.bias is not None:
                nn.init.constant_(layer.bias, 0.0)
    model.sun_sidecar.apply(wake_up_sidecar)
    model.storm_sidecar.apply(wake_up_sidecar)
    # Strong initial offset prevents collapse
    model.sun_sidecar.fc2.bias.fill_(-10.0)
    model.storm_sidecar.fc2.bias.fill_(-10.0)
    # Freeze fc1 bias, keep fc2 bias learnable
    model.sun_sidecar.fc1.bias.requires_grad = False
    model.storm_sidecar.fc1.bias.requires_grad = False

# 3. Weight clamping after EVERY step
def clamp_v16_sidecars(model):
    with torch.no_grad():
        for sidecar in [model.sun_sidecar, model.storm_sidecar]:
            sidecar.fc1.weight.clamp_(0.5, 2.0)
            sidecar.fc2.weight.clamp_(0.5, 2.0)

# 4. HuberLoss (robust to outliers)
criterion = nn.HuberLoss(reduction='none', delta=1.0)

# 5. Gate variance loss (forces context-sensitivity)
var_loss = -0.001 * (sun_gate.var() + storm_gate.var())

# 6. 6-group optimizer
optimizer = AdamW([
    {'params': model.trunk.parameters(), 'lr': 1e-5},
    {'params': model.base_head.parameters(), 'lr': 1e-5},
    {'params': model.sun_scaler_head.parameters(), 'lr': 5e-5},
    {'params': model.storm_scaler_head.parameters(), 'lr': 5e-5},
    {'params': model.sun_sidecar.parameters(), 'lr': 1e-3},
    {'params': model.storm_sidecar.parameters(), 'lr': 1e-3},
])
```

Violation of any law results in sidecar death.


## Appendix B: The Dialectical Record

Key hypothesis transitions during V19 diagnosis:

| Date | Hypothesis | Evidence | Agent | Status |
|------|------------|----------|-------|--------|
| 2026-02-10 | RBN Full causes Pearson drop | V17 metrics | Dr. Watson | Partial |
| 2026-02-10 | Normalization scale shock | V18 Kp at +1.51σ | Bob | Partial |
| 2026-02-11 | IonisModel lacks constraints | Architecture diff | Einstein | Proposed |
| 2026-02-11 | V19.4 decisive test | Zero RBN, still died | All | **Confirmed: Structure** |
| 2026-02-11 | V20 replication | Metrics match V16 | All | **Validated** |


*"The logs have been speaking for decades, but nobody is listening."*

*Now we're listening.*



## Section 10: Eight Dead Ends — The V23-V27 Arc

### 10.1 The Pareto Frontier Emerges

Following the audits, V22-gamma stood as the production baseline: TST-900 9/11, KI7MT 16/17, Pearson +0.492, RMSE 0.821σ. One test failed — the "acid test" — predicting +0.540σ (detectable signal) on the 10m band at 02:00 UTC between Idaho and central Europe (JN48), when both endpoints were in deep darkness.

A 15-year-old ham radio operator knows this path is closed. The model with 205,621 parameters did not.

What followed was the most intensive architectural exploration in the project's history: eight distinct approaches, each attempting to teach the model what every operator knows. Every one failed.

### 10.2 The Eight Failures

| Version | Approach | Acid Test | TST-900 | KI7MT Hard | Root Cause |
|---------|----------|-----------|---------|------------|------------|
| V23 | IRI features in trunk | +2.810σ FAIL | 4/11 | 14/17 | foF2 ratio bypasses band×darkness cross-products |
| V24 | Remove sun sidecar | -0.472σ **PASS** | 4/11 | 14/17 | Both sidecars die, trunk compresses dynamic range |
| V25-alpha | 2D sidecar [SFI, freq_log] | +0.946σ FAIL | (not run) | 15/17 | Optimizer kills redundant SFI dimension |
| V25-beta | Forced SFI×freq_log product | +1.417σ FAIL | 4/11 | 12/17 | Multiplicative coupling inverts band ordering |
| V26 | 9 band-specific output heads | -5.654σ **PASS** | 4/10 | 6/17 | Heads learn band bias, not band×time physics |
| AUDIT-01 | Widen clamp [0.1, 5.0] | +0.179σ FAIL | 5/11 | — | SFI drops to new floor, proves clamp artifact |
| AUDIT-02 | Xavier init | DOA | (not run) | (not run) | Sidecars dead at epoch 1, Defibrillator is load-bearing |
| V27 | PhysicsInformedLoss fine-tuning | +2.939σ FAIL | (not run) | 11/17 | DXpedition 50× upsample overpowers 0.66% penalty |

### 10.3 The Pattern

A devastating pattern emerged across all eight experiments:

**Every architecture that passed the acid test broke global physics.**

V24 passed the acid test (-0.472σ) by compressing the entire dynamic range — day/night deltas dropped from 10+ dB to ~3 dB. V26 passed the acid test (-5.654σ) by making the 10m head pathologically negative *all the time* — predicting -6.7σ at midday (worse than night).

**Every architecture that preserved global physics failed the acid test.**

V22-gamma maintained correct band ordering, correct day/night deltas, correct storm response — and predicted +0.540σ on a path that should be closed.

The trade-off was fundamental, not accidental.

### 10.4 V27: The Final Proof

V27 was the definitive test of whether loss function modification could succeed where architectural changes had failed.

**Strategy**: Fine-tune V22-gamma (the best physics model) with a 10× loss penalty for physically impossible predictions — high-band paths (≥21 MHz) where both endpoints are below civil twilight (solar elevation < -6°) and the model predicts above -1.0σ.

**Pre-flight** (Bob on 9975WX, CUDA, 10 epochs, 1M WSPR subset):
- Acid test trending: +0.640σ → +0.248σ [OK]
- Violation rate: 0.74% (surgical, not overreaching) [OK]
- Loss decreasing, Pearson positive [OK]

**Production** (Dr. Watson on M3, MPS, 30 epochs, full recipe):
- KI7MT: 16/17 → **11/17** (lost 5 tests)
- Acid test: +0.540σ → **+2.939σ** (worse by +2.4σ)
- RMSE: 0.845σ (regressed)
- Pearson: +0.433 (regressed)

The penalty was surgical. The patient died anyway.

### 10.5 V27 Root Cause: The DXpedition Bias

Judge's diagnosis, verified by training logs:

The production data recipe includes 13M DXpedition rows (260K × 50× upsample) — **100% positive observations**. DXpedition data only records successful contacts; there is no "band closed" label. When the PhysicsInformedLoss penalty fired on 0.66% of samples, the optimizer faced a choice:

1. Push violations down (as intended)
2. Shift the entire distribution up to maintain correlation on the 99.34% majority

It chose option 2. The trunk's learned negative predictions (V22-gamma: -0.38σ on 10m EC night) were destroyed. All predictions shifted up 1-2σ.

**The lesson**: Fine-tuning from a converged checkpoint ≠ training from scratch. Data recipes that work for training are toxic for fine-tuning. The positive-only DXpedition upsampling — essential for rare-grid coverage during training — became an adversarial signal during fine-tuning.

### 10.6 Judge's Intervention

After V27, Judge called a halt:

> *"We're chasing our tails. Eight architectures, eight failures. Every fix breaks something else. V22-gamma at 16/17 is the Pareto frontier. The question isn't 'how do we train the acid test?' It's 'should we stop training and do something else?'"*

This was the CLCA discipline in action. When corrective actions create new defects faster than they fix old ones, the process is out of control. The correct response is not "try harder" — it's "change the approach."


## Section 11: The Pareto Frontier — Accepting Limits

### 11.1 What V22-gamma Actually Learned

V22-gamma's physics are remarkable for what they get right:

- **Band ordering**: High bands outperform low bands at midday; low bands outperform high bands at night
- **Day/night deltas**: 10+ dB difference on 160m, 15+ dB on 10m
- **Storm response**: Kp 9 costs +3.0σ (~20 dB) relative to Kp 0
- **Path geometry**: Long paths attenuate; equatorial paths show TEC enhancement
- **Seasonal variation**: Summer sporadic-E lifts 10m beyond F2 predictions

The model passes 16 of 17 operator-grounded tests derived from 49,000 actual QSOs and 5.7 million contest signatures.

### 11.2 What V22-gamma Cannot Learn

The single failure — 10m EU night at +0.540σ — reveals a structural limitation:

The training data contains orders of magnitude more daytime 10m observations than nighttime 10m observations (contest data shows a 10,000:1 ratio at peak vs. off-peak hours). This is not sampling bias; it reflects reality — operators don't try 10m DX at 02:00 UTC because the band is closed. The model sees predominantly positive examples on 10m and learns "10m is usually good."

The negative evidence (band closed) is implicit in the absence of observations, not explicit in labeled samples. The model has no way to learn "absence means closure" from data that only records presence.

### 11.3 The Information-Theoretic Limit

Judge framed it this way:

> *"The data says 'when people try 10m, they usually succeed.' The data does not say 'people don't try 10m at night because it's closed.' The model learns what the data teaches. The data doesn't teach this."*

This is not a bug in the model. It is a fundamental limit of supervised learning on observational data. The model can only learn P(success | attempt), not P(attempt | conditions). The acid test asks about the latter.


## Section 12: The PhysicsOverrideLayer — When to Stop Training

### 12.1 The Resolution

After eight failed architectures, the team — Judge, Patton (Failure Analyst), Einstein (Physics Consultant), Dr. Watson (Training Agent), and Bob (Infrastructure Agent) — converged on a different answer:

**Don't change the model. Add a deterministic physics constraint at inference time.**

The rule is absolute: no F2-layer skip above 21 MHz when both endpoints are below civil twilight. This is Appleton-Hartree physics, not statistical tendency. The clamp introduces zero false negatives because the condition is physically impossible.

```python
class PhysicsOverrideLayer:
    """IF freq >= 21 MHz AND tx_solar < -6° AND rx_solar < -6° AND pred > -1.0σ
       THEN clamp to -1.0σ"""
```

### 12.2 Validation Results

Cross-validated on both M3 (MPS) and 9975WX (CUDA) with identical results:

| Metric | Raw V22-gamma | With Override |
|--------|--------------|---------------|
| KI7MT Hard | 16/17 | **17/17** |
| TST-900 | 9/11 | 9/11 |
| Regressions | — | **0** |
| Acid Test | +0.540σ FAIL | **-1.000σ PASS** |

The override fired on exactly 2 of 18 KI7MT tests:
- KI7MT-002 (10m EC night): -0.380σ → -1.000σ (was passing, clamped harder)
- KI7MT-005 (acid test): +0.540σ → -1.000σ (the fix)

### 12.3 The Hybrid Architecture

The production model is now:

```
V22-gamma (205K params, IonisGate)
    ↓ inference
PhysicsOverrideLayer (deterministic, 4 lines)
    ↓
Production output (17/17 KI7MT, 9/11 TST-900)
```

This architecture embodies a principle the semiconductor industry learned decades ago: **statistical process control handles normal variation; specification limits catch physical violations.**

The model learns what the data teaches (statistical process). The override enforces what physics requires (specification limit). They are complementary, not competing.

### 12.4 Judge's Verdict

> *"We don't exit Phase 5 until one of two things exist: the model does what it needs to on its own, or we stay there until it does. But that doesn't mean we ship broken product while we work on it. V22-gamma plus the override is production. The model without the override is research."*

The CLCA process demands containment before root cause resolution. The override is the containment action — it stops the defect from reaching users. The architectural work continues, but production ships today.

### 12.5 What the Failure Record Proved

Eight dead ends were not wasted effort. They proved:

1. **The acid test is a physical boundary condition**, not a statistical tendency. No amount of training data can teach a condition that the data cannot represent.

2. **Aggregate metrics are adversarial to physics.** Every architecture that improved RMSE or Pearson degraded physics tests. The optimizer finds shortcuts; the shortcuts destroy understanding.

3. **Fine-tuning is not training.** Data recipes that work from scratch are toxic for checkpoints that have already converged. DXpedition upsampling, essential for training, destroyed fine-tuning.

4. **The scalar sidecar is vestigial.** The +0.48σ "constant" was a clamp floor artifact. The optimizer wanted the sidecar dead; the clamp kept it on life support. The trunk had absorbed SFI through cross-products.

5. **IRI features are physics shortcuts.** Giving the model foF2 directly let it bypass the band×darkness learning the cross-products encode. Record Pearson, broken physics.

6. **Defibrillator init is load-bearing.** Xavier init killed both sidecars at epoch 1. The aggressive uniform(0.8-1.2) initialization with fc2.bias=-10 is not a hyperparameter — it's the difference between life and death.

7. **Multi-head architectures learn bias, not physics.** The 10m head learned "always predict negative" — correct direction, wrong mechanism. Decoupling bands from the shared trunk destroyed band×time interaction.

8. **The Pareto frontier is real.** At 16/17 KI7MT, V22-gamma had extracted all the physics the data could teach. Pushing for 17/17 through training destroyed the 16.

The failure record is the thesis. The successes are footnotes.


## Section 13: Lessons for Physics-Constrained ML

### 13.1 When to Stop Training

Stop training when:
- Improving one metric degrades another (Pareto frontier)
- The defect is a physical boundary, not a statistical pattern
- Eight architectures have failed with documented root causes
- The fix is a four-line deterministic rule

Continue training when:
- The defect is learnable from available data
- Architectural changes show monotonic improvement
- The failure mode is not understood

### 13.2 The Hybrid Architecture Pattern

For physics-constrained ML, consider:

1. **Train the model on what data can teach.** The neural network learns P(outcome | features) from observations.

2. **Enforce physics at inference time.** Deterministic rules clamp outputs that violate known physical laws.

3. **Document which constraints are trained vs. enforced.** V22-gamma learned day/night, band ordering, storm response. The override enforces high-band night closure.

4. **Version the hybrid together.** The model without the override is not production. Ship the pair.

### 13.3 The CLCA Discipline

The Ford 8D / CLCA methodology applies to neural networks:

- **D1 (Team)**: Multi-agent collaboration with distinct roles
- **D2 (Describe)**: Quantify the defect (acid test +0.540σ)
- **D3 (Containment)**: Ship working product (override) while fixing root cause
- **D4 (Root Cause)**: Eight architectures, eight documented failures
- **D5 (Corrective Actions)**: PhysicsOverrideLayer at inference
- **D6 (Validation)**: Cross-platform identical results
- **D7 (Prevention)**: Hybrid architecture as standard pattern
- **D8 (Congratulate)**: "Not bad for a human"

The process is slow. The results are permanent.

### 13.4 The Human Contribution

Throughout the V20-V27 arc, Judge's contributions were not technical — they were methodological:

- **"The Skeptic in me says it's Code doing it, not the data."** — caught the +0.48σ clamp floor artifact that four AIs missed
- **"10m to 160m is a sine wave with 30m being the reversal point."** — reframed the ML task from scalar to curve
- **"Pretty numbers don't mean squat if the physics tests fail."** — prevented shipping V23 despite record metrics
- **"We're chasing our tails."** — recognized the Pareto frontier after eight failures
- **"Ship the override, continue the research."** — separated containment from cure

None of these required writing code. All of them required the CLCA discipline that comes from manufacturing quality engineering, not machine learning.

Judge's role is not to be smarter than the AI. Judge's role is to enforce the process when the AI wants to optimize past it.


## Appendix C: The Complete Version Lineage

```
v2 → ... → v16 (Contest Anchored)
              ↓
          v17 (RBN Full) ← FAILED: Pearson dropped
              ↓
          v18 (Normalization) ← FAILED: Kp weak
              ↓
          v19 (IonisModel refactor) ← FAILED: Constraints missing
              ↓
          v19.4 (Decisive experiment) ← FALSIFIED data hypothesis
              ↓
          v20 (Exact replication) ← SUCCESS: V16 physics restored
              ↓
          v21-alpha/beta (Vertex lat) ← Kp distillation discovery
              ↓
          v22-alpha (Solar depression) ← Cross-products emerge
              ↓
          v22-beta (freq_centered) ← RMSE record, Pearson regressed
              ↓
          v22-gamma (Best tuning) ← PRODUCTION BASELINE: 9/11, 16/17
              ↓
          v22-delta (RBN Full redux) ← FAILED: Data still toxic
              ↓
          v23 (IRI features) ← FAILED: Record metrics, 4/11 physics
              ↓
          AUDIT-01/02/03 ← Clamp floor, Defibrillator load-bearing, IRI shortcuts
              ↓
          v24 (No sun sidecar) ← FAILED: Acid pass, 3 paths lost
              ↓
          v25-alpha (2D sidecar) ← FAILED: Optimizer killed SFI
              ↓
          v25-beta (Forced product) ← FAILED: Band ordering inverted
              ↓
          v26 (9 band heads) ← FAILED: Band bias, not physics
              ↓
          v27 (PhysicsInformedLoss) ← FAILED: DXpedition bias overpowered penalty
              ↓
          v22-gamma + PhysicsOverrideLayer ← PHASE 4.0 PRODUCTION: 17/17
```


## Appendix D: Mathematical Foundations

### D.1 The IonisGate Output Equation

The model output combines a base prediction from the DNN trunk with physics-encoding sidecars modulated by learned gates:

$$\hat{y} = f_{\text{trunk}}(\mathbf{x}_{\text{geo}}) + g_{\text{sun}}(\mathbf{x}_{\text{geo}}) \cdot s_{\text{sun}}(\text{SFI}) + g_{\text{storm}}(\mathbf{x}_{\text{geo}}) \cdot s_{\text{storm}}(K_p)$$

Where:
- $\mathbf{x}_{\text{geo}}$ = geographic/temporal features (11-13 dims): distance, freq_log, hour_sin/cos, az_sin/cos, lat_diff, midpoint_lat, season_sin/cos, day_night_est, cross-products
- $f_{\text{trunk}}: \mathbb{R}^{d} \rightarrow \mathbb{R}$ = DNN trunk (d→512→256) + base head (256→128→1)
- $g_{\text{sun}}, g_{\text{storm}}: \mathbb{R}^{256} \rightarrow [0.5, 2.0]$ = gates from trunk's 256-dim hidden layer
- $s_{\text{sun}}, s_{\text{storm}}: \mathbb{R} \rightarrow \mathbb{R}^+$ = MonotonicMLP sidecars

**Critical**: The trunk receives **zero** direct solar information. SFI and Kp flow only through the sidecars. This "Nuclear Option" forces the optimizer to route solar physics through the constrained pathways.

### D.2 MonotonicMLP Sidecar

Each sidecar is a two-layer MLP with weight constraints ensuring monotonicity:

$s(x) = \text{sp}(W_2 \cdot \text{sp}(W_1 \cdot x + b_1) + b_2)$

Where:
- $W_1, W_2 \in [0.5, 2.0]$ (clamped after every optimizer step)
- $\text{sp}$ = softplus activation: $\text{sp}(z) = \log(1 + e^z)$ (not sigmoid)
- Weights initialized uniform(0.8, 1.2)
- $b_2$ initialized to -10.0 ("Defibrillator")

The clamp $[0.5, 2.0]$ ensures:
1. Weights cannot go negative (preserves monotonicity)
2. Weights cannot go to zero (prevents sidecar death)
3. Weights cannot explode (prevents gradient instability)

### D.3 HuberLoss (Robust Regression)

$$L_\delta(y, \hat{y}) = \begin{cases} \frac{1}{2}(y - \hat{y})^2 & \text{if } |y - \hat{y}| \leq \delta \\ \delta \cdot (|y - \hat{y}| - \frac{1}{2}\delta) & \text{otherwise} \end{cases}$$

With $\delta = 1.0$ (1σ threshold). This provides:
- Quadratic penalty for small errors (standard regression)
- Linear penalty for large errors (robust to outliers)

Contest anchor observations (+10σ / 0σ) would dominate MSE loss. HuberLoss treats them as linear penalties, preventing them from overwhelming the gradient.

### D.4 Appleton-Hartree: Why SFI Effect is Frequency-Dependent

The refractive index of the ionosphere for a radio wave is given by the Appleton-Hartree equation. In simplified form for vertical incidence:

$$n^2 = 1 - \frac{f_p^2}{f^2}$$

Where:
- $n$ = refractive index
- $f_p$ = plasma frequency $\propto \sqrt{N_e}$ (electron density)
- $f$ = wave frequency

**F2 layer** (reflection): Wave reflects when $n^2 = 0$, i.e., when $f = f_p$. Higher SFI → higher $N_e$ → higher $f_p$ → higher MUF. **SFI helps high bands.**

**D layer** (absorption): Absorption coefficient:

$$\kappa \propto \frac{N_e \cdot \nu}{f^2 + \nu^2}$$

Where $\nu$ = collision frequency. Higher SFI → higher $N_e$ → more absorption. Effect scales as $1/f^2$. **SFI hurts low bands disproportionately.**

This is why a scalar SFI sidecar cannot work: the physics requires multiplication above ~10 MHz and division below. The zero crossing at 30m (10 MHz) is where the two effects cancel.

### D.5 Feature Normalization

All features are normalized to approximately [-1, 1] or [0, 1]:

| Feature | Normalization | Range |
|---------|--------------|-------|
| distance | $d / 20000$ km | [0, 1] |
| freq_log | $\log_{10}(f) / 8$ | [0.2, 0.9] |
| hour_sin/cos | $\sin/\cos(2\pi h / 24)$ | [-1, 1] |
| az_sin/cos | $\sin/\cos(\theta)$ | [-1, 1] |
| lat_diff | $(lat_{tx} - lat_{rx}) / 180$ | [-1, 1] |
| midpoint_lat | $lat_{mid} / 90$ | [-1, 1] |
| season_sin/cos | $\sin/\cos(2\pi d / 365)$ | [-1, 1] |
| sfi | $\text{SFI} / 300$ | [0.23, 0.80] |
| kp_penalty | $1 - K_p / 9$ | [0, 1] (inverted: high Kp → low value) |

### D.6 PhysicsOverrideLayer

The deterministic inference-time constraint:

$$\hat{y}_{\text{final}} = \begin{cases} -1.0 & \text{if } f \geq 21\text{ MHz} \land \theta_{tx} < -6° \land \theta_{rx} < -6° \land \hat{y} > -1.0 \\ \hat{y} & \text{otherwise} \end{cases}$$

Where:
- $f$ = frequency in MHz
- $\theta_{tx}, \theta_{rx}$ = solar elevation angles at TX/RX (degrees)
- $-6°$ = civil twilight threshold (sun below horizon)
- $-1.0\sigma \approx -24.5$ dB (below WSPR decode floor)

This encodes the physical law: no F2-layer skip above 21 MHz when both endpoints are in darkness. The condition is absolute, not statistical.

### D.7 Pearson Correlation Coefficient

$$r = \frac{\sum_i (y_i - \bar{y})(\hat{y}_i - \bar{\hat{y}})}{\sqrt{\sum_i (y_i - \bar{y})^2} \sqrt{\sum_i (\hat{y}_i - \bar{\hat{y}})^2}}$$

Production threshold: $r > +0.48$ (V22-gamma achieves +0.492).

For comparison, VOACAP achieves $r \approx +0.02$ on the same validation set.


## What's Next: Phase 5.0 and the ISAAC Protocol

Phase 4.0 concluded with the realization that V22-gamma represents the Pareto frontier of what empirical WSPR data can teach a continuous tensor architecture. The `PhysicsOverrideLayer` successfully contains the model's inability to predict high-band night closures, but as a containment action, it treats the symptom rather than the root cause.

The root cause of the 10m acid test failure is a fundamental dataset flaw: **ultimate survivorship bias**. The 13.18 billion WSPR observations record what *happened*. They cannot record what *could not happen*. Because operators do not transmit on 10m when the band is closed, the dataset contains zero explicit examples of absolute F2-layer collapse. The neural network never receives a negative gradient to pull those predictions into the noise floor.

In the parlance of failure analysis: we spent six months studying the flower, but the answer was the missing ants.

### The Phase 5.0 Objective: Eliminating the Override

To eliminate the inference-time override, we must teach the neural network the word "No."

In the early 2000s, semiconductor metrology software like Accent Optical's ISAAC modeled structures from first physics principles, independent of physical measurement. It could tell a process engineer that a specific film thickness was physically impossible before a wafer was ever etched. Phase 5.0 brings this exact philosophy to the IONIS pipeline.

Instead of relying solely on observational data, Phase 5.0 will introduce **Synthetic Negative Anchors** — an ISAAC-style dataset generated entirely from physics equations, not radios.

**The Execution Plan:**

1. **First-Principles Generation:** Using Appleton-Hartree constraints and the PyIRI atlas, the infrastructure pipeline will generate a synthetic dataset of physically impossible paths (frequency ≥ 21 MHz, both endpoints ≤ -6° solar elevation).

2. **The -30 dB Anchor:** These synthetic rows will be hardcoded with a Signal-to-Noise Ratio of -30 dB, placing them definitively below the WSPR decode floor (-28 dB).

3. **Equilibrium Injection:** These synthetic negatives will be injected into the training mix at the same volume as the heavily upsampled DXpedition positive data (~13 million rows). By counterbalancing the extreme positive bias with extreme negative bias from first-principles physics, we force the optimizer to learn the boundary condition natively.

Phase 4.0 proved what the neural network could learn from observation. Phase 5.0 will prove what it can learn from the laws of physics.


## References

- Appleton, E. V. (1932). Wireless studies of the ionosphere. *Journal of the Institution of Electrical Engineers*, 71(430), 642-650.

- Bilitza, D., Altadill, D., Truhlik, V., et al. (2017). International Reference Ionosphere 2016: From ionospheric climate to real-time weather predictions. *Space Weather*, 15(2), 418-429.

- Davies, K. (1990). *Ionospheric Radio*. Peter Peregrinus Ltd.

- Ford Motor Company. (c. 1987). *Team Oriented Problem Solving (TOPS)*. Internal quality methodology; precursor to Global 8D.

- Ratcliffe, J. A. (1959). *The Magneto-Ionic Theory and Its Applications to the Ionosphere*. Cambridge University Press.


<div class="paper-citation">
<p class="cite-label">How to cite</p>
<p>Beam, G. (KI7MT), et al. "The Dialectical Engine: Multi-Agent Falsification in Scientific Software Development." <em>IONIS Project Technical Papers</em>, Version 1.1, February 2026. Available at: <a href="https://ionis-ai.com/papers/the-dialectical-engine/">ionis-ai.com/papers/the-dialectical-engine</a></p>
</div>

</div> <!-- /paper-article -->
