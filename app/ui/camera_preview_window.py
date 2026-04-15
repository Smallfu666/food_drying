from __future__ import annotations

import time

import cv2
from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from app.core.config import DEFAULT_CAPTURE_RESOLUTION
from app.core.logger import AppLogger
from app.services.camera_service import CameraService


class CameraPreviewWorker(QObject):
    frame_ready = Signal(QImage)
    started = Signal(int, int, int)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, camera_service: CameraService, logger: AppLogger) -> None:
        super().__init__()
        self.camera_service = camera_service
        self.logger = logger
        self._running = False

    @Slot()
    def run(self) -> None:
        self._running = True

        try:
            session = self.camera_service.acquire_camera(DEFAULT_CAPTURE_RESOLUTION)
        except Exception as error:
            self.failed.emit(str(error))
            self.finished.emit()
            return

        capture = session.capture
        real_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        real_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.started.emit(session.camera_index, real_width, real_height)

        try:
            while self._running:
                ok, frame = session.read()
                if not ok:
                    time.sleep(0.05)
                    continue

                display_frame = self._resize_for_display(frame, max_width=960)
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                height, width, channels = rgb_frame.shape
                bytes_per_line = channels * width
                image = QImage(
                    rgb_frame.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_RGB888,
                ).copy()
                self.frame_ready.emit(image)
                time.sleep(0.01)
        finally:
            session.release()
            self.finished.emit()

    @Slot()
    def stop(self) -> None:
        self._running = False

    def _resize_for_display(self, frame, max_width: int):
        height, width = frame.shape[:2]
        if width <= max_width:
            return frame

        scale = max_width / width
        return cv2.resize(frame, (int(width * scale), int(height * scale)))


class CameraPreviewWindow(QMainWindow):
    closed = Signal()

    def __init__(self, camera_service: CameraService, logger: AppLogger) -> None:
        super().__init__()
        self.camera_service = camera_service
        self.logger = logger
        self.thread: QThread | None = None
        self.worker: CameraPreviewWorker | None = None

        self.setWindowTitle("相機預覽")
        self.resize(980, 620)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.status_label = QLabel("正在啟動相機預覽...")
        self.status_label.setObjectName("hintText")
        layout.addWidget(self.status_label)

        self.image_label = QLabel("等待相機畫面")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(800, 450)
        self.image_label.setStyleSheet("border: 1px solid #D9E2EC; border-radius: 12px;")
        layout.addWidget(self.image_label, 1)

        self.setCentralWidget(root)

    def start(self) -> None:
        if self.thread is not None:
            return

        self.thread = QThread(self)
        self.worker = CameraPreviewWorker(self.camera_service, self.logger)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.frame_ready.connect(self._show_frame)
        self.worker.started.connect(self._on_started)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self._on_thread_finished)

        self.thread.start()

    def stop(self) -> None:
        if self.worker is not None:
            self.worker.stop()

    @Slot(QImage)
    def _show_frame(self, image: QImage) -> None:
        pixmap = QPixmap.fromImage(image)
        self.image_label.setPixmap(
            pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    @Slot(int, int, int)
    def _on_started(self, camera_index: int, width: int, height: int) -> None:
        self.status_label.setText(f"相機預覽中：index {camera_index} / {width}x{height}")
        self.logger.info(f"相機預覽已啟動，使用 index {camera_index}，解析度 {width}x{height}。")

    @Slot(str)
    def _on_failed(self, message: str) -> None:
        self.status_label.setText(f"相機預覽啟動失敗：{message}")
        self.logger.error(f"相機預覽啟動失敗：{message}")

    @Slot()
    def _on_thread_finished(self) -> None:
        if self.thread is not None:
            self.thread.deleteLater()
        self.thread = None
        self.worker = None
        self.logger.info("相機預覽已關閉。")
        self.closed.emit()

    def closeEvent(self, event) -> None:  # noqa: N802
        self.stop()
        super().closeEvent(event)
