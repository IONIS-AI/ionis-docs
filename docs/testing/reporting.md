# Reporting Issues

Found a path where the model disagrees with your on-air experience? That's
exactly the feedback we need.

## What to Report

### Test Suite Failures

If `ionis-validate test` reports any failures:

1. Run `ionis-validate info` and include the full output
2. Copy the failing test output (test ID, expected vs actual values)
3. Note your platform (OS, Python version, CPU/GPU)

### Prediction Disagreements

If `ionis-validate predict` gives a result that contradicts your operating
experience:

1. The exact command you ran (all arguments)
2. What you expected and why (e.g., "I work this path on FT8 every evening")
3. Your station details if relevant (antenna, power class)
4. The approximate date and conditions when you observed the path
5. Current solar conditions if you have them (SFI, Kp)

### Custom Path Results

If you have a JSON file with `expect_open` assertions that fail:

1. Attach the JSON file
2. Include the command output
3. Add notes on which paths you're most confident about

## Where to Report

File an issue on the ionis-training repository:

**[https://github.com/IONIS-AI/ionis-training/issues](https://github.com/IONIS-AI/ionis-training/issues)**

Use the title format: `[V20 Beta] <brief description>`

Examples:

- `[V20 Beta] 160m polar path predicted open during Kp 7`
- `[V20 Beta] TST-100 test 14 fails on Rocky 9.7 aarch64`
- `[V20 Beta] Custom paths — 10m EU consistently over-predicted`

## What Happens Next

Every beta test result gets reviewed. Paths where the model consistently
disagrees with experienced operators become training data for the next version.

Your custom path JSON files are particularly valuable — they represent
real-world ground truth that no public dataset captures.
