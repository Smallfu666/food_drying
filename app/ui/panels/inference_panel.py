from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)


class InferencePanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("panel")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title = QLabel("邊緣推論")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        summary = QLabel("支援 `.pt` 直接跑 YOLOv8，保留 `.hef` 介面，並內建 Mock 模式可先測流程。")
        summary.setObjectName("hintText")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        model_row = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(220)
        self.refresh_models_button = QPushButton("掃描模型")
        model_row.addWidget(self.model_combo, 1)
        model_row.addWidget(self.refresh_models_button)
        layout.addLayout(model_row)

        utility_row = QVBoxLayout()
        utility_row.setSpacing(10)
        self.open_model_dir_button = QPushButton("開啟模型資料夾")
        utility_row.addWidget(self.open_model_dir_button)
        layout.addLayout(utility_row)

        action_row = QHBoxLayout()
        self.start_button = QPushButton("開始推論")
        self.start_button.setProperty("primary", True)
        self.stop_button = QPushButton("停止推論")
        action_row.addWidget(self.start_button)
        action_row.addWidget(self.stop_button)
        layout.addLayout(action_row)

        status_title = QLabel("系統狀態")
        status_title.setObjectName("sectionTitle")
        layout.addWidget(status_title)

        self.status_log = QPlainTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setPlaceholderText("系統狀態會顯示在這裡。")
        layout.addWidget(self.status_log, 1)
