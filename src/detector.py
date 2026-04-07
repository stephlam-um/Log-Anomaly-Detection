"""
detector.py — Isolation Forest anomaly detection wrapper.

sklearn's IsolationForest returns:
  -1  → anomaly
   1  → inlier (normal)

The `score_samples` method returns the raw anomaly score;
lower (more negative) = more anomalous.

Design note:
Isolation Forest treats each log entry independently — it scores how
unusual a single feature vector looks relative to the rest of the dataset.
This works well for obvious outliers (a scanner hitting 404s at 3am), but
produces false positives for benign-but-rare events and misses multi-step
attack sequences where each individual request looks unremarkable.

Future: provenance-based detection would track event relationships (e.g.,
the same IP doing recon → auth failures → data access) rather than scoring
entries in isolation. That context is what separates noise from real signal.
"""

from typing import Optional

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnomalyDetector:
    """
    Wraps sklearn IsolationForest with scaling and result merging.

    Config keys (all optional):
        contamination  : float, expected anomaly fraction (default 0.05)
        n_estimators   : int, number of trees (default 200)
        random_state   : int (default 42)
        max_samples    : int or "auto" (default "auto")
    """

    def __init__(self, config: Optional[dict] = None):
        cfg = config or {}
        self.contamination = cfg.get("contamination", 0.05)
        self.n_estimators = cfg.get("n_estimators", 200)
        self.random_state = cfg.get("random_state", 42)
        self.max_samples = cfg.get("max_samples", "auto")

        self.scaler = StandardScaler()
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            max_samples=self.max_samples,
            random_state=self.random_state,
            n_jobs=-1,
        )

    def fit_predict(
        self, feature_df: pd.DataFrame, original_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Fit the model on feature_df and return original_df augmented with:
          - anomaly        : -1 (anomaly) or 1 (normal)
          - anomaly_score  : raw IF score (lower = more anomalous)
          - anomaly_pct    : score normalised to [0, 1] for easier plotting
        """
        X = self.scaler.fit_transform(feature_df.values)

        predictions = self.model.fit_predict(X)
        scores = self.model.score_samples(X)

        result = original_df.copy()
        result["anomaly"] = predictions
        result["anomaly_score"] = scores

        # Normalise to [0,1] where 1 = most anomalous
        min_s, max_s = scores.min(), scores.max()
        if max_s > min_s:
            result["anomaly_pct"] = 1 - (scores - min_s) / (max_s - min_s)
        else:
            result["anomaly_pct"] = 0.0

        return result

    def get_flagged(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """Return only rows flagged as anomalies, sorted by severity."""
        flagged = results_df[results_df["anomaly"] == -1].copy()
        return flagged.sort_values("anomaly_score", ascending=True)
