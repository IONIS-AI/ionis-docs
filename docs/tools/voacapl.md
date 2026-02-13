# Validation: VOACAP

!!! note "External Tool — Local Build Only"
    `voacapl` is **not part of the IONIS project**. It is an independent HF
    propagation prediction engine maintained by
    [James Watson, HZ1JW](https://github.com/jawatson/voacapl). We build it
    locally as a validation baseline to compare IONIS predictions against.

## voacapl

VOACAP (Voice of America Coverage Analysis Program) is the NTIA/ITS professional
HF propagation prediction engine, originally developed for the Voice of America.
`voacapl` is the Linux port compiled with GFortran, maintaining the unchanged
original prediction algorithms.

IONIS uses VOACAP as an independent baseline: the same 1M contest QSO paths
validated by `validate_v12.py` are run through VOACAP, and recall is compared
side by side.

```text
voacapl - release 0.7.5
```

### Building from Source

**Requirements:**

- GFortran compiler
- GNU Autotools (automake, autoconf)
- ~50 MB disk for the `itshfbc` data directory

**Install GFortran (Rocky Linux 9):**

```bash
sudo dnf install -y gcc-gfortran
```

**Build and install:**

```bash
git clone https://github.com/jawatson/voacapl.git
cd voacapl
autoreconf -i
./configure
make -j$(nproc)
sudo make install
```

**Initialize data directory:**

```bash
makeitshfbc
```

This creates `~/itshfbc/` containing ionospheric coefficients (CCIR/URSI),
antenna models, and propagation data tables. The engine reads from this
directory at runtime.

### Usage

**Point-to-point prediction:**

```bash
voacapl ~/itshfbc                              # default (voacapx.dat -> voacapx.out)
voacapl ~/itshfbc input.dat output.out         # custom files
voacapl ~/itshfbc batch                        # batch mode (reads voacap.cir)
```

!!! warning "File arguments are relative to `run/`"
    The input and output filenames are resolved relative to the `run/`
    subdirectory inside the itshfbc root. So `voacapl ~/itshfbc input.dat output.out`
    reads `~/itshfbc/run/input.dat` and writes `~/itshfbc/run/output.out`.
    This is a Fortran heritage detail — the engine always operates inside `run/`.

**Options:**

```text
  -s, --silent           Reduce console output
  -v                     Display version
  --run-dir DIR          Specify input/output directory
  --absorption-mode M    Override absorption model (W, I, A, or a)
```

### Input File Format

VOACAP uses a text-based "card deck" format (Fortran heritage). Each line is a
card specifying one parameter. A minimal input file for a single path prediction:

```text
COEFFS    CCIR
TIME          1   24    1    1
MONTH      2024 6.00
SUNSPOT    120.
LABEL     TX Site                 RX Site
CIRCUIT   46.50N   107.00W    48.50N    12.00E  S     0
SYSTEM       1. 145. 0.10  90. 73.0 3.00 0.10
FPROB      1.00 1.00 1.00 0.00
ANTENNA       1    1    2   30     0.000[default/const17.voa  ]  0.0    0.0100
ANTENNA       2    2    2   30     0.000[default/const17.voa  ]  0.0    0.0100
FREQUENCY 14.10 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
METHOD       30    0
EXECUTE
QUIT
```

**Key cards:**

| Card | Purpose |
|------|---------|
| COEFFS | Ionospheric coefficient set (CCIR or URSI88) |
| TIME | Start hour, end hour, increment, time reference (1=UT) |
| MONTH | Year and month (mm.dd format) |
| SUNSPOT | Smoothed sunspot number for the prediction period |
| CIRCUIT | TX lat/lon, RX lat/lon, path type (S=short) |
| SYSTEM | Power(kW), noise(dBW), min angle, req reliability(%), req SNR, MP tol, delay tol |
| ANTENNA | TX/RX antenna model, beam direction, and transmit power (kW) |
| FREQUENCY | Up to 11 frequencies in MHz |
| METHOD | Prediction method (30 = complete system performance) |

### Output Fields

VOACAP produces hourly predictions. Fields used for IONIS comparison:

| Field | Description |
|-------|-------------|
| MUF | Maximum usable frequency for the path |
| MUFday | Fraction of days the MUF supports the frequency |
| SNR | Signal-to-noise ratio (dB) |
| REL | Circuit reliability (fraction of days the link works) |
| S DBW | Signal power at receiver (dBW) |
| LOSS | Total path loss (dB) |
| MODE | Propagation mode (F2F2, E, etc.) |

### IONIS vs VOACAP Comparison

Both systems predict whether an HF path is open for a given band, time, and
solar condition. The comparison methodology:

1. Load the 1M contest QSO paths from `validation.step_i_paths` (ClickHouse)
2. Group by unique circuit (TX, RX, freq, year, month, SSN) — ~965K circuits
3. Generate VOACAP input cards (one per circuit, all 24 hours)
4. Run `voacapl` in parallel (32 workers, each with its own `itshfbc/` copy)
5. Parse SNR/REL/MUFday from Method 30 output
6. Apply mode thresholds: DG/CW = -22 dB, RY/PH = -21 dB
7. INSERT results into `validation.step_i_voacap` (ClickHouse)
8. Compare: `SELECT ... FROM step_i_paths p JOIN step_i_voacap v USING (...)`

### Batch Runner

The script `voacap_batch_runner.py` automates the full VOACAP validation run.

**Location:** `ionis-training/scripts/voacap_batch_runner.py`

**Prerequisites:**

- `voacapl` installed at `/usr/local/bin/voacapl`
- `~/itshfbc/` initialized via `makeitshfbc`
- `validation.step_i_paths` loaded in ClickHouse (1M rows)
- `validation.step_i_voacap` table created (DDL: `16-validation_step_i.sql`)

**Run a small test (1000 rows, dry run):**

```bash
python3 voacap_batch_runner.py --sample 1000 --workers 8 --dry-run
```

**Full 1M run (32 workers):**

```bash
python3 voacap_batch_runner.py --workers 32
```

**Options:**

```text
  --workers N    Parallel workers (default: 32)
  --host HOST    ClickHouse host (default: localhost)
  --port PORT    ClickHouse native port (default: 9000)
  --sample N     Process only N rows (0 = all)
  --dry-run      Skip ClickHouse INSERT
  --work-dir DIR Worker directory base (default: /tmp/voacap_work)
```

**How parallelization works:**

Each worker gets its own `itshfbc/` directory tree. Large read-only directories
(`coeffs/`, `antennas/`) are symlinked; writable directories (`run/`, `database/`)
are copied. Each worker writes its input card to `run/voacapx.dat`, invokes
`voacapl`, and parses `run/voacapx.out` independently. On the 9975WX (32C/64T),
this achieves ~370 circuits/sec — the full 965K circuits complete in ~43 minutes.

### Limitations

- VOACAP predicts for a **monthly median** SSN, not a specific date — daily
  variability is not captured
- Antenna models affect absolute signal levels but not band-open/closed decisions
- The original algorithms date to the 1980s and do not account for modern
  understanding of sporadic-E or grey line propagation
- Path length limit: ~52 characters for the `itshfbc` directory path (DOS legacy)

### References

- [voacapl GitHub](https://github.com/jawatson/voacapl) — source code and releases
- [VOACAP Quick Guide](https://www.voacap.com/) — online VOACAP interface by OH6BG
- [voacapl Wiki](https://github.com/jawatson/voacapl/wiki) — input card documentation
