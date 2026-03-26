"""tests/test_parser.py"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.parser import LogParser


APACHE_LINES = [
    '192.168.1.10 - - [10/Mar/2026:08:12:01 +0000] "GET /index.html HTTP/1.1" 200 2048 "-" "Mozilla/5.0"',
    '10.0.0.1 - - [10/Mar/2026:02:00:00 +0000] "POST /api/login HTTP/1.1" 401 256 "-" "python-requests/2.28"',
]

MALFORMED = [
    "this is not a log line",
    "",
    "127.0.0.1 incomplete entry",
]


class TestApacheParser:
    def setup_method(self):
        self.parser = LogParser(format="apache")

    def test_parses_valid_lines(self):
        df = self.parser.parse(APACHE_LINES)
        assert len(df) == 2

    def test_extracts_ip(self):
        df = self.parser.parse(APACHE_LINES)
        assert df.iloc[0]["ip"] == "192.168.1.10"

    def test_extracts_status(self):
        df = self.parser.parse(APACHE_LINES)
        assert df.iloc[1]["status"] == 401

    def test_extracts_bytes(self):
        df = self.parser.parse(APACHE_LINES)
        assert df.iloc[0]["bytes"] == 2048

    def test_skips_malformed_lines(self):
        df = self.parser.parse(MALFORMED)
        assert len(df) == 0

    def test_mixed_input(self):
        df = self.parser.parse(APACHE_LINES + MALFORMED)
        assert len(df) == 2

    def test_timestamp_parsed(self):
        df = self.parser.parse(APACHE_LINES)
        assert df.iloc[0]["timestamp"] is not None


class TestGenericParser:
    def setup_method(self):
        self.parser = LogParser(format="generic")

    def test_returns_raw_field(self):
        df = self.parser.parse(["some random log line"])
        assert "raw" in df.columns
        assert df.iloc[0]["raw"] == "some random log line"


class TestParserInit:
    def test_raises_on_unknown_format(self):
        with pytest.raises(ValueError):
            LogParser(format="cobol")
