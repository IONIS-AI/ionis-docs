# ionis-docs

Documentation site for the **IONIS** (Ionospheric Neural Inference System) project.

Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## About IONIS

IONIS is a machine learning system that predicts HF radio propagation using real-world observations. Instead of relying solely on theoretical ionospheric models, IONIS learns from billions of heterogeneous observations (WSPR, RBN, Contest Logs) harmonized through a Z-normalized signal-to-noise architecture.

**Current Model:** IONIS V22-gamma + PhysicsOverrideLayer — *Production (Phase 4.0)*
- IonisGate architecture (205,621 parameters, 17 features)
- Trained on 38.7M rows: WSPR + DXpedition (50x) + Contest
- Pearson **+0.492**, RMSE **0.821σ**, KI7MT **17/17**, TST-900 **9/11**
- PhysicsOverrideLayer: deterministic high-band night closure clamp
- Checkpoint format: safetensors (805 KB)

## Local Development

```bash
git clone https://github.com/IONIS-AI/ionis-docs.git
cd ionis-docs
pip install -r requirements.txt
mkdocs serve
```

The site will be available at `http://127.0.0.1:8000/`.

## Related Repositories

| Repository | Purpose |
|------------|---------|
| [ionis-training](https://github.com/IONIS-AI/ionis-training) | PyTorch model training and validation |
| [ionis-validate](https://github.com/IONIS-AI/ionis-validate) | Model validation suite (PyPI) |
| [ionis-apps](https://github.com/IONIS-AI/ionis-apps) | Go data ingesters (WSPR, solar, contest, RBN, PSKR) |
| [ionis-core](https://github.com/IONIS-AI/ionis-core) | DDL schemas, SQL scripts, base configuration |
| [ionis-cuda](https://github.com/IONIS-AI/ionis-cuda) | CUDA signature embedding engine |
| [ionis-hamstats](https://github.com/IONIS-AI/ionis-hamstats) | ham-stats.com publishing |

## License

GPLv3 — See [LICENSE](LICENSE) for details.

## Author

Greg Beam, KI7MT

---

*Built for amateur radio operators who want propagation predictions based on what actually happened, not what theory says should happen.*
