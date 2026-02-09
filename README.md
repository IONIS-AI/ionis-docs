# KI7MT Sovereign AI Lab — Documentation

Documentation site for the **IONIS** (Ionospheric Neural Inference System) project.

Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## About IONIS

IONIS is a machine learning system that predicts HF radio propagation using real-world observations. Instead of relying solely on theoretical ionospheric models, IONIS learns from billions of heterogeneous observations (WSPR, RBN, Contest Logs) harmonized through a Z-normalized signal-to-noise architecture.

**Current Model:** IONIS V13 Combined — *Multi-Source Hybrid*
- 203,573 parameters
- Trained on 20M WSPR + 91K RBN DXpedition signatures
- Bridges weak-signal digital modes with high-power CW and DXpedition activity
- 152 rare DXCC entities covered (Bouvet, Heard Island, South Sandwich, etc.)
- **Step K Quality Test**: Pearson r +0.3675 vs VOACAP +0.0218 (IONIS wins 9/10 bands)
- Low-band correlation delta: +0.5167 (IONIS +0.3204 vs VOACAP -0.1963)

**V14-TP (Terrestrial Physics)** — in training. Uses balloon-filtered signature library (89.9M signatures, 276M contaminated spots excluded).

## Data Sources

| Source | Volume | Status | Role |
|--------|--------|--------|------|
| WSPR | 10.8B spots | Complete | Signal floor baseline |
| RBN | 2.18B spots | Complete | High-SNR transitions, DXpeditions |
| Contest Logs | 195M QSOs | Complete | Ground truth validation |
| Solar Indices | 76K rows | Complete | Gated physics input (SFI, Kp) |
| DXpedition Synthesis | 2.52M paths | Complete | 152 rare DXCC entities (RBN x GDXF) |

## Documentation Sections

- **Architecture** — Model design, monotonic sidecars, gated physics
- **Methodology** — Data pipeline, bronze/silver/gold layers, training
- **Validation** — Physics tests, reference model comparison, test specifications
- **Roadmap** — D-to-Z path to production (Steps D-K complete, V14-TP training in progress)
- **Tools** — WSPR ingestion, solar pipeline, contest/RBN, CUDA engine

## Local Development

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/KI7MT/ki7mt-ai-lab-docs.git
cd ki7mt-ai-lab-docs

# Install dependencies
pip install -r requirements.txt

# Serve locally (with live reload)
mkdocs serve

# Build static site
mkdocs build
```

The site will be available at `http://127.0.0.1:8000/`.

## Related Repositories

| Repository | Purpose |
|------------|---------|
| [ki7mt-ai-lab-training](https://github.com/KI7MT/ki7mt-ai-lab-training) | PyTorch model training and validation |
| [ki7mt-ai-lab-apps](https://github.com/KI7MT/ki7mt-ai-lab-apps) | Go data ingesters (WSPR, solar, contest, RBN) |
| [ki7mt-ai-lab-core](https://github.com/KI7MT/ki7mt-ai-lab-core) | DDL schemas, SQL scripts, base configuration |
| [ki7mt-ai-lab-cuda](https://github.com/KI7MT/ki7mt-ai-lab-cuda) | CUDA signature embedding engine |

## License

GPLv3 — See [LICENSE](LICENSE) for details.

## Author

Greg Beam, KI7MT

---

*Built for amateur radio operators who want propagation predictions based on what actually happened, not what theory says should happen.*
