from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import cv2

from app.core.config import DEFAULT_PREVIEW_RESOLUTION, MODELS_DIR, SUPPORTED_MODEL_SUFFIXES
from app.core.logger import AppLogger
from app.services.camera_service import CameraService

try:
    from ultralytics import YOLO
except Exception:  # pragma: no cover - optional dependency in development
    YOLO = None


@dataclass(frozen=True)
class ModelInfo:
    path: Path
    is_mock: bool = False

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def backend_name(self) -> str:
        if self.is_mock:
            return "Mock"
        suffix = self.path.suffix.lower()
        if suffix == ".pt":
            return "YOLOv8"
        if suffix == ".hef":
            return "Hailo"
        return "Unknown"

    @classmethod
    def mock(cls) -> "ModelInfo":
        return cls(path=Path("__mock__"), is_mock=True)


class BaseInferenceBackend(ABC):
    def __init__(self, model_path: Path, logger: AppLogger) -> None:
        self.model_path = model_path
        self.logger = logger

    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def infer(self, frame):
        raise NotImplementedError


class UltralyticsBackend(BaseInferenceBackend):
    def __init__(self, model_path: Path, logger: AppLogger) -> None:
        super().__init__(model_path, logger)
        self.model = None

    def load(self) -> None:
        if YOLO is None:
            raise RuntimeError("未安裝 ultralytics，無法載入 .pt 模型。")
        self.logger.info(f"正在載入 YOLOv8 模型：{self.model_path.name}")
        self.model = YOLO(str(self.model_path))

    def infer(self, frame):
        results = self.model.predict(source=frame, verbose=False)
        return results[0].plot()


class HailoBackend(BaseInferenceBackend):
    def load(self) -> None:
        raise NotImplementedError("`.hef` backend 已保留，但這一版尚未串接 Hailo runtime。")

    def infer(self, frame):
        return frame


class MockBackend(BaseInferenceBackend):
    def __init__(self, model_path: Path, logger: AppLogger) -> None:
        super().__init__(model_path, logger)
        self.frame_index = 0

    def load(self) -> None:
        self.logger.info("已載入 Mock 推論模式。")

    def infer(self, frame):
        self.frame_index += 1
        height, width = frame.shape[:2]

        box_width = max(width // 4, 160)
        box_height = max(height // 3, 180)
        max_x = max(width - box_width - 20, 20)
        cycle = self.frame_index % max(max_x - 20, 1)
        x1 = 20 + cycle
        y1 = max((height - box_height) // 2, 20)
        x2 = min(x1 + box_width, width - 20)
        y2 = min(y1 + box_height, height - 20)

        annotated = frame.copy()
        overlay = annotated.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (15, 118, 110), -1)
        annotated = cv2.addWeighted(overlay, 0.18, annotated, 0.82, 0)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (20, 184, 166), 3)

        label = "fresh" if (self.frame_index // 45) % 2 == 0 else "dried"
        confidence = 0.92 if label == "fresh" else 0.88
        label_text = f"{label} {confidence:.2f}"
        cv2.putText(
            annotated,
            label_text,
            (x1, max(y1 - 12, 32)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            annotated,
            "MOCK INFERENCE MODE",
            (24, height - 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        return annotated


class InferenceService:
    def __init__(self, camera_service: CameraService, logger: AppLogger) -> None:
        self.camera_service = camera_service
        self.logger = logger
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def scan_models(self) -> list[ModelInfo]:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        models = [ModelInfo.mock()]
        models.extend(
            ModelInfo(path=model_path)
            for model_path in sorted(MODELS_DIR.iterdir())
            if model_path.is_file() and model_path.suffix.lower() in SUPPORTED_MODEL_SUFFIXES
        )
        self.logger.info(f"掃描模型完成，共找到 {len(models)} 個模型。")
        return models

    def start_inference(
        self,
        model_path: Path,
        state_callback: Callable[[bool], None] | None = None,
    ) -> bool:
        if self.is_running():
            self.logger.warning("推論已經在執行中。")
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._inference_loop,
            args=(model_path, state_callback),
            daemon=True,
        )
        self._thread.start()
        return True

    def stop_inference(self) -> None:
        self._stop_event.set()

    def _build_backend(self, model_path: Path) -> BaseInferenceBackend:
        if model_path.name == "__mock__":
            return MockBackend(model_path, self.logger)
        suffix = model_path.suffix.lower()
        if suffix == ".pt":
            return UltralyticsBackend(model_path, self.logger)
        if suffix == ".hef":
            return HailoBackend(model_path, self.logger)
        raise RuntimeError(f"不支援的模型格式：{model_path.suffix}")

    def _inference_loop(self, model_path: Path, state_callback: Callable[[bool], None] | None) -> None:
        window_name = "Edge Inference"
        if state_callback:
            state_callback(True)

        try:
            backend = self._build_backend(model_path)
            backend.load()
            session = self.camera_service.acquire_camera(DEFAULT_PREVIEW_RESOLUTION, timeout=2.0)
        except Exception as error:
            self.logger.error(f"啟動推論失敗：{error}")
            if state_callback:
                state_callback(False)
            return

        try:
            self.logger.info(f"推論已開始，模型：{model_path.name}")
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, *DEFAULT_PREVIEW_RESOLUTION)

            while not self._stop_event.is_set():
                ok, frame = session.read()
                if not ok:
                    self.logger.warning("推論讀取影像失敗，正在結束推論。")
                    break

                annotated_frame = backend.infer(frame)
                cv2.imshow(window_name, annotated_frame)
                key = cv2.waitKey(1) & 0xFF
                visible = cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
                if key == ord("q") or visible < 1:
                    break
        finally:
            session.release()
            cv2.destroyWindow(window_name)
            self.logger.info("推論已停止。")
            if state_callback:
                state_callback(False)
