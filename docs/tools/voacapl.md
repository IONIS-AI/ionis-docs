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
head-to-head.

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
voacapl ~/itshfbc                              # default input/output
voacapl ~/itshfbc input.dat output.out         # custom files
voacapl ~/itshfbc batch                        # batch mode
```

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
| SYSTEM | Min angle, required reliability, power, SNR threshold |
| ANTENNA | TX/RX antenna model files and gain |
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

1. Export the 1M contest QSO paths from `validate_v12.py`
2. Convert each path to VOACAP input format (grid → lat/lon, band → freq,
   date → month + SSN from `solar.bronze`)
3. Run through `voacapl` in batch mode
4. Score recall: did VOACAP predict "band open" when a real QSO occurred?
5. Compare VOACAP recall against IONIS recall (90.42%)

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
