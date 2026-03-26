"""tests/test_detector.py"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.detector import AnomalyDetector


def make_feature_df(n=100):
    np.random.seed(42)
    return pd.DataFrame({
        "hour_of_day": np.random.randint(0, 24, n),
        "is_error": np.random.randint(0, 2, n),
        "is_server_error": np.random.randint(0, 2, n),
        "bytes_transferred": np.random.randint(100, 50000, n),
        "log_bytes": np.log1p(np.random.randint(100, 50000, n)),
        "method_encoded": np.random.randint(0, 5, n),
        "status_class": np.random.randint(2, 5, n),
        "path_depth": np.random.randint(1, 6, n),
        "ip_request_count": np.random.randint(1, 50, n),
    })


def make_original_df(n=100):
    return pd.DataFrame({"ip": [f"192.168.1.{i % 20}" for i in range(n)]})


class TestAnomalyDetector:
    def setup_method(self):
        self.detector = AnomalyDetector(config={"contamination": 0.1, "n_estimators": 50})

    def test_fit_predict_returns_df(self):
        features = make_feature_df()
        original = make_original_df()
        result = self.detector.fit_predict(features, original)
        assert isinstance(result, pd.DataFrame)

    def test_anomaly_column_present(self):
        result = self.detector.fit_predict(make_feature_df(), make_original_df())
        assert "anomaly" in result.columns

    def test_anomaly_values_valid(self):
        result = self.detector.fit_predict(make_feature_df(), make_original_df())
        assert set(result["anomaly"].unique()).issubset({-1, 1})

    def test_anomaly_score_column_present(self):
        result = self.detector.fit_predict(make_feature_df(), make_original_df())
        assert "anomaly_score" in result.columns

    def test_anomaly_pct_in_range(self):
        result = self.detector.fit_predict(make_feature_df(), make_original_df())
        assert result["anomaly_pct"].between(0, 1).all()

    def test_contamination_respected(self):
        n = 100
        result = self.detector.fit_predict(make_feature_df(n), make_original_df(n))
        n_anomalies = (result["anomaly"] == -1).sum()
        # Should be approximately contamination * n (±5)
        assert abs(n_anomalies - 10) <= 5

    def test_get_flagged_returns_only_anomalies(self):
        result = self.detector.fit_predict(make_feature_df(), make_original_df())
        flagged = self.detector.get_flagged(result)
        assert (flagged["anomaly"] == -1).all()
