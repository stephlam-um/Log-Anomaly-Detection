# Log Anomaly Detection

> [!WARNING]
> **This repository is archived and no longer actively maintained.**
>
> I ran into some fundamental issues with the CSIC 2010 dataset midway through — HTTP requests are split across per-parameter rows rather than one row per request, and the ~55% anomaly rate breaks the assumptions that unsupervised methods like Isolation Forest rely on. Continuing didn't feel worth it.
>
> More importantly, I realised the question I actually wanted to answer was different. From what I've seen in a SOC environment, the bottleneck isn't whether the model catches the attack — it's whether the analyst can trust and act on the alert. Most detection engineering projects stop at the F1 score. I would like to go one step further into the part that actually matters operationally.
>
> The follow-on project keeps the groundwork from here (feature engineering, model comparison, evaluation pipeline) and builds an explainability layer on top. See [Actionable-CF-NIDS](https://github.com/stephlam-um/Actionable-CF-NIDS) if you're curious where this went.

Detecting HTTP attacks using unsupervised anomaly detection and session-level sequence graphs, validated on real labeled data.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-orange?style=flat-square&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## What it does

- Parses raw Apache, nginx, and syslog logs into structured feature vectors
- Detects anomalous entries using Isolation Forest (unsupervised)
- Evaluates against labeled ground truth data (CSIC 2010 HTTP dataset)
- Compares Isolation Forest, LOF, and rule-based detection side-by-side
- Extends detection with session-level graphs — modeling request sequences per client, not just individual events

---

## Why it matters

Standard anomaly detectors score each log entry in isolation. A brute-force attack is 6 identical `POST /login` 401s — individually, they look consistent and score as *normal*. The model misses it entirely.

Session graphs fix this. By modeling the sequence of requests from each client (what comes after what, how repetitive, how varied), attacks that look benign per-entry become visible as patterns.

Motivated by SOC experience: high-volume alert triage requires automation, but automation without context produces too many false positives. This project explores the gap between the two.

See [comparison_analysis.md](comparison_analysis.md) for a concrete demonstration of where per-entry detection succeeds and where it fails.

---

## How it works

**Current pipeline (Apache/syslog logs):**
```
Raw Logs → Ingest → Parse → Feature Extraction → Isolation Forest → Anomaly Scores → Output
```

**CSIC evaluation pipeline (in progress):**
```
CSIC CSV → Preprocess → HTTP Feature Extraction → Baseline Models → Evaluate
                                                         ↓
                                              Session Grouping → Transition Graphs
                                                         ↓
                                              Graph Features → Re-evaluate → Delta
```

---

## Quickstart (Apache/syslog pipeline)

```bash
git clone https://github.com/stephlam-um/Log-Anomaly-Detection.git
cd Log-Anomaly-Detection
pip install -r requirements.txt

# Run on sample Apache logs
python main.py --input data/sample_logs/apache_sample.log --format apache

# Run on nginx logs with custom config
python main.py --input /var/log/nginx/access.log --format nginx --config config.yaml
```

Output is written to `output/`: score distribution plot, timeline, and `flagged_events.csv`.

---

## Project structure

```
log-anomaly-detection/
├── src/
│   ├── ingestor.py        # Log file reader (streaming + batch)
│   ├── parser.py          # Regex-based parsing (Apache, nginx, syslog)
│   ├── features.py        # Feature extraction (9 numeric features)
│   ├── detector.py        # Isolation Forest wrapper
│   ├── visualizer.py      # Score plots and CSV export
│   └── evaluator.py       # Precision/recall/F1/ROC-AUC (in progress)
├── data/
│   ├── sample_logs/       # Sample logs for testing
│   └── raw/               # CSIC 2010 CSV (not committed)
├── tests/
│   ├── test_parser.py
│   └── test_detector.py
├── docs/
│   └── design_notes.md    # Architecture decisions and trade-offs
├── comparison_analysis.md # Anomaly vs. rule-based detection comparison
├── building plan.md       # Phased development plan
├── config.yaml
└── main.py
```

---

## Detection approach comparison

See [comparison_analysis.md](comparison_analysis.md) for a side-by-side analysis of Isolation Forest vs. rule-based detection on the same log data.

Key finding: Isolation Forest flagged a large PDF download (size outlier) while missing a brute-force login attack — because repeated identical requests look *consistent*, and consistency reads as normal to the model. This is the core limitation Stage 2 addresses.

---

## Roadmap

### Stage 1 — Baseline evaluation on labeled data (in progress)
Validate the existing Isolation Forest against CSIC 2010 HTTP dataset (223k labeled HTTP requests, attack types: SQL injection, XSS, path traversal, parameter tampering).

Compare three approaches:
| Method | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|
| Rule-based | — | — | — | — |
| Isolation Forest | — | — | — | — |
| LOF | — | — | — | — |
| Random Forest (supervised upper bound) | — | — | — | — |

### Stage 2 — Session graphs
Add session-level sequence context. Group requests by client, build directed transition graphs, extract graph features (session length, rare transitions, self-loop depth, entropy), and measure improvement over per-entry detection.

Expected: improved recall on multi-step attacks (brute-force, scanning sequences) with modest precision cost.

---

## Stack

Python, scikit-learn, pandas, networkx

---

## License

MIT — see [LICENSE](LICENSE)
