from __future__ import annotations

import threading
from dataclasses import dataclass

import cv2

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

    def release_camera(self) -> None:
        if self._camera_lock.locked():
            self._camera_lock.release()

    def find_available_camera(self, max_tested: int = 10) -> int | None:
        self.logger.info("正在掃描可用相機...")
        # 在 RPi 上，通常影像裝置是偶數號，且需要指定 CAP_V4L2
        preferred_indices = [0, 2, 4, 1, 3, 5]
        for index in preferred_indices:
            capture = cv2.VideoCapture(index, cv2.CAP_V4L2)
            if capture.isOpened():
                ok, _ = capture.read()
                capture.release()
                if ok:
                    self.logger.info(f"成功在 index {index} 找到相機。")
                    return index
        
        # fallback to default
        for index in range(max_tested):
            if index in preferred_indices: continue
            capture = cv2.VideoCapture(index)
            if capture.isOpened():
                ok, _ = capture.read()
                capture.release()
                if ok:
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

            # 強制指定 V4L2 以獲得更好的效能與相容性
            capture = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
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
