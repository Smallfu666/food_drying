from __future__ import annotations

import sys
import shutil
import subprocess
import webbrowser
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QWidget,
    QVBoxLayout,
)

from app.core.config import AI_MAKER_URL, DATASETS_DIR, MODELS_DIR, WINDOW_TITLE
from app.core.logger import AppLogger
from app.core.theme import ThemeManager
from app.services.camera_service import CameraService
from app.services.collection_service import DataCollectionService
from app.services.inference_service import InferenceService, ModelInfo
from app.services.uart_service import UARTService
from app.ui.panels.collection_panel import CollectionPanel
from app.ui.panels.hardware_panel import HardwarePanel
from app.ui.panels.inference_panel import InferencePanel


class MainWindowSignals(QObject):
    preview_changed = Signal(bool)
    collection_changed = Signal(bool, str)
    inference_changed = Signal(bool)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(1600, 880)

        DATASETS_DIR.mkdir(parents=True, exist_ok=True)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

        self.logger = AppLogger()
        self.theme_manager = ThemeManager()
        self.camera_service = CameraService(self.logger)
        self.uart_service = UARTService(self.logger)
        self.collection_service = DataCollectionService(self.camera_service, self.logger)
        self.inference_service = InferenceService(self.camera_service, self.logger)
        self.signals = MainWindowSignals()

        self._build_ui()
        self._bind_events()
        self._refresh_model_list()
        self._refresh_serial_port_hint()
        self._initialize_button_states()

        self.logger.info("系統已就緒。")

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(28, 24, 28, 24)
        root_layout.setSpacing(20)

        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)

        header = QVBoxLayout()
        title = QLabel("果乾 Edge AI 控制台")
        title.setObjectName("titleLabel")
        subtitle = QLabel("資料收集、模型管理與本地即時推論")
        subtitle.setObjectName("hintText")
        header.addWidget(title)
        header.addWidget(subtitle)
        top_bar_layout.addLayout(header)
        top_bar_layout.addStretch()

        self.theme_toggle = QCheckBox("深色模式")
        top_bar_layout.addWidget(self.theme_toggle, alignment=Qt.AlignmentFlag.AlignRight)
        root_layout.addWidget(top_bar)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(18)

        self.hardware_panel = HardwarePanel()
        self.collection_panel = CollectionPanel()
        self.inference_panel = InferencePanel()

        content_layout.addWidget(self.hardware_panel, 1)
        content_layout.addWidget(self.collection_panel, 1)
        content_layout.addWidget(self.inference_panel, 1)

        root_layout.addLayout(content_layout, 1)
        self.setCentralWidget(root)

    def _bind_events(self) -> None:
        self.logger.message_logged.connect(self.inference_panel.status_log.appendPlainText)

        self.signals.preview_changed.connect(self._on_preview_state_changed)
        self.signals.collection_changed.connect(self._on_collection_state_changed)
        self.signals.inference_changed.connect(self._on_inference_state_changed)

        self.theme_toggle.toggled.connect(self._toggle_theme)

        self.hardware_panel.preview_button.clicked.connect(self._toggle_preview)
        self.hardware_panel.connect_button.clicked.connect(self._connect_uart)
        self.hardware_panel.refresh_ports_button.clicked.connect(self._refresh_serial_port_hint)
        self.hardware_panel.start_button.clicked.connect(self.uart_service.send_start)
        self.hardware_panel.stop_button.clicked.connect(self.uart_service.send_stop)
        self.hardware_panel.fan_slider.valueChanged.connect(
            lambda value: self.hardware_panel.fan_value_label.setText(str(value))
        )
        self.hardware_panel.fan_slider.sliderReleased.connect(self._send_fan_pwm)

        self.collection_panel.start_button.clicked.connect(self._start_collection)
        self.collection_panel.stop_button.clicked.connect(self.collection_service.stop_collection)
        self.collection_panel.open_dataset_button.clicked.connect(self._open_current_dataset_dir)
        self.collection_panel.open_browser_button.clicked.connect(self._open_ai_maker)

        self.inference_panel.open_model_dir_button.clicked.connect(self._open_model_dir)
        self.inference_panel.refresh_models_button.clicked.connect(self._refresh_model_list)
        self.inference_panel.start_button.clicked.connect(self._start_inference)
        self.inference_panel.stop_button.clicked.connect(self.inference_service.stop_inference)

    def _initialize_button_states(self) -> None:
        self.collection_panel.stop_button.setEnabled(False)
        self.inference_panel.stop_button.setEnabled(False)

    def _toggle_theme(self, checked: bool) -> None:
        if checked != (self.theme_manager.current_theme.name == "dark"):
            self.theme_manager.toggle()
        self.theme_manager.apply(QApplication.instance())

    def _refresh_serial_port_hint(self) -> None:
        ports = self.uart_service.available_ports()
        if ports:
            self.hardware_panel.port_input.setPlaceholderText(ports[0])
            self.logger.info(f"找到序列埠：{', '.join(ports)}")
        else:
            self.logger.warning("目前未偵測到序列埠，仍可使用模擬模式測試。")

    def _connect_uart(self) -> None:
        port = self.hardware_panel.port_input.text().strip()
        self.uart_service.connect(port or None)

    def _toggle_preview(self) -> None:
        if self.camera_service.preview_running():
            self.camera_service.stop_preview()
            return

        self.camera_service.start_preview(self.signals.preview_changed.emit)

    def _on_preview_state_changed(self, running: bool) -> None:
        self.hardware_panel.preview_button.setText("關閉相機預覽" if running else "開啟相機預覽")

    def _send_fan_pwm(self) -> None:
        self.uart_service.send_fan_pwm(self.hardware_panel.fan_slider.value())

    def _start_collection(self) -> None:
        started = self.collection_service.start_collection(
            duration_hours=self.collection_panel.duration_input.value(),
            interval_minutes=self.collection_panel.interval_input.value(),
            state_callback=self.signals.collection_changed.emit,
        )
        if not started:
            QMessageBox.warning(self, "無法開始", "資料收集目前無法啟動，請查看狀態訊息。")

    def _on_collection_state_changed(self, running: bool, dataset_dir: str) -> None:
        self.collection_panel.start_button.setEnabled(not running)
        self.collection_panel.stop_button.setEnabled(running)
        if dataset_dir:
            self.collection_panel.dataset_dir_label.setText(f"目前資料夾：{dataset_dir}")

    def _open_current_dataset_dir(self) -> None:
        dataset_dir = self.collection_service.current_dataset_dir or DATASETS_DIR
        self._open_path(dataset_dir)

    def _open_ai_maker(self) -> None:
        browser_candidates = ["chromium-browser", "chromium", "google-chrome"]
        opened = False

        for browser_name in browser_candidates:
            browser_path = shutil.which(browser_name)
            if browser_path:
                subprocess.Popen([browser_path, AI_MAKER_URL])
                opened = True
                break

        if not opened:
            opened = webbrowser.open(AI_MAKER_URL)

        if opened:
            self.logger.info("已開啟 AI Maker 網站。")
        else:
            self.logger.warning("無法直接啟動瀏覽器，請手動開啟 AI Maker。")

    def _open_model_dir(self) -> None:
        self._open_path(MODELS_DIR)

    def _refresh_model_list(self) -> None:
        models = self.inference_service.scan_models()
        self.inference_panel.model_combo.clear()

        self.inference_panel.model_combo.setEnabled(True)
        for model in models:
            self.inference_panel.model_combo.addItem(f"{model.name} ({model.backend_name})", model)

    def _selected_model(self) -> ModelInfo | None:
        data = self.inference_panel.model_combo.currentData()
        return data if isinstance(data, ModelInfo) else None

    def _start_inference(self) -> None:
        model = self._selected_model()
        if model is None:
            QMessageBox.warning(self, "找不到模型", "請先將 `.pt` 或 `.hef` 模型放入 models 資料夾。")
            return

        started = self.inference_service.start_inference(
            model.path,
            state_callback=self.signals.inference_changed.emit,
        )
        if not started:
            QMessageBox.warning(self, "無法開始", "推論目前無法啟動，請查看狀態訊息。")

    def _on_inference_state_changed(self, running: bool) -> None:
        self.inference_panel.start_button.setEnabled(not running)
        self.inference_panel.stop_button.setEnabled(running)

    def _open_path(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        opened = QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.resolve())))
        if opened:
            self.logger.info(f"已開啟資料夾：{path.resolve()}")
        else:
            self.logger.error(f"無法開啟資料夾：{path.resolve()}")

    def closeEvent(self, event) -> None:  # noqa: N802
        self.camera_service.stop_preview()
        self.collection_service.stop_collection()
        self.inference_service.stop_inference()
        self.uart_service.disconnect()
        super().closeEvent(event)


def run() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.theme_manager.apply(app)
    window.show()
    sys.exit(app.exec())
