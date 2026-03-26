# 🔍 Log Anomaly Detection

> ML-based log analysis tool using Isolation Forest to detect anomalous patterns in server and network logs.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-orange?style=flat-square&logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Motivation

After 1.5 years working in a live SOC environment, I repeatedly ran into the same bottleneck: analysts spending hours manually triaging alerts, many of which turned out to be noise. Most SIEM tools either flood you with false positives or require expensive rule-writing to reduce them.

This project is my attempt to apply unsupervised ML — specifically Isolation Forest — to automatically surface genuinely anomalous log patterns, reducing manual triage overhead and helping analysts focus on what actually matters.

---

## How It Works

```
Raw Logs → Parsing → Feature Extraction → Isolation Forest → Anomaly Scores → Visualization
```

1. **Ingestion** – Reads raw server/network logs (Apache, syslog, custom formats)
2. **Parsing** – Extracts structured fields (IP, timestamp, status code, bytes, method, etc.)
3. **Feature Engineering** – Constructs numeric feature vectors (request rate, error ratio, byte volume, hour-of-day, etc.)
4. **Isolation Forest** – Trains an unsupervised model; assigns anomaly scores to each log window
5. **Visualization** – Plots anomaly score timelines, highlights flagged events, exports reports

---

## Project Structure

```
log-anomaly-detection/
├── src/
│   ├── ingestor.py          # Log file reader & format dispatcher
│   ├── parser.py            # Regex-based log parsing (Apache, syslog, generic)
│   ├── features.py          # Feature extraction & engineering
│   ├── detector.py          # Isolation Forest model wrapper
│   └── visualizer.py        # Matplotlib-based plotting & reporting
├── data/
│   └── sample_logs/         # Anonymized sample log files for testing
├── notebooks/
│   └── exploration.ipynb    # EDA & model tuning experiments
├── tests/
│   ├── test_parser.py
│   ├── test_features.py
│   └── test_detector.py
├── docs/
│   └── design_notes.md      # Architecture decisions & open questions
├── requirements.txt
├── config.yaml              # Tunable parameters (contamination rate, window size, etc.)
└── main.py                  # CLI entry point
```

---

## Quickstart

```bash
# Clone & install
git clone https://github.com/YOUR_USERNAME/log-anomaly-detection.git
cd log-anomaly-detection
pip install -r requirements.txt

# Run on sample data
python main.py --input data/sample_logs/apache_sample.log --format apache

# Run with custom config
python main.py --input /var/log/nginx/access.log --format nginx --config config.yaml
```

---

## Current Status

| Component         | Status        |
|-------------------|---------------|
| Log ingestion     | ✅ Done        |
| Apache parser     | ✅ Done        |
| Syslog parser     | 🔧 In progress |
| Feature extraction| ✅ Done        |
| Isolation Forest  | ✅ Done        |
| Visualization     | 🔧 In progress |
| Tests             | 🔧 In progress |
| Docs              | 📝 Planned     |

---

## Tech Stack

- **Python 3.10+**
- **scikit-learn** – Isolation Forest implementation
- **pandas** – Log data manipulation
- **matplotlib / seaborn** – Anomaly visualization
- **PyYAML** – Config management

---

## Roadmap

- [ ] Add support for Windows Event Log (EVTX) parsing
- [ ] Sliding-window aggregation for time-series anomaly detection
- [ ] Interactive HTML report output
- [ ] Baseline comparison against LOF and One-Class SVM
- [ ] Docker container for easy deployment

---

## Background

Isolation Forest works by randomly partitioning the feature space using binary trees. Anomalous points — which tend to be sparse and different — require fewer splits to isolate, yielding lower anomaly scores. This makes it well-suited for high-dimensional, unlabeled log data where "normal" behaviour is hard to define explicitly.

---

## License

MIT — see [LICENSE](LICENSE)
