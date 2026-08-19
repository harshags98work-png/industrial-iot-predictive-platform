# Machine-Learning Workflow

## Baseline

The trainer creates 5,000 synthetic normal-operation samples for four signals:

- temperature in degrees Celsius;
- vibration velocity in millimeters per second;
- motor current in amperes;
- pressure in bar.

A scikit-learn pipeline standardizes features and trains an `IsolationForest` with a fixed seed. The container writes the fitted pipeline and a JSON metadata file to a named Docker volume. Collectors load the same artifact and persist the model version with every score.

## Interpretation

Isolation Forest is useful here because the demonstration assumes abundant normal data and limited fault labels. Its decision function is a relative abnormality score; it is not a probability of failure or remaining useful life. The explanation adds transparent engineering-limit cues when temperature, vibration, current, or pressure crosses a simple threshold, but those cues do not replace the multivariate model.

## Honest limitations

- Training and evaluation data are synthetic and partially generated from related distributions.
- The threshold is a demonstration setting, not optimized against maintenance cost.
- Consecutive readings are scored independently; temporal features are not modeled.
- No labeled holdout report currently measures precision, recall, false alarms, or lead time.
- A warning means “unusual relative to the baseline,” not “failure is certain.”

## Next evaluation milestone

Create separately seeded labeled scenarios for normal load changes, sensor drift, bearing wear, overheating, and pressure loss. Report precision/recall by fault type, false alarms per operating hour, and median detection lead time. Freeze the evaluation set before tuning the threshold.
