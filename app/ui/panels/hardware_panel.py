from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from app.core.config import DEFAULT_SERIAL_PORT, SERIAL_BAUDRATE, UART_FORMAT


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

        summary = QLabel("先控制機器電源，再進行資料收集與推論。")
        summary.setObjectName("hintText")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        dryer_row = QHBoxLayout()
        self.start_button = QPushButton("開啟機器")
        self.start_button.setProperty("primary", True)
        self.stop_button = QPushButton("關閉機器")
        self.stop_button.setProperty("danger", True)
        dryer_row.addWidget(self.start_button)
        dryer_row.addWidget(self.stop_button)
        layout.addLayout(dryer_row)

        self.power_status_label = QLabel("控制狀態：待命")
        self.power_status_label.setObjectName("hintText")
        self.power_status_label.setWordWrap(True)
        layout.addWidget(self.power_status_label)

        self.preview_button = QPushButton("開啟獨立相機預覽")
        layout.addWidget(self.preview_button)

        self.advanced_toggle = QCheckBox("顯示 UART / 風扇進階設定")
        layout.addWidget(self.advanced_toggle)

        self.advanced_frame = QFrame()
        self.advanced_frame.setObjectName("panel")
        advanced_layout = QVBoxLayout(self.advanced_frame)
        advanced_layout.setContentsMargins(16, 16, 16, 16)
        advanced_layout.setSpacing(14)

        uart_title = QLabel("UART 進階設定")
        uart_title.setObjectName("sectionTitle")
        advanced_layout.addWidget(uart_title)

        uart_hint = QLabel(f"預設：{DEFAULT_SERIAL_PORT} / {SERIAL_BAUDRATE} {UART_FORMAT} / on-off")
        uart_hint.setObjectName("hintText")
        uart_hint.setWordWrap(True)
        advanced_layout.addWidget(uart_hint)

        port_row = QHBoxLayout()
        port_label = QLabel("序列埠")
        port_row.addWidget(port_label)
        self.port_input = QLineEdit(DEFAULT_SERIAL_PORT)
        self.port_input.setPlaceholderText("/dev/ttyAMA0")
        port_row.addWidget(self.port_input)
        advanced_layout.addLayout(port_row)

        self.uart_status_label = QLabel("UART 狀態：未連線")
        self.uart_status_label.setObjectName("hintText")
        self.uart_status_label.setWordWrap(True)
        advanced_layout.addWidget(self.uart_status_label)

        button_row = QHBoxLayout()
        self.connect_button = QPushButton("連線 UART")
        self.refresh_ports_button = QPushButton("掃描序列埠")
        button_row.addWidget(self.connect_button)
        button_row.addWidget(self.refresh_ports_button)
        advanced_layout.addLayout(button_row)

        fan_title = QLabel("風扇速度")
        fan_title.setObjectName("sectionTitle")
        advanced_layout.addWidget(fan_title)

        fan_hint = QLabel("拖曳後放開滑桿，才會送出一次 PWM 指令。")
        fan_hint.setObjectName("hintText")
        fan_hint.setWordWrap(True)
        advanced_layout.addWidget(fan_hint)

        fan_row = QHBoxLayout()
        self.fan_slider = QSlider(Qt.Orientation.Horizontal)
        self.fan_slider.setRange(0, 100)
        self.fan_slider.setValue(50)
        fan_row.addWidget(self.fan_slider)

        self.fan_value_label = QLabel("50")
        self.fan_value_label.setObjectName("valueChip")
        fan_row.addWidget(self.fan_value_label)
        advanced_layout.addLayout(fan_row)

        self.advanced_frame.setVisible(False)
        self.advanced_toggle.toggled.connect(self.advanced_frame.setVisible)
        layout.addWidget(self.advanced_frame)

        layout.addStretch()
