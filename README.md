# KI7MT Sovereign AI Lab — Documentation

Documentation site for the **IONIS** (Ionospheric Neural Inference System) project.

Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## About IONIS

IONIS is a machine learning system that predicts HF radio propagation using real-world observations. Instead of relying solely on theoretical ionospheric models, IONIS learns from billions of actual radio contacts to predict what the bands will do next.

**Current Model:** IONIS V13 Combined
- 203,573 parameters
- Trained on 20M WSPR + 91K RBN DXpedition signatures
- 152 rare DXCC entities covered
- +9.5 percentage points improvement over reference model (VOACAP)

## Data Sources

| Source | Volume | Status |
|--------|--------|--------|
| WSPR | 10.8B spots | Complete |
| RBN | 2.18B spots | Complete |
| Contest Logs | 232.6M QSOs | Complete |
| Solar Indices | 76K rows | Complete |

## Documentation Sections

- **Architecture** — Model design, monotonic sidecars, gated physics
- **Methodology** — Data pipeline, bronze/silver/gold layers, training
- **Validation** — Physics tests, VOACAP comparison, test specifications
- **Roadmap** — D-to-Z path from infrastructure to production validation
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
| [ki7mt-ai-lab-devel](https://github.com/KI7MT/ki7mt-ai-lab-devel) | Development notes and shared context |

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

## Author

Greg Beam, KI7MT

---

*Built for amateur radio operators who want propagation predictions based on what actually happened, not what theory says should happen.*
