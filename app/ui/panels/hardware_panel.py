from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from app.core.config import DEFAULT_SERIAL_PORT


class HardwarePanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("panel")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title = QLabel("硬體控制")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        preview_hint = QLabel("使用 OpenCV 視窗預覽 1280x720 即時影像。")
        preview_hint.setObjectName("hintText")
        preview_hint.setWordWrap(True)
        layout.addWidget(preview_hint)

        self.preview_button = QPushButton("開啟相機預覽")
        self.preview_button.setProperty("primary", True)
        layout.addWidget(self.preview_button)

        uart_title = QLabel("MCU / UART")
        uart_title.setObjectName("sectionTitle")
        layout.addWidget(uart_title)

        port_row = QHBoxLayout()
        port_label = QLabel("序列埠")
        port_row.addWidget(port_label)
        self.port_input = QLineEdit(DEFAULT_SERIAL_PORT)
        self.port_input.setPlaceholderText("/dev/ttyAMA0")
        port_row.addWidget(self.port_input)
        layout.addLayout(port_row)

        button_row = QHBoxLayout()
        self.connect_button = QPushButton("連線 UART")
        self.refresh_ports_button = QPushButton("掃描序列埠")
        button_row.addWidget(self.connect_button)
        button_row.addWidget(self.refresh_ports_button)
        layout.addLayout(button_row)

        dryer_row = QHBoxLayout()
        self.start_button = QPushButton("送出 ON")
        self.start_button.setProperty("primary", True)
        self.stop_button = QPushButton("送出 OFF")
        self.stop_button.setProperty("danger", True)
        dryer_row.addWidget(self.start_button)
        dryer_row.addWidget(self.stop_button)
        layout.addLayout(dryer_row)

        fan_title = QLabel("風扇速度")
        fan_title.setObjectName("sectionTitle")
        layout.addWidget(fan_title)

        fan_hint = QLabel("拖曳後放開滑桿，才會送出一次 PWM 指令。")
        fan_hint.setObjectName("hintText")
        fan_hint.setWordWrap(True)
        layout.addWidget(fan_hint)

        fan_row = QHBoxLayout()
        self.fan_slider = QSlider(Qt.Orientation.Horizontal)
        self.fan_slider.setRange(0, 100)
        self.fan_slider.setValue(50)
        fan_row.addWidget(self.fan_slider)

        self.fan_value_label = QLabel("50")
        self.fan_value_label.setObjectName("valueChip")
        fan_row.addWidget(self.fan_value_label)
        layout.addLayout(fan_row)

        layout.addStretch()
