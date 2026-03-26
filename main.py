"""
main.py — CLI entry point for Log Anomaly Detection
"""

import argparse
import yaml
import sys
from pathlib import Path

from src.ingestor import LogIngestor
from src.parser import LogParser
from src.features import FeatureExtractor
from src.detector import AnomalyDetector
from src.visualizer import AnomalyVisualizer


def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Log Anomaly Detection — Isolation Forest based log analysis"
    )
    parser.add_argument("--input", required=True, help="Path to log file")
    parser.add_argument(
        "--format",
        required=True,
        choices=["apache", "nginx", "syslog", "generic"],
        help="Log format",
    )
    parser.add_argument(
        "--config", default="config.yaml", help="Path to config file"
    )
    parser.add_argument(
        "--output", default="output/", help="Directory to write output reports"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Anomaly score threshold override (default: from config)",
    )
    args = parser.parse_args()

    # Load config
    config = load_config(args.config)
    if args.threshold is not None:
        config["detector"]["contamination"] = args.threshold

    print(f"[*] Loading logs from: {args.input}")
    ingestor = LogIngestor(args.input)
    raw_lines = ingestor.read()

    print(f"[*] Parsing {len(raw_lines)} log entries (format: {args.format})")
    log_parser = LogParser(format=args.format)
    parsed_df = log_parser.parse(raw_lines)
    print(f"    Parsed {len(parsed_df)} valid entries")

    print("[*] Extracting features...")
    extractor = FeatureExtractor(config=config.get("features", {}))
    feature_df = extractor.transform(parsed_df)

    print("[*] Running Isolation Forest...")
    detector = AnomalyDetector(config=config.get("detector", {}))
    results_df = detector.fit_predict(feature_df, parsed_df)

    n_anomalies = (results_df["anomaly"] == -1).sum()
    print(f"    Detected {n_anomalies} anomalous entries out of {len(results_df)}")

    print(f"[*] Generating visualizations → {args.output}")
    Path(args.output).mkdir(parents=True, exist_ok=True)
    viz = AnomalyVisualizer(output_dir=args.output)
    viz.plot_anomaly_scores(results_df)
    viz.plot_timeline(results_df)
    viz.export_flagged(results_df)

    print("[✓] Done. Check the output/ directory for reports.")


if __name__ == "__main__":
    main()
