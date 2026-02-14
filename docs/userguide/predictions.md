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

### Validate Against Signatures

```bash
cd ionis-training/versions/v20

python validate_v20.py --host 10.60.1.1
```

This computes Pearson correlation and RMSE against `validation.quality_test_paths`
(100K signatures stratified by band).

### Validate Against Live PSK Reporter Data

```bash
python validate_v20_pskr.py --host 10.60.1.1
```

This tests the model against real-time PSK Reporter spots with current solar
conditions — data the model has never seen during training.

### Key Metrics

| Metric | Description | V20 Result |
|--------|-------------|------------|
| Pearson r | Correlation between predicted and observed SNR | +0.4879 |
| RMSE | Root mean squared error in sigma units | 0.862 |
| SFI effect | SNR benefit from solar flux (should be positive, monotonic) | +0.482 sigma |
| Kp effect | SNR cost from geomagnetic storms (should be negative, monotonic) | -3.487 sigma |

## Comparing Against VOACAP

To run a side-by-side comparison of IONIS vs VOACAP predictions:

```bash
cd ionis-training/versions/v20

python validate_v20.py --host 10.60.1.1 --voacap
```

This evaluates both models against the same ground-truth paths and reports
Pearson correlation for each. In Step K testing, IONIS achieved Pearson
+0.3675 vs VOACAP +0.0218.

## Training a New Model Version

Training is covered in detail in the [Training Methodology](../methodology/training.md)
page. At a high level:

1. Export training data: `gold_v6.csv` from ClickHouse (see [Gold Layer](../methodology/gold_layer.md))
2. Transfer to training host (M3 Ultra via DAC link)
3. Create a new version config: `versions/vNN/config_vNN.json`
4. Run training: `python train.py --config versions/vNN/config_vNN.json`
5. Validate: run `validate_vNN.py` against quality test paths

The model architecture (IonisGate) and its six non-negotiable constraints
are documented in the [IonisGate Architecture](../architecture/ionisgate.md) page.
