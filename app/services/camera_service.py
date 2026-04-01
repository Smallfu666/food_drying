from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable

import cv2

from app.core.config import DEFAULT_PREVIEW_RESOLUTION
from app.core.logger import AppLogger


@dataclass
class CameraCaptureSession:
    camera_service: "CameraService"
    capture: cv2.VideoCapture
    camera_index: int

    def read(self):
        return self.capture.read()

    def release(self) -> None:
        if self.capture.isOpened():
            self.capture.release()
        self.camera_service.release_camera()


class CameraService:
    def __init__(self, logger: AppLogger) -> None:
        self.logger = logger
        self._camera_lock = threading.Lock()
        self._preview_thread: threading.Thread | None = None
        self._preview_stop_event = threading.Event()

    def release_camera(self) -> None:
        if self._camera_lock.locked():
            self._camera_lock.release()

    def find_available_camera(self, max_tested: int = 10) -> int | None:
        self.logger.info("正在掃描可用相機...")
        preferred_indices = [0, 1, 2, 4, 6, 8, 10]
        remaining_indices = [index for index in range(max_tested + 1) if index not in preferred_indices]
        for index in preferred_indices + remaining_indices:
            capture = cv2.VideoCapture(index)
            if capture.isOpened():
                ok, _ = capture.read()
                capture.release()
                if ok:
                    self.logger.info(f"成功在 index {index} 找到相機。")
                    return index
        self.logger.error("找不到可用相機。")
        return None

    def acquire_camera(self, resolution: tuple[int, int], timeout: float = 1.0) -> CameraCaptureSession:
        if not self._camera_lock.acquire(timeout=timeout):
            raise RuntimeError("相機目前被其他流程佔用。")

        try:
            camera_index = self.find_available_camera()
            if camera_index is None:
                raise RuntimeError("沒有可用的相機裝置。")

            capture = cv2.VideoCapture(camera_index)
            if not capture.isOpened():
                raise RuntimeError(f"無法開啟相機 index {camera_index}。")

            width, height = resolution
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            ok, _ = capture.read()
            if not ok:
                capture.release()
                raise RuntimeError("相機開啟成功，但無法讀取影像。")

            return CameraCaptureSession(
                camera_service=self,
                capture=capture,
                camera_index=camera_index,
            )
        except Exception:
            self.release_camera()
            raise

    def preview_running(self) -> bool:
        return self._preview_thread is not None and self._preview_thread.is_alive()

    def start_preview(self, state_callback: Callable[[bool], None] | None = None) -> None:
        if self.preview_running():
            self.logger.warning("相機預覽已經在執行中。")
            return

        self._preview_stop_event.clear()
        self._preview_thread = threading.Thread(
            target=self._preview_loop,
            args=(state_callback,),
            daemon=True,
        )
        self._preview_thread.start()

    def stop_preview(self) -> None:
        self._preview_stop_event.set()

    def _preview_loop(self, state_callback: Callable[[bool], None] | None) -> None:
        window_name = "Camera Preview"
        if state_callback:
            state_callback(True)

        try:
            session = self.acquire_camera(DEFAULT_PREVIEW_RESOLUTION)
        except Exception as error:
            self.logger.error(f"開啟相機預覽失敗：{error}")
            if state_callback:
                state_callback(False)
            return

        try:
            self.logger.info(f"相機預覽已啟動，使用 index {session.camera_index}。")
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, *DEFAULT_PREVIEW_RESOLUTION)

            while not self._preview_stop_event.is_set():
                ok, frame = session.read()
                if not ok:
                    self.logger.warning("相機預覽讀取失敗，正在結束預覽。")
                    break

                cv2.imshow(window_name, frame)
                key = cv2.waitKey(1) & 0xFF
                visible = cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
                if key == ord("q") or visible < 1:
                    break
        finally:
            session.release()
            cv2.destroyWindow(window_name)
            self.logger.info("相機預覽已關閉。")
            if state_callback:
                state_callback(False)
