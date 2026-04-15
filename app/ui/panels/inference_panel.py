from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
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
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(18)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)
        step_badge = QLabel("03")
        step_badge.setObjectName("stepBadge")
        title = QLabel("邊緣推論")
        title.setObjectName("sectionTitle")
        title_row.addWidget(step_badge)
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)

        summary = QLabel("支援 `.pt` 直接跑 YOLOv8，保留 `.hef` 介面，並內建 Mock 模式可先測流程。")
        summary.setObjectName("hintText")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        model_row = QHBoxLayout()
        model_row.setSpacing(12)
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(220)
        self.refresh_models_button = QPushButton("掃描模型")
        model_row.addWidget(self.model_combo, 1)
        model_row.addWidget(self.refresh_models_button)
        layout.addLayout(model_row)

        utility_row = QHBoxLayout()
        utility_row.setSpacing(12)
        self.open_model_dir_button = QPushButton("開啟模型資料夾")
        utility_row.addWidget(self.open_model_dir_button)
        utility_row.addStretch()
        layout.addLayout(utility_row)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.start_button = QPushButton("開始推論")
        self.start_button.setProperty("primary", True)
        self.stop_button = QPushButton("停止推論")
        action_row.addWidget(self.start_button)
        action_row.addWidget(self.stop_button)
        layout.addLayout(action_row)

        self.debug_toggle = QCheckBox("顯示除錯資訊 / 系統狀態")
        layout.addWidget(self.debug_toggle)

        self.debug_frame = QFrame()
        self.debug_frame.setObjectName("panel")
        debug_layout = QVBoxLayout(self.debug_frame)
        debug_layout.setContentsMargins(16, 16, 16, 16)
        debug_layout.setSpacing(12)

        status_title = QLabel("系統狀態")
        status_title.setObjectName("subsectionTitle")
        debug_layout.addWidget(status_title)

        self.status_log = QPlainTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setPlaceholderText("系統狀態會顯示在這裡。")
        self.status_log.setMinimumHeight(220)
        debug_layout.addWidget(self.status_log)

        self.debug_frame.setVisible(False)
        self.debug_toggle.toggled.connect(self.debug_frame.setVisible)
        layout.addWidget(self.debug_frame)
