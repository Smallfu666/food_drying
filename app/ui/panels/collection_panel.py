from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)


class CollectionPanel(QFrame):
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
        step_badge = QLabel("02")
        step_badge.setObjectName("stepBadge")
        title = QLabel("資料收集")
        title.setObjectName("sectionTitle")
        title_row.addWidget(step_badge)
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)

        summary = QLabel("依照指定時長與拍攝間隔，自動建立資料集並按小時分資料夾。")
        summary.setObjectName("hintText")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        parameter_grid = QGridLayout()
        parameter_grid.setHorizontalSpacing(14)
        parameter_grid.setVerticalSpacing(10)

        duration_label = QLabel("持續時間（小時）")
        duration_label.setObjectName("fieldLabel")
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setRange(0.1, 240.0)
        self.duration_input.setDecimals(1)
        self.duration_input.setSingleStep(0.5)
        self.duration_input.setValue(1.0)
        self.duration_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        parameter_grid.addWidget(duration_label, 0, 0)
        parameter_grid.addWidget(self.duration_input, 0, 1)

        interval_label = QLabel("拍攝間隔（分鐘）")
        interval_label.setObjectName("fieldLabel")
        self.interval_input = QDoubleSpinBox()
        self.interval_input.setRange(0.1, 240.0)
        self.interval_input.setDecimals(1)
        self.interval_input.setSingleStep(0.5)
        self.interval_input.setValue(5.0)
        self.interval_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        parameter_grid.addWidget(interval_label, 0, 2)
        parameter_grid.addWidget(self.interval_input, 0, 3)
        parameter_grid.setColumnStretch(1, 1)
        parameter_grid.setColumnStretch(3, 1)
        layout.addLayout(parameter_grid)

        self.dataset_dir_label = QLabel("目前資料夾：尚未建立")
        self.dataset_dir_label.setObjectName("hintText")
        self.dataset_dir_label.setWordWrap(True)
        layout.addWidget(self.dataset_dir_label)

        self.progress_label = QLabel("收集狀態：尚未開始")
        self.progress_label.setObjectName("statusChip")
        self.progress_label.setWordWrap(True)
        layout.addWidget(self.progress_label)

        self.preview_label = QLabel("資料收集開始後會在這裡顯示即時畫面")
        self.preview_label.setObjectName("cameraPreview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(320)
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.preview_label)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.start_button = QPushButton("開始收集資料")
        self.start_button.setProperty("primary", True)
        self.stop_button = QPushButton("停止收集")
        action_row.addWidget(self.start_button)
        action_row.addWidget(self.stop_button)
        layout.addLayout(action_row)

        utility_row = QHBoxLayout()
        utility_row.setSpacing(12)
        self.open_dataset_button = QPushButton("開啟目前資料夾")
        self.open_browser_button = QPushButton("開啟 AI Maker")
        utility_row.addWidget(self.open_dataset_button)
        utility_row.addWidget(self.open_browser_button)
        layout.addLayout(utility_row)

    def set_preview_pixmap(self, pixmap: QPixmap) -> None:
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
