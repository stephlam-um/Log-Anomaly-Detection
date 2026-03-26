"""
parser.py — Regex-based log parsing for common formats.
Supports: Apache Combined Log, nginx, syslog, and a generic fallback.
"""

import re
import pandas as pd
from datetime import datetime


# ── Format definitions ────────────────────────────────────────────────────────

APACHE_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<bytes>\S+)'
    r'(?: "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)")?'
)

NGINX_PATTERN = re.compile(
    r'(?P<ip>\S+) - \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<bytes>\d+)'
)

SYSLOG_PATTERN = re.compile(
    r'(?P<timestamp>\w{3}\s+\d{1,2} \d{2}:\d{2}:\d{2}) '
    r'(?P<host>\S+) (?P<process>\S+): (?P<message>.+)'
)

APACHE_TIME_FMT = "%d/%b/%Y:%H:%M:%S %z"
SYSLOG_TIME_FMT = "%b %d %H:%M:%S"


class LogParser:
    """Parses raw log lines into a structured pandas DataFrame."""

    def __init__(self, format: str = "apache"):
        self.format = format.lower()
        self._parsers = {
            "apache": self._parse_apache,
            "nginx": self._parse_nginx,
            "syslog": self._parse_syslog,
            "generic": self._parse_generic,
        }
        if self.format not in self._parsers:
            raise ValueError(f"Unsupported log format: {format}")

    def parse(self, lines: list[str]) -> pd.DataFrame:
        parse_fn = self._parsers[self.format]
        records = []
        for line in lines:
            record = parse_fn(line)
            if record:
                records.append(record)
        return pd.DataFrame(records)

    # ── Format-specific parsers ───────────────────────────────────────────────

    def _parse_apache(self, line: str) -> dict | None:
        m = APACHE_PATTERN.match(line)
        if not m:
            return None
        d = m.groupdict()
        try:
            d["timestamp"] = datetime.strptime(d["timestamp"], APACHE_TIME_FMT)
        except ValueError:
            d["timestamp"] = None
        d["status"] = int(d["status"])
        d["bytes"] = int(d["bytes"]) if d["bytes"] != "-" else 0
        return d

    def _parse_nginx(self, line: str) -> dict | None:
        m = NGINX_PATTERN.match(line)
        if not m:
            return None
        d = m.groupdict()
        try:
            d["timestamp"] = datetime.strptime(d["timestamp"], APACHE_TIME_FMT)
        except ValueError:
            d["timestamp"] = None
        d["status"] = int(d["status"])
        d["bytes"] = int(d["bytes"])
        return d

    def _parse_syslog(self, line: str) -> dict | None:
        m = SYSLOG_PATTERN.match(line)
        if not m:
            return None
        d = m.groupdict()
        try:
            d["timestamp"] = datetime.strptime(d["timestamp"], SYSLOG_TIME_FMT).replace(
                year=datetime.now().year
            )
        except ValueError:
            d["timestamp"] = None
        return d

    def _parse_generic(self, line: str) -> dict | None:
        """Best-effort fallback: returns the raw line with a placeholder timestamp."""
        return {"timestamp": None, "raw": line}
