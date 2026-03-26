"""
ingestor.py — Reads raw log files from disk.
Handles large files via line-by-line streaming.
"""

from pathlib import Path


class LogIngestor:
    """Reads a log file and returns its lines as a list of strings."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"Log file not found: {self.filepath}")

    def read(self) -> list[str]:
        """Read all lines from the log file, stripping whitespace."""
        with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines

    def stream(self):
        """Generator — yields one line at a time (for large files)."""
        with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line
