# Running Predictions

IONIS provides two prediction interfaces: `predict.py` for single-path
queries and version-specific oracle/validation scripts for batch evaluation.

## Single-Path Prediction

The unified predictor combines the neural oracle with a historical signature
search, weighting results by signature density.

### Basic Usage

```bash
cd ionis-training/scripts

python predict.py \
    --tx FN31 --rx JO21 \
    --band 20m \
    --hour 14 --month 6
```

### With Solar Conditions

```bash
python predict.py \
    --tx FN31 --rx JO21 \
    --band 20m \
    --hour 14 --month 6 \
    --sfi 180 --kp 3
```

Defaults: SFI 150, Kp 2 (moderate solar activity, quiet geomagnetic).

### JSON Output

```bash
python predict.py \
    --tx FN31 --rx JO21 \
    --band 20m --hour 14 --month 6 \
    --json
```

### Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `--tx` | Yes | Transmitter grid (4-char Maidenhead) | `FN31` |
| `--rx` | Yes | Receiver grid (4-char Maidenhead) | `JO21` |
| `--band` | Yes | Band label or ADIF ID | `20m` or `107` |
| `--hour` | Yes | UTC hour (0-23) | `14` |
| `--month` | Yes | Month (1-12) | `6` |
| `--sfi` | No | Solar Flux Index (default 150) | `180` |
| `--kp` | No | Kp geomagnetic index (default 2) | `3` |
| `--host` | No | ClickHouse host (default `10.60.1.1`) | `192.168.1.90` |

### Interpreting Output

The predictor returns three assessments:

1. **Neural Oracle** — model prediction in sigma-normalized units, converted
   to dB
2. **Signature Search** — median SNR from the nearest historical signatures
   in ClickHouse
3. **Combined** — confidence-weighted blend of both

**Confidence weighting:**

| Signature Density | Oracle Weight | Signature Weight |
|-------------------|---------------|------------------|
| HIGH (dense) | 30% | 70% |
| MEDIUM | 50% | 50% |
| LOW (sparse) | 70% | 30% |
| None found | 100% | — |

**Condition labels** (based on combined SNR in dB):

| SNR Threshold | Condition | Typical Modes |
|---------------|-----------|---------------|
| > -10 dB | EXCELLENT | SSB, Voice |
| > -15 dB | GOOD | CW, Digital |
| > -20 dB | FAIR | FT8, FT4 |
| > -28 dB | MARGINAL | WSPR |
| <= -28 dB | CLOSED | — |

## Batch Validation

Version-specific oracle scripts evaluate the model against ground-truth
signatures from ClickHouse.

### Standalone Validation (ionis-validate)

The easiest way to validate is with the `ionis-validate` CLI (no ClickHouse required):

```bash
pip install ionis-validate
ionis-validate test
```

This runs 29 operator-grounded tests: KI7MT 18/18 + TST-900 9/11.

### Key Metrics

| Metric | Description | V22-gamma Result |
|--------|-------------|------------------|
| Pearson r | Correlation between predicted and observed SNR | +0.492 |
| RMSE | Root mean squared error in sigma units | 0.821σ |
| KI7MT operator tests | Operator-grounded physics gates | 17/17 |
| TST-900 band x time | Band discrimination across time periods | 9/11 |

## Training a New Model Version

Training is covered in detail in the [Training Methodology](../model/methodology/training.md)
page. At a high level:

1. Export training data: `gold_v6.csv` from ClickHouse (see [Gold Layer](../model/methodology/gold_layer.md))
2. Transfer to training host (M3 Ultra via DAC link)
3. Create a new version config: `versions/vNN/config_vNN.json`
4. Run training: `python train.py --config versions/vNN/config_vNN.json`
5. Validate: run `validate_vNN.py` against quality test paths

The model architecture (IonisGate) and its six non-negotiable constraints
are documented in the [IonisGate Architecture](../model/architecture/ionisgate.md) page.
