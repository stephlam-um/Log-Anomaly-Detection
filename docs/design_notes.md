# Design Notes

## Why Isolation Forest?

Most log anomaly detection approaches either require labelled data (supervised) or rely on rigid thresholds (rule-based). Both are problematic in a real SOC:

- **Labelled data is rare and expensive.** Analysts rarely have the time to retrospectively label months of logs as "anomalous" or "normal."
- **Rules lag behind attackers.** By the time a rule is written, the threat has evolved.

Isolation Forest sidesteps both problems. It's unsupervised, requires no labels, and works by isolating data points using random binary trees. Anomalous points — by definition sparse and different — are easier to isolate and end up with lower scores. This is computationally cheap and scales well.

---

## Feature Engineering Decisions

### Why `log_bytes` instead of raw bytes?
Byte counts are heavily right-skewed (a few large transfers dominate). Log-transforming them makes the feature distribution more uniform and helps the model treat unusually large transfers as anomalous without being overwhelmed by normal variation.

### Why `ip_request_count`?
A brute-force or scanning attempt typically involves a single IP making far more requests than legitimate users. Encoding request volume per IP (session-level, not windowed) gives the model a strong signal for this pattern.

### Why `hour_of_day`?
SOC experience tells us that anomalous activity (scanning, exfiltration) clusters at odd hours (late night, early morning). Encoding the hour lets the model associate unusual feature combinations that occur at unusual times.

---

## Open Questions / TODOs

1. **Sliding window aggregation** — Currently features are per-row. The next step is aggregating features over fixed time windows (e.g., 5-minute buckets) to detect patterns that span multiple requests.

2. **Streaming mode** — The current implementation is batch. For live SOC use, the ingestor needs to tail a log file or consume from a queue (Kafka, syslog UDP).

3. **Contamination tuning** — `contamination` is a hyperparameter that requires domain knowledge. Need a calibration method (or interactive tool) for analysts to tune it.

4. **Model persistence** — The detector re-trains on each run. Adding `joblib` save/load support would allow training once on a baseline and running inference on new logs.

5. **Syslog parser completeness** — The current regex handles standard RFC 3164 format but not RFC 5424 (structured data). Needs extension.

---

## References

- Liu, F.T., Ting, K.M., Zhou, Z. (2008). *Isolation Forest.* ICDM 2008.
- scikit-learn IsolationForest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
