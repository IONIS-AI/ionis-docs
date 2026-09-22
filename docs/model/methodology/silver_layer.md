# Silver Layer — retired 2026-09-22

!!! danger "There is no silver layer. The pipeline is `bronze → gold`."
    `wspr.silver` and `wspr.v_quality_distribution` were dropped on 2026-09-22. This page
    is kept because the layer was documented for months and the links to it are load-bearing;
    it now records what happened rather than instructing anyone to build it.

## What was found

The 2026-09-22 data audit found `wspr.silver` holding **zero rows**, against documentation —
this page included — that advertised 4.4 billion embeddings across 41 GiB.

It was probably not always empty. The QA table below recorded a clean-slate rebuild on
2026-02-07 producing 4,430,000,000 rows. ClickHouse's `part_log` and `query_log` retain only
back to 2026-09-06, so **when or how it emptied cannot be established.**

That uncertainty is the finding, not a gap in it. A table can shed four billion rows and go
unnoticed for seven months only if nothing reads it.

## Why nothing read it

| | |
|---|---|
| **Written by** | `bulk-processor`, a CUDA job in `ionis-cuda`. Not packaged in any RPM, no systemd unit, runs only by hand. |
| **Read by** | `wspr.v_quality_distribution` — a materialized view that was also empty. |
| **Used to build gold** | **No.** All fourteen populate scripts read `wspr.bronze` directly. `populate_stratified.sh` and `populate_continuous.sh` both join `wspr.bronze` to `solar.bronze`; `gold_v6` derives from `gold_continuous`. Not one script references silver. |

So the `bronze → silver → gold` medallion chain in the architecture documents described a
design. The build is `bronze → gold`, and the gold tables were never affected.

## What was removed

| Object | Where |
|---|---|
| `wspr.silver` | dropped from ClickHouse |
| `wspr.v_quality_distribution` | dropped from ClickHouse |
| `src/08-model_features.sql` | deleted from `ionis-core` — `src/*.sql` is globbed by the `Makefile` **and** by `ionis-core.spec`, so leaving the file would have recreated the table on the next apply |
| `src/09-quality_distribution_mv.sql` | deleted from `ionis-core`, same reason |
| `sql/01-model_features.sql` | in `ionis-cuda`, every statement commented out — reference schema only |

**`03-solar_silver.sql` was not touched.** Despite the name it creates `solar.v_daily_indices`,
a view over `solar.bronze` that exists and is in active use. The filename is a leftover from the
retired concept and has nothing to do with `wspr.silver`.

## The CUDA engine is kept

`ionis-cuda` computes real float4 embeddings and the code is sound. What it lacks is a
*consumer*. Before it runs again, decide what reads its output — not merely where to put it. An
unconsumed table is exactly how this one sat empty without anyone noticing.

## Historical QA record

Kept for provenance. This is the run that reported 4.43B rows, and the claim this page carried
until it was checked:

```text
Clean-slate rebuild on 9975WX (2026-02-07)

Table                           Rows            Time
------------------------------  --------------  ---------
wspr.silver                     4,430,000,000   ~45 min
wspr.signatures_v2_terrestrial     93,600,000   3m31s
v_quality_distribution              ~6,100,000   (auto)
```

`wspr.signatures_v2_terrestrial` is real and current — 93.60M rows as of 2026-09-22. It is built
from `wspr.signatures_v1`, which is built from `wspr.bronze`. It never involved silver.

## Where to look instead

- **[Bronze Stack](bronze_stack.md)** — the raw ingest tables
- **[Gold Layer](gold_layer.md)** — the training tables, built from bronze
- **[Aggregated Signatures](step_f_signatures.md)** — the 115:1 compression that does the work
  this layer was supposed to do
- **`ionis-core/docs/DATA-DICTIONARY.md`** — every table in the lab: source, writer, readers,
  derivation. Authoritative; if a document disagrees with it, that document is wrong.
