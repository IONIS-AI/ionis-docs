# Data Privacy and GDPR Statement

## Our Position

IONIS is a scientific research project that studies ionospheric propagation
patterns using publicly available amateur radio observations. **We have zero
interest in personal data. We study propagation paths between grid squares,
not the operators who generated them.**

There is no commercial motive behind IONIS. There is no monetization plan. There
is no startup. This is real research, built to provide a badly needed tool for
the public and the greater ham radio community at large.

All IONIS tools, models, and research results are free to the public under
the GNU General Public License v3 (GPLv3). We credit every data source, share
our insights back to the community, and redistribute only derived works
(models and aggregated signatures) — never raw data.

---

## Data Sources and Authorization

All source data used by IONIS is publicly available, provided by community
organizations for public use, and downloaded with the explicit or implied
consent of the data providers.

| Source | Authorization | Policy |
|--------|--------------|--------|
| **WSPRNet** | Public archive, no restrictions | "The data collected are available to the public through this site" |
| **Reverse Beacon Network** | Public, share results back (voluntary) | "Data from the RBN are freely available for study and analysis" |
| **CQ Contest Logs** | Entrant consent to public posting | CQ WW Rules Section XIII: entrants "agreed the log entry may be made open to the public" |
| **ARRL Contest Logs** | Publicly posted, no restriction found | Logs published at contests.arrl.org since 2018; no terms prohibiting research use |

Full details: [WSPRNet Downloads](https://www.wsprnet.org/drupal/downloads) |
[RBN Raw Data](https://www.reversebeacon.net/raw_data/) |
[CQ WW Public Logs](https://cqww.com/publiclogs/) |
[ARRL Public Logs](https://contests.arrl.org/publiclogs.php)

---

## GDPR Compliance

### Why Callsigns Appear in Our Pipeline

Amateur radio callsigns appear in the bronze (raw ingest) and silver (enrichment)
layers of our data pipeline for one reason only: **to link an observation to a
geographic grid square** when the source record does not include one directly (e.g.,
Reverse Beacon Network spots contain no grid square — only a callsign and DXCC
prefix). This is the Rosetta Stone's sole function.

By the time data reaches the gold layer (training-ready, model-facing), **all
callsigns have been removed**. The model receives only: grid-pair, band, time of
day, month, solar flux index (SFI), geomagnetic index (Kp), distance, and bearing.
No callsign, no name, no address, no personal identifier of any kind.

### GDPR Analysis

We have assessed our data processing against the EU General Data Protection
Regulation (GDPR) and believe our use is compliant on multiple independent grounds:

**1. Anonymization (Recital 26)**

GDPR Recital 26 states: "The principles of data protection should therefore not
apply to anonymous information, namely information which does not relate to an
identified or identifiable natural person or to personal data rendered anonymous
in such a manner that the data subject is not or no longer identifiable. This
Regulation does not therefore concern the processing of such anonymous information,
including for statistical or research purposes."

Our gold-layer output is anonymous by design. Callsigns are stripped. Grid squares
are 4-character Maidenhead locators representing areas of approximately
100 km x 200 km — far too coarse to identify any individual. The model's input
and output contain no personal data whatsoever.

**2. Publicly Available Data, Voluntarily Disclosed**

Every observation in our dataset was voluntarily made public by the operator:

- **WSPR beacons** are transmitted over public radio frequencies specifically to be
  received and reported by anyone. Operators configure their software to upload
  spots to WSPRNet's public database. This is a deliberate, affirmative act of
  publication.
- **RBN spots** are machine-decoded from public radio transmissions. CW and RTTY
  signals are broadcast on public amateur radio frequencies. The Reverse Beacon
  Network provides these observations as a public service.
- **Contest logs** are submitted by operators who explicitly consent to public
  posting. CQ WW rules require entrants to agree their "log entry may be made
  open to the public" as a condition of participation. ARRL posts submitted logs
  publicly at contests.arrl.org.

Amateur radio is, by its nature, a public service. ITU Radio Regulations and
national licensing authorities (FCC 47 CFR 97.119, Ofcom, BNetzA, etc.) **require**
operators to identify themselves with their callsign during every transmission.
Callsigns are broadcast over the air, published in national licensing databases,
and printed in callbooks that have been publicly available for over 70 years.
There is no expectation of privacy for amateur radio callsigns.

**3. Scientific Research Purpose (Article 89)**

GDPR Article 89 provides safeguards and derogations for processing personal data
for scientific or historical research purposes and statistical purposes, provided
appropriate technical and organizational measures are in place — particularly the
principle of data minimization. Our pipeline exemplifies this:

- Callsigns are used only where necessary (grid resolution in silver layer)
- Callsigns are stripped as early as possible (before gold layer)
- The model never receives any personal identifier
- We do not attempt to identify, profile, or contact any individual
- Our purpose is exclusively scientific: understanding ionospheric propagation

**4. Data Minimization in Practice**

Our medallion architecture enforces data minimization structurally:

| Layer | Contains Callsigns? | Purpose |
|-------|-------------------|---------|
| **Bronze** (raw ingest) | Yes — as received from source | Immutable archive, never modified |
| **Silver** (enriched) | Yes — used for grid resolution | Cross-source validation, temporal grid matching |
| **Gold** (training-ready) | **No** | Aggregated signatures: grid-pair, band, time, solar, SNR |

The callsign does its job in the silver layer (linking observations to grids) and
is permanently left behind. By the time any data touches the neural network, it
contains only physics — no person.

### What We Do Not Do

- We do **not** collect data directly from individuals
- We do **not** attempt to identify, track, or profile any operator
- We do **not** correlate callsigns with names, addresses, or other PII
- We do **not** redistribute raw data containing callsigns
- We do **not** use callsign data for any commercial purpose
- We do **not** store callsign data beyond what the public source already provides
- We do **not** contact operators based on data in our pipeline

### What We Redistribute

We redistribute only:

- **Open source tools** (GPLv3) — ingesters, parsers, training scripts
- **Trained model weights** — callsign-free, anonymous
- **Aggregated signature vectors** — callsign-free, anonymous
- **Published research results** — shared with data providers and the public

We do **not** redistribute raw WSPR spots, RBN spots, or contest logs. Anyone
wanting the source data should download it from the original providers.

---

## Contact

Questions about our data handling practices can be directed to:

- **Greg Beam, KI7MT** — Project lead
- **Email**: See QRZ.com listing for KI7MT

---

*Last updated: 2026-02-08*
*Status: Living Document*
