"""
features.py — Derives numeric feature vectors from parsed log DataFrames.

Features computed (for HTTP logs):
  - hour_of_day         : 0–23, captures time-of-day patterns
  - is_error            : 1 if status >= 400
  - is_server_error     : 1 if status >= 500
  - bytes_transferred   : raw byte count
  - log_bytes           : log1p(bytes) to reduce skew
  - method_encoded      : ordinal encoding of HTTP method
  - status_class        : 1xx–5xx bucket (1–5)
  - path_depth          : number of '/' segments in URL path
  - ip_request_count    : rolling count of requests from same IP (session-level)
"""

import pandas as pd
import numpy as np
from typing import Optional

METHOD_MAP = {"GET": 0, "POST": 1, "PUT": 2, "DELETE": 3, "HEAD": 4, "OPTIONS": 5}


class FeatureExtractor:
    """Transforms a parsed log DataFrame into a numeric feature matrix."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame(index=df.index)

        # Time-based features
        if "timestamp" in df.columns and df["timestamp"].notna().any():
            ts = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
            features["hour_of_day"] = ts.dt.hour.fillna(0).astype(int)
            features["day_of_week"] = ts.dt.dayofweek.fillna(0).astype(int)
        else:
            features["hour_of_day"] = 0
            features["day_of_week"] = 0

        # Status code features
        if "status" in df.columns:
            features["status_class"] = (df["status"] // 100).clip(1, 5)
            features["is_error"] = (df["status"] >= 400).astype(int)
            features["is_server_error"] = (df["status"] >= 500).astype(int)
        else:
            features["status_class"] = 2
            features["is_error"] = 0
            features["is_server_error"] = 0

        # Byte volume
        if "bytes" in df.columns:
            features["bytes_transferred"] = df["bytes"].fillna(0)
            features["log_bytes"] = np.log1p(features["bytes_transferred"])
        else:
            features["bytes_transferred"] = 0
            features["log_bytes"] = 0

        # HTTP method
        if "method" in df.columns:
            features["method_encoded"] = (
                df["method"].map(METHOD_MAP).fillna(99).astype(int)
            )
        else:
            features["method_encoded"] = 0

        # URL path depth
        if "path" in df.columns:
            features["path_depth"] = (
                df["path"].fillna("/").apply(lambda p: p.count("/"))
            )
        else:
            features["path_depth"] = 1

        # Per-IP request volume — a strong signal for brute-force and scanning.
        # Counting total requests per IP (session-level) is a blunt instrument:
        # it catches high-volume attackers but misses slow/distributed attacks
        # where each IP makes only a handful of requests.
        # A sliding time window (e.g., requests-per-IP per 5 minutes) would
        # improve this, at the cost of added complexity.
        if "ip" in df.columns:
            ip_counts = df["ip"].map(df["ip"].value_counts())
            features["ip_request_count"] = ip_counts.fillna(1).astype(int)
        else:
            features["ip_request_count"] = 1

        return features
