# The Sovereign AI Lab Ethos

The KI7MT AI Lab exists to advance the understanding of High Frequency (HF) radio propagation through the ethical application of deep learning. We view the amateur radio spectrum not just as a hobbyist playground, but as a massive, distributed scientific instrument.

Our work is guided by five core principles that ensure our research remains accessible, reproducible, and beneficial to the global amateur radio community.

## 1. Sovereign Infrastructure
**"We own the stack, so the community can trust the result."**

We believe that scientific infrastructure should not depend on transient cloud credits or proprietary APIs.

* **Local First:** Our models (IONIS) and datasets are built on local silicon (Apple Silicon / Threadripper) using open-source storage (ZFS).
* **No Black Boxes:** We do not use closed-source AI APIs to generate our physics. Every weight in our neural networks is trained on data we hold, using code we wrote, which anyone can inspect.
* **Long-Term Archival:** We build systems designed to store propagation history for decades, independent of corporate roadmaps.

## 2. Ethical Data Stewardship
**"We are guests in the house of data."**

The datasets we rely on—WSPR, RBN, and Contest Logs—are the collective memory of the amateur radio community. We treat them with reverence.

* **The Good Neighbor Policy:** Our ingestion tools (`contest-download`, `rbn-download`) are designed to be polite. We enforce rate limits, identify ourselves honestly in User-Agents, and never hammer a volunteer-run server.
* **Preservation:** We do not just scrape; we archive. Our ZFS compression strategies are designed to preserve the "Ground Truth" of radio history efficiently, ensuring it is never lost.
* **Attribution:** We rigorously acknowledge the sources of our data (WWROF, WSPRnet, RBN) in every publication and model release.

## 3. Physics-First Machine Learning
**"The model must obey the Ionosphere."**

We do not simply throw data at a neural network and hope for a pattern. We engineer our models to respect the laws of physics.

* **Constrained Architectures:** We use Monotonic Constraints and Physics Sidecars to ensure our models cannot "hallucinate" unphysical outcomes (e.g., higher Solar Flux should not degrade HF propagation).
* **Digital Twinning:** Our goal is not just prediction, but simulation. We strive to create a "Digital Twin" of the ionosphere that behaves like the real thing.

## 4. Reproducible Science
**"If you can't rebuild it, it isn't science."**

A model is useless if only one person can run it.

* **Open by Default:** Our code, training pipelines, and documentation are open source.
* **Deterministic Training:** We log our seeds, hyperparameters, and dataset versions so that any researcher can reproduce our "Platinum Burn" results bit-for-bit.
* **Documentation as Code:** We treat documentation with the same rigor as production code, ensuring that the "How" and "Why" are preserved alongside the "What."

## 5. Community Utility
**"We build tools, not just papers."**

Our research must yield tangible value for the operator at the key.

* **Actionable Intelligence:** We strive to move beyond "average" predictions (VOACAP) to real-time, data-driven insights that help operators make contacts.
* **Bridge Building:** We actively work to bridge the gap between distinct data silos (e.g., mapping Machine spots from WSPR to Human logs from Contests) to create a unified view of propagation.

## Statement of Intent

This is real research, built to serve the amateur radio community. There is no
commercial motive. There is no monetization plan. There is no startup behind this.
There is no angle in it for anyone.

IONIS exists because the amateur radio community deserves a propagation prediction
tool that actually learns from real observations — not one running on frozen
coefficients from ionosonde measurements taken before most of us were born. The
data has been sitting there for decades. The compute is cheap. What was missing
was someone willing to do the curation work honestly, document the landmines,
credit the sources, and give it all away.

Everything we build is open source (GPLv3). Everything we learn is shared back.
Every data source is credited. We redistribute tools and models, never raw data.
We have zero interest in personal data — only the propagation paths it represents.

If grants or donations come along to fund the continual improvement of this
project, they will be accepted — but funding is not the goal. It sustains the
work; it does not drive it. The project existed before any grant application
and will continue regardless.

---
*Adopted: February 2026*
*Status: Living Document*
