# Log Anomaly Detection

A practical log analysis tool for identifying anomalous patterns in system and network logs.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-orange?style=flat-square&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## What it does

- Parses logs and extracts features (frequency, timing, entropy patterns)
- Uses Isolation Forest to detect anomalies
- Produces simple, actionable output for alert triage

---

## Why it matters

Built from observations during SOC experience—anomaly detection handles high-volume alert triage better than manual rules, but lacks context. This project explores both anomaly-based and rule-based approaches, with future investigation into provenance-based detection (tracking event relationships rather than isolated patterns).

**Key learning:** Effective detection requires understanding trade-offs between automation and interpretability.

---

## How it works

```
Raw Logs → Parsing → Feature Extraction → Isolation Forest → Anomaly Scores → Output
```

1. **Ingestion** – Reads raw server/network logs (Apache, nginx, syslog)
2. **Parsing** – Extracts structured fields (IP, timestamp, status code, bytes, method)
3. **Feature Engineering** – Constructs numeric feature vectors (request rate, error ratio, byte volume, hour-of-day)
4. **Isolation Forest** – Trains an unsupervised model; assigns anomaly scores to each log entry
5. **Output** – Score distribution plot, timeline, and CSV of flagged events for analyst review

---

## Quickstart

```bash
git clone https://github.com/stephlam-um/Log-Anomaly-Detection.git
cd Log-Anomaly-Detection
pip install -r requirements.txt

# Run on sample data
python main.py --input data/sample_logs/apache_sample.log --format apache

# Run with custom config
python main.py --input /var/log/nginx/access.log --format nginx --config config.yaml
```

Output is written to `output/`: score distribution plot, timeline, and `flagged_events.csv`.

---

## Detection approach comparison

See [comparison_analysis.md](comparison_analysis.md) for a side-by-side comparison of anomaly-based vs. rule-based detection on the same log data — including where each approach succeeds and where it falls short.

---

## Project structure

```
log-anomaly-detection/
├── src/
│   ├── ingestor.py      # Log file reader
│   ├── parser.py        # Regex-based parsing (Apache, nginx, syslog)
│   ├── features.py      # Feature extraction (9 numeric features)
│   ├── detector.py      # Isolation Forest wrapper
│   └── visualizer.py    # Score plots and CSV export
├── data/
│   └── sample_logs/     # Sample logs for testing
├── tests/
│   ├── test_parser.py
│   └── test_detector.py
├── docs/
│   └── design_notes.md  # Architecture decisions and trade-offs
├── comparison_analysis.md  # Anomaly vs. rule-based detection comparison
├── config.yaml
└── main.py
```

---

## Stack

Python, scikit-learn, pandas

---

## Future direction

The main limitation of anomaly-based detection is that it treats each log entry independently. A single unusual request may not be anomalous in isolation—but as part of a sequence (recon → exploitation → lateral movement), it becomes highly significant.

Provenance-based detection addresses this by tracking *how events are connected*, not just whether individual events look unusual. Inspired by discussions with Prof. Chen Ang (UMich), this is the direction I want to explore next.

---

## License

MIT — see [LICENSE](LICENSE)
