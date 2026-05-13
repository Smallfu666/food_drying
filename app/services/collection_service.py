from __future__ import annotations

import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

import cv2

from app.core.config import DATASETS_DIR, DEFAULT_CAPTURE_RESOLUTION
from app.core.logger import AppLogger
from app.services.camera_service import CameraService


class DataCollectionService:
    def __init__(self, camera_service: CameraService, logger: AppLogger) -> None:
        self.camera_service = camera_service
        self.logger = logger
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self.current_dataset_dir: Path | None = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start_collection(
        self,
        duration_hours: float,
        interval_minutes: float,
        state_callback: Callable[[bool, str], None] | None = None,
        frame_callback: Callable[[object], None] | None = None,
        progress_callback: Callable[[int, str, str], None] | None = None,
    ) -> bool:
        if self.is_running():
            self.logger.warning("資料收集已經在執行中。")
            return False

        if duration_hours <= 0 or interval_minutes <= 0:
            self.logger.error("資料收集參數必須大於 0。")
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._collection_loop,
            args=(duration_hours, interval_minutes, state_callback, frame_callback, progress_callback),
            daemon=True,
        )
        self._thread.start()
        return True

    def stop_collection(self) -> None:
        self._stop_event.set()

    def _collection_loop(
        self,
        duration_hours: float,
        interval_minutes: float,
        state_callback: Callable[[bool, str], None] | None,
        frame_callback: Callable[[object], None] | None,
        progress_callback: Callable[[int, str, str], None] | None,
    ) -> None:
        started_at = datetime.now()
        self.current_dataset_dir = DATASETS_DIR / started_at.strftime("%Y-%m-%d_%H-%M-%S")
        self.current_dataset_dir.mkdir(parents=True, exist_ok=True)

        if state_callback:
            state_callback(True, str(self.current_dataset_dir))

        self.logger.info(f"資料收集開始，資料夾：{self.current_dataset_dir}")

        try:
            session = self.camera_service.acquire_camera(DEFAULT_CAPTURE_RESOLUTION, timeout=2.0)
        except Exception as error:
            self.logger.error(f"資料收集無法啟動：{error}")
            if state_callback:
                state_callback(False, str(self.current_dataset_dir))
            return

        deadline = started_at + timedelta(hours=duration_hours)
        interval_seconds = interval_minutes * 60
        next_capture_at = started_at
        last_read_warning_at: datetime | None = None
        capture_index = 1

        try:
            while not self._stop_event.is_set() and datetime.now() <= deadline:
                now = datetime.now()
                ok, frame = session.read()
                if not ok:
                    if last_read_warning_at is None or (now - last_read_warning_at).total_seconds() >= 5:
                        self.logger.warning("資料收集讀取影像失敗，正在重試。")
                        last_read_warning_at = now
                    if self._stop_event.wait(0.1):
                        break
                    continue

                if frame_callback:
                    frame_callback(frame.copy())

                if now >= next_capture_at:
                    hour_index = int((now - started_at).total_seconds() // 3600) + 1
                    hour_dir = self.current_dataset_dir / f"hour_{hour_index:02d}"
                    hour_dir.mkdir(parents=True, exist_ok=True)
                    filename = hour_dir / f"capture_{now.strftime('%Y%m%d_%H%M%S')}_{capture_index:04d}.jpg"
                    success = cv2.imwrite(str(filename), frame)
                    if success:
                        self.logger.info(f"已儲存影像：{filename.name}")
                        if progress_callback:
                            progress_callback(capture_index, filename.name, now.strftime("%Y-%m-%d %H:%M:%S"))
                        capture_index += 1
                    else:
                        self.logger.error(f"儲存影像失敗：{filename}")

                    while next_capture_at <= now:
                        next_capture_at += timedelta(seconds=interval_seconds)

                if self._stop_event.wait(0.05):
                    break
        finally:
            session.release()
            if self._stop_event.is_set():
                self.logger.info("資料收集已手動停止。")
            else:
                self.logger.info("資料收集已完成。")
            if state_callback:
                state_callback(False, str(self.current_dataset_dir))
