from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class CollectionPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("panel")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title = QLabel("資料收集")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        summary = QLabel("依照指定時長與拍攝間隔，自動建立資料集並按小時分資料夾。")
        summary.setObjectName("hintText")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        duration_row = QHBoxLayout()
        duration_label = QLabel("持續時間（小時）")
        duration_row.addWidget(duration_label)
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setRange(0.1, 240.0)
        self.duration_input.setDecimals(1)
        self.duration_input.setSingleStep(0.5)
        self.duration_input.setValue(1.0)
        self.duration_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        duration_row.addWidget(self.duration_input)
        layout.addLayout(duration_row)

        interval_row = QHBoxLayout()
        interval_label = QLabel("拍攝間隔（分鐘）")
        interval_row.addWidget(interval_label)
        self.interval_input = QDoubleSpinBox()
        self.interval_input.setRange(0.1, 240.0)
        self.interval_input.setDecimals(1)
        self.interval_input.setSingleStep(0.5)
        self.interval_input.setValue(5.0)
        self.interval_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        interval_row.addWidget(self.interval_input)
        layout.addLayout(interval_row)

        self.dataset_dir_label = QLabel("目前資料夾：尚未建立")
        self.dataset_dir_label.setObjectName("hintText")
        self.dataset_dir_label.setWordWrap(True)
        layout.addWidget(self.dataset_dir_label)

        self.progress_label = QLabel("收集狀態：尚未開始")
        self.progress_label.setObjectName("hintText")
        self.progress_label.setWordWrap(True)
        layout.addWidget(self.progress_label)

        self.preview_label = QLabel("資料收集開始後會在這裡顯示即時畫面")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(280)
        self.preview_label.setStyleSheet("border: 1px solid #D9E2EC; border-radius: 12px;")
        layout.addWidget(self.preview_label)

        action_row = QHBoxLayout()
        self.start_button = QPushButton("開始收集資料")
        self.start_button.setProperty("primary", True)
        self.stop_button = QPushButton("停止收集")
        action_row.addWidget(self.start_button)
        action_row.addWidget(self.stop_button)
        layout.addLayout(action_row)

        utility_row = QVBoxLayout()
        utility_row.setSpacing(10)
        self.open_dataset_button = QPushButton("開啟目前資料夾")
        self.open_browser_button = QPushButton("開啟 AI Maker")
        utility_row.addWidget(self.open_dataset_button)
        utility_row.addWidget(self.open_browser_button)
        layout.addLayout(utility_row)

        layout.addStretch()

    def set_preview_pixmap(self, pixmap: QPixmap) -> None:
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
