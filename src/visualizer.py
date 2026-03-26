"""
visualizer.py — Matplotlib-based plotting and report export.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path


COLORS = {
    "normal": "#4A90D9",
    "anomaly": "#E84040",
    "score_line": "#2C2C2C",
    "grid": "#E5E5E5",
    "bg": "#FAFAFA",
}


class AnomalyVisualizer:
    def __init__(self, output_dir: str = "output/"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ── Anomaly Score Distribution ────────────────────────────────────────────

    def plot_anomaly_scores(self, df: pd.DataFrame):
        """Histogram of anomaly scores, split by normal vs anomalous."""
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor(COLORS["bg"])
        ax.set_facecolor(COLORS["bg"])

        normal = df[df["anomaly"] == 1]["anomaly_score"]
        anomalous = df[df["anomaly"] == -1]["anomaly_score"]

        ax.hist(normal, bins=40, alpha=0.7, color=COLORS["normal"], label="Normal")
        ax.hist(anomalous, bins=40, alpha=0.8, color=COLORS["anomaly"], label="Anomaly")

        ax.set_xlabel("Isolation Forest Score", fontsize=12)
        ax.set_ylabel("Count", fontsize=12)
        ax.set_title("Anomaly Score Distribution", fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(axis="y", color=COLORS["grid"], linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)

        path = self.output_dir / "score_distribution.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"    Saved: {path}")

    # ── Timeline Plot ─────────────────────────────────────────────────────────

    def plot_timeline(self, df: pd.DataFrame):
        """Anomaly score over time with flagged events highlighted."""
        if "timestamp" not in df.columns or df["timestamp"].isna().all():
            print("    [!] No timestamp data — skipping timeline plot.")
            return

        plot_df = df.dropna(subset=["timestamp"]).copy()
        plot_df["timestamp"] = pd.to_datetime(plot_df["timestamp"], utc=True, errors="coerce")
        plot_df = plot_df.sort_values("timestamp")

        fig, ax = plt.subplots(figsize=(14, 5))
        fig.patch.set_facecolor(COLORS["bg"])
        ax.set_facecolor(COLORS["bg"])

        ax.plot(
            plot_df["timestamp"],
            plot_df["anomaly_pct"],
            color=COLORS["score_line"],
            linewidth=0.8,
            alpha=0.6,
            label="Anomaly score",
        )

        flagged = plot_df[plot_df["anomaly"] == -1]
        ax.scatter(
            flagged["timestamp"],
            flagged["anomaly_pct"],
            color=COLORS["anomaly"],
            s=20,
            zorder=5,
            label=f"Flagged ({len(flagged)})",
        )

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
        fig.autofmt_xdate()
        ax.set_ylabel("Anomaly Score (normalised)", fontsize=12)
        ax.set_title("Anomaly Score Timeline", fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(color=COLORS["grid"], linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)

        path = self.output_dir / "timeline.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"    Saved: {path}")

    # ── CSV Export ────────────────────────────────────────────────────────────

    def export_flagged(self, df: pd.DataFrame):
        """Write flagged anomaly rows to a CSV for analyst review."""
        flagged = df[df["anomaly"] == -1].sort_values("anomaly_score", ascending=True)
        path = self.output_dir / "flagged_events.csv"
        flagged.to_csv(path, index=False)
        print(f"    Saved: {path}  ({len(flagged)} rows)")
