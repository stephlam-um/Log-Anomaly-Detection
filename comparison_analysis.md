# Detection Approach Comparison: Anomaly-Based vs. Rule-Based

This document compares two detection strategies applied to the same Apache log sample (`data/sample_logs/apache_sample.log`). The goal is not to declare a winner but to understand the trade-offs — which matters more than picking the "best" algorithm.

---

## The sample log

The sample contains 20 entries with three distinct attack patterns embedded:

| Pattern | IPs / Entries | What it looks like |
|---|---|---|
| Brute-force login | `192.168.1.99`, 6 entries | Rapid `POST /api/login` returning 401 at 2:47am |
| Web scanner (Nikto) | `10.0.0.200`, 3 entries | `GET /etc/passwd`, `/.env`, `/wp-admin/` returning 404 at 3:15am |
| Server errors | `192.168.1.16/17`, 2 entries | `GET /api/data` returning 500 |

---

## Rule-based detection

Rules are explicit heuristics written by a human. Applied to this log:

```
Rule 1: Flag any IP with 3+ failed auth attempts (status 401) in a session
Rule 2: Flag requests to known-sensitive paths (/etc/passwd, /.env, /wp-admin/)
Rule 3: Flag any 500-series status code
```

**Results on sample log:**

| Rule | Entries flagged | Correct? |
|---|---|---|
| Rule 1 (brute-force) | 6 entries from `192.168.1.99` | Yes |
| Rule 2 (path scanning) | 3 entries from `10.0.0.200` | Yes |
| Rule 3 (server errors) | 2 entries from `.16/.17` | Yes (but noisy in prod) |

**Strengths:**
- High precision on known patterns — zero ambiguity about *why* an entry was flagged
- Fast to implement and easy to explain to non-technical stakeholders
- No training data needed; works on day one

**Weaknesses:**
- Rules must be written for every attack pattern — unknown/novel techniques are invisible
- Path-based rules require constant maintenance as attackers change their tooling
- In production environments, rules like "any 401" generate enormous alert volume; tuning thresholds is time-consuming and environment-specific

---

## Anomaly-based detection (Isolation Forest)

Isolation Forest learns what "normal" looks like from the data and flags entries that deviate statistically.

**Results on sample log:**

With `contamination=0.05` (top 5% most anomalous flagged) on 20 entries → 1 entry flagged.

The model flags `192.168.1.13 GET /reports/q1.pdf` (204,800 bytes) — the large PDF download. This is the statistical outlier in feature space because `bytes_transferred` and `log_bytes` are the dominant features, and 204KB is a 100x outlier relative to all other requests in the sample.

The brute-force entries (`192.168.1.99`) and scanner (`10.0.0.200`) are *not* flagged at this contamination level. The brute-force requests are actually very consistent with each other (same IP, method, path, status, bytes) — that consistency makes them look *normal* to a model trained on the same data. The scanner's 404 responses and odd paths score as moderately anomalous, but not the top 5%.

This is a concrete illustration of the model's limitation: **the most statistically unusual event is not always the most security-relevant one.**

**Strengths:**
- Catches novel patterns without pre-written rules — useful for unknown attack tooling
- Handles high-volume logs automatically without manual threshold tuning per rule
- Scales well; unsupervised, so no labeled training data needed

**Weaknesses:**
- Each entry is scored in isolation — a slow brute-force (one attempt per hour from different IPs) may score as normal
- The `contamination` parameter is a hyperparameter that requires domain knowledge to set correctly; wrong values produce either too many or too few alerts
- Low interpretability: the model flags an entry as anomalous, but doesn't tell you *which* feature drove the score — analysts must investigate manually

---

## Head-to-head summary

| Dimension | Rule-based | Anomaly-based (IF) |
|---|---|---|
| Known attack patterns | High precision | Moderate (depends on features) |
| Novel/unknown attacks | Blind | Can detect if features diverge |
| False positive rate | Low for tuned rules, high for generic rules | Tunable via contamination |
| Analyst explainability | High — rule name tells you why | Low — requires feature inspection |
| Maintenance burden | High — rules need updates | Low — model adapts to new data |
| Alert volume at scale | High without careful tuning | Bounded by contamination % |

---

## The real-world problem both approaches share

Neither approach answers the question: *"Is this series of events an attack?"*

A sophisticated attacker doesn't trip a single rule or generate a single outlier. They blend in:
- Recon requests look like normal browsing
- Auth attempts are slow and distributed across IPs
- Lateral movement uses legitimate credentials

**Provenance-based detection** addresses this by tracking *event relationships* rather than scoring individual entries. If the same host that scanned `/etc/passwd` later successfully authenticated, that connection is the signal — regardless of whether either event looked anomalous in isolation. This is the direction I'm interested in exploring next, inspired by research in attack graph analysis and system call provenance tracking.

---

## Takeaway for SOC environments

A practical detection stack layers both approaches:

1. **Rules** for high-confidence, low-noise patterns you know about (brute-force thresholds, known-bad IPs, specific malware signatures)
2. **Anomaly detection** as a catch-all for unusual patterns that rules miss
3. **Analyst review** of anomaly-flagged events — automation narrows the field, humans make the call

The goal is reducing the triage burden, not eliminating human judgment.
