# Reporting Issues

Found a path where the model disagrees with your on-air experience? That's
exactly the feedback we need.

## The Easy Way: `ionis-validate report`

One command generates a complete, structured report you can paste directly
into a GitHub Issue:

```bash
# System info + full test suite results
ionis-validate report

# Include your custom path tests
ionis-validate report --custom my_paths.json

# System info only (skip test suite)
ionis-validate report --skip-tests
```

Progress prints to stderr. The report prints to stdout as markdown — copy
it, open an issue, paste it in.

```bash
# Pipe directly to clipboard (Linux)
ionis-validate report | xclip -selection clipboard

# Save to file
ionis-validate report --custom my_paths.json > report.md
```

## Where to Report

File an issue on the ionis-training repository. Structured templates guide
you through each report type:

**[https://github.com/IONIS-AI/ionis-training/issues/new/choose](https://github.com/IONIS-AI/ionis-training/issues/new/choose)**

Three templates:

| Template | When to Use |
|----------|-------------|
| **Test Suite Failure** | `ionis-validate test` reports a failure |
| **Prediction Disagreement** | Model prediction contradicts your on-air experience |
| **Custom Path Results** | Sharing results from `ionis-validate custom` |

Each template has structured fields — fill in what you can, paste the
`ionis-validate report` output in the "Full Report" field, and submit.

## What to Include

### Test Suite Failures

If `ionis-validate test` reports failures:

1. Run `ionis-validate report` and paste the full output
2. Or manually include: `ionis-validate info` output, failing test ID, expected vs actual

### Prediction Disagreements

If `ionis-validate predict` contradicts your experience:

1. The exact command you ran (all arguments)
2. What you expected and why (e.g., "I work this path on FT8 every evening")
3. Approximate date and UTC time of your observation
4. Solar conditions if you know them (SFI, Kp)
5. Station details if relevant (antenna, power class)

### Custom Path Results

If your JSON file with `expect_open` assertions has failures:

1. Run `ionis-validate report --custom your_file.json`
2. The report includes your JSON, the output, and system info — all in one paste

## What Happens Next

Every beta test result gets reviewed. Reports are tagged by model version
in GitHub Issues, so feedback flows directly into the next version's
development cycle.

Paths where the model consistently disagrees with experienced operators
become training data for the next version. Your custom path JSON files are
particularly valuable — they represent real-world ground truth that no
public dataset captures.
