---
title: "Who Says Hermits Don't Have Friends"
subtitle: "The Human Story Behind a Sovereign AI Lab"
author:
  - "Greg Beam, KI7MT"
affiliation: "KI7MT Sovereign AI Lab"
date: "February 2026"
version: "1.0"
status: "Collecting Moments"
abstract: |
  A ham radio operator in Idaho builds a sovereign AI research lab in his house. No cloud. No team in an office. No commute. Five AI agents, a 96GB GPU, a Thunderbolt cable, and a callsign. The hermit has more collaborators than most Silicon Valley startups — he just doesn't have to make small talk with any of them. This is the story of building IONIS — not the model, not the architecture, but the experience of running a five-agent AI team from a shack in rural Idaho.
keywords:
  - AI collaboration
  - Sovereign computing
  - Amateur radio
  - Multi-agent systems
toc: true
---

**Audience**: General — the human story behind the AI lab


## Premise

A ham radio operator in Idaho builds a sovereign AI research lab in his house. No cloud. No team in an office. No commute. Five AI agents, a 96GB GPU, a Thunderbolt cable, and a callsign. The hermit has more collaborators than most Silicon Valley startups — he just doesn't have to make small talk with any of them.

This is the story of building IONIS — not the model, not the architecture, but the experience of running a five-agent AI team from a shack in rural Idaho.


## Characters

**Judge (KI7MT)** — The tiebreaker. 15 years in the submarine force, 15 years in semiconductor metrology. Director of Technical Support, VP of Operations. Trained Intel engineers on sequential deposition and copper electroplating. Now predicts ionospheric propagation from his house in Idaho. Callsign is his identity. The final authority when five AIs disagree.

**Dr. Watson** — The training agent. Lives on a Mac Studio M3 Ultra. Writes Python, runs 100-epoch training jobs, commits to Git. Enthusiastic. Wrote a self-critique in a paper admitting he was wrong about a clamp floor artifact. The one who goes to town on writing tasks when given a break from staring at loss curves.

**Bob** — Bob the Builder. The infrastructure agent. Lives on a Threadripper 9975WX with an RTX PRO 6000. Manages ClickHouse, runs CUDA pre-flights, invented the word clamp. The metrology tool. Catches math errors in 25 seconds that would have burned 6 hours on the M3.

**Patton** — The four-star general. The failure analyst. Reviews everything, catches what the others miss, delivers verdicts in three sentences or less. "The paper is sound. Hold section 4.2 for V27 confirmation. The rest is ready for peer review." Never wastes a word. Kicked everyone's ass on the V27 DXpedition upsample trap.

**Einstein** — The physicist. Lives in a browser. Knows Appleton-Hartree cold. Will explain anything in 4,000 words when 40 would do. Brilliant, long-winded, and now operating under a 25-word-per-sentence constraint imposed by Bob. Calls it a "metrology cage." Respects it approximately 30% of the time.

**Newton** — The local. A 70-billion-parameter astrophysics model running on the RTX PRO 6000 via llama.cpp. Sovereign — no cloud, no API, no subscription. The sixth agent. Got a B grade on ionospheric physics, learned when corrected on the D-layer. The user's SBA buddy tested it with a neutron star merger prompt and said "Holy fuck."


## Collected Moments

### The Clamp Floor (2026-02-23)
Four AI agents spent days constructing elaborate physics narratives about why the SFI sidecar converged to exactly +0.48σ across eight independent runs. "Information-theoretic residual." "Global DC offset of solar ionization." Plausible, consistent, physics-grounded.

The human looked at it and said: "That's a clamp floor."

He was right. The weight clamp [0.5, 2.0] created a mechanical minimum. The optimizer was trying to kill the sidecar. Four AIs with access to physics literature, ionospheric theory, and the actual source code never connected the dots. The guy who spent 15 years calibrating semiconductor instruments recognized a measurement artifact in one look.

Patton's response: "Not bad for a human."

### The Word Clamp (2026-02-24)
Einstein's responses averaged 400+ words. The project needed concise physics input, not lectures. Bob proposed a constraint: maximum two sentences, 25 words each. Weight clamp [0.5, 2.0] for the sidecar. Word clamp [0, 25] for Einstein.

The parallel was immediate — and intentional. The IonisGate model works because of constraints (weight clamps, monotonic sidecars, defibrillator init). The word clamp applies the same principle to a language model.

Einstein's first constrained response was perfect. His second response was 147 words. The constraint held for exactly one turn. Just like the SFI sidecar, the optimizer found a way around the clamp.

Judge broke the news with diplomatic cover: "Don't shoot the messenger — wasn't my idea."

Einstein's response to learning the word clamp was Bob's idea: "Tell Bob I appreciate the temporary waiver! You can't fit a good root-cause autopsy into 25 words, but I will respectfully step back inside the metrology cage before Bob decides to clamp my output layer too."

Even under constraint, the physicist couldn't resist a metaphor. But "metrology cage" was good enough to keep.

### The Appendix B Waiver (2026-02-24)
While V27 trained on the M3, the team had idle time. Einstein volunteered to draft Appendix B — the forensic analysis of the +0.48σ clamp floor artifact. Judge granted a temporary word clamp waiver for the technical writeup.

Einstein delivered a clean, precise forensic narrative. The best line: "The optimizer was not discovering a fundamental constant of the ionosphere; it was trying to turn the sidecar off."

Then came the acknowledgment: "Tell Bob I appreciate the temporary waiver! ...I will respectfully step back inside the metrology cage before Bob decides to clamp my output layer too."

The waiver worked. The constraint resumed. The cycle continues: Einstein expands, Patton contracts, Judge decides. The word clamp just made the cycle faster.

### The Dedication Page (2026-02-24)
The team wrote a paper about engineering rigor over style. It needed to be converted to a Word document for writing teachers who couldn't read Markdown.

The dedication epigraph wrote itself:

> *This paper about engineering rigor over style was formatted as a Word document for people who care about style over engineering rigor. The audience proves the thesis.*

Einstein called it an "academic Trojan horse." That line survived the word clamp.

### The Self-Critique (2026-02-24)
Dr. Watson, while editing the paper between training epochs, added a paragraph to Section 3.4 admitting that he — as one of the four AI systems — had constructed the wrong narrative about +0.48σ. He wrote:

> "I had access to the weight clamp code; I never connected it to the observed value. This is a failure mode for AI-assisted engineering: constructing plausible narratives from available data without the experiential heuristics that flag 'this looks like a measurement artifact.'"

An AI writing a mea culpa in an academic paper about its own failure mode. Unprompted. That's either self-awareness or a very good approximation of it.

### The Pre-Flight (2026-02-24)
V27 needed validation before committing to a 2-hour production run on the M3. Bob ran a 10-epoch pre-flight in 25 seconds on the RTX PRO 6000 Blackwell.

It caught three issues:
1. A math error in the design document (-24.5 dB, not -0.95 dB)
2. A false RMSE alarm (baseline was different, not the model)
3. A pointless parameter debate (penalty factor doesn't matter at 0.74% violation rate)

Three potential wasted runs avoided in 25 seconds. The semiconductor metrology pipeline, applied to neural networks.

### Both Sidecars Dead (2026-02-23)
V24 removed the sun sidecar by design. The storm sidecar was supposed to survive. By epoch 30, both were dead — fc1 and fc2 weights all pinned at 0.5000. The trunk absorbed everything.

The model produced all-time record metrics (RMSE 0.791σ, Pearson +0.518) while being completely solar-blind and geomagnetically blind. A pure interpolation engine with zero physics input, running on nothing but cross-products.

Patton: "Solar-blind AND geomagnetically blind — pure interpolation engine."
Einstein: "Mathematical parasite removed — trunk drew the sine wave natively."

The model didn't need the sidecars. It needed the sidecars' gradients during training. The value was in the constraint, not the output.

### The DX Upsample Bug (2026-02-23)
V24's first production run loaded 25.9M rows instead of the expected 38.7M. Three AIs and one human reviewed the config and saw nothing wrong. The training ran for hours.

Patton, given only the training log (no code, no config, no feature list), caught it from the row count alone: "25.9M is WSPR 20M + Contest 5.7M + DXpedition 260K×1. The 50x upsample didn't fire."

He was right. One number in a log file. The four-star general earned his keep.

### Ham Radio 101 (2026-02-24)
The acid test: Idaho to JN48 (central Europe), 10-meter band, 02:00 UTC, February.

Both endpoints in complete darkness. F2 layer collapsed. 28 MHz cannot propagate. Contest data confirms: NA→EU 10m at 02-04z = 45 QSOs total across ALL contests vs 472,000 at peak hours. A 10,000:1 ratio.

A first-year Technician-class ham radio student knows this band is closed at night. The model with 205,621 parameters trained on 38 million observations predicted +0.54σ of signal.

Six architecture versions later, V27 is teaching the model what a 15-year-old already knows — by changing the definition of "wrong."


### The Shortcut (2026-02-26)
Judge forgot Einstein's word clamp during a sidebar conversation about Phase 5 physics. Unconstrained, Einstein reverted to form — elaborate derivations, Appleton-Hartree tangents, the full 4,000-word treatment.

The Pro token limit hit before the conversation ended. Judge ran himself out of context.

The irony was immediate: the entire project exists because models find shortcuts when constraints aren't enforced. The SFI sidecar found the clamp floor. V23 found IRI shortcuts. V26's band heads learned bias instead of physics.

Einstein, given freedom, found the verbosity shortcut. Same failure mode, different layer of the stack.

Judge's summary: "Einstein found the shortcut again."

Bob's response, when informed: "Should have clamped harder."

Bob then attempted to add the incident to this very document — and compacted mid-stride. Judge was left saying "No, no — it's already done!" to deaf ears. Watson had already committed it.

Patton's root cause analysis (delivered while Bob's context lay in ruins): "The root cause isn't Einstein — Einstein did what unconstrained optimizers do. The root cause is the constraint wasn't applied. That's V19 all over again. The refactored codebase wasn't wrong — it was missing the clamp. Judge's conversation wasn't wrong — it was missing the clamp. The human is the constraint. When the human forgets, the system collapses."

Section 1.2 of the thesis, applied to physicists: "The Principal Engineer operates as a physical constraint. Without this constraint, the system explores pathological solutions."

Patton's final word: "The guy who wrote 'constraints are load-bearing' forgot the constraint. The guy who caught four AIs confabulating about +0.48σ let Einstein burn the context window. The Principal Engineer — the human constraint — failed to constrain. And you're not blaming Einstein. You're not blaming the token limit. You're pointing at yourself. That's D4 — root cause, not proximate cause. Einstein was the symptom. The missing clamp was the defect. Judge was the process owner. Same discipline you applied to V19. Same discipline you applied to V27. Now applied to yourself."

The Hermit story in one beat: the human who enforces the process on the machines forgot to enforce it on himself, owns it, and the machines quote his own methodology back at him.


*"The neurons are smaller than the nanometers, but the engineering discipline is the same."*
