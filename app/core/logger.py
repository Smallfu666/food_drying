from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QObject, Signal


class AppLogger(QObject):
    message_logged = Signal(str)

    def _emit(self, level: str, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message_logged.emit(f"[{timestamp}] [{level}] {message}")

    def info(self, message: str) -> None:
        self._emit("INFO", message)

    def warning(self, message: str) -> None:
        self._emit("WARN", message)

    def error(self, message: str) -> None:
        self._emit("ERROR", message)
