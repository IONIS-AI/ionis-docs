# ionis-docs

Documentation site for the **IONIS** (Ionospheric Neural Inference System) project.

Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## About IONIS

IONIS is a machine learning system that predicts HF radio propagation using real-world observations. Instead of relying solely on theoretical ionospheric models, IONIS learns from billions of heterogeneous observations (WSPR, RBN, Contest Logs) harmonized through a Z-normalized signal-to-noise architecture.

**Current Model:** IONIS V20 Golden Master — *Production*
- IonisGate architecture (203,573 parameters)
- Trained on 20M WSPR + 4.55M DXpedition (50x) + 6.34M Contest = ~31M rows
- Pearson **+0.4879**, RMSE **0.862σ**, Kp **+3.487σ**, SFI **+0.482σ**
- Step I Recall: 96.38% vs VOACAP 75.82% (+20.56 pp)
- PSK Reporter live validation: 84.14% recall on independent data
- 100 epochs in 4h 16m on Mac Studio M3 Ultra (MPS backend)

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
| [ionis-apps](https://github.com/IONIS-AI/ionis-apps) | Go data ingesters (WSPR, solar, contest, RBN) |
| [ionis-core](https://github.com/IONIS-AI/ionis-core) | DDL schemas, SQL scripts, base configuration |
| [ionis-cuda](https://github.com/IONIS-AI/ionis-cuda) | CUDA signature embedding engine |

## License

GPLv3 — See [LICENSE](LICENSE) for details.

## Author

Greg Beam, KI7MT

---

*Built for amateur radio operators who want propagation predictions based on what actually happened, not what theory says should happen.*
