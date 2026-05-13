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
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(18)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)
        step_badge = QLabel("01")
        step_badge.setObjectName("stepBadge")
        title = QLabel("硬體控制")
        title.setObjectName("sectionTitle")
        title_row.addWidget(step_badge)
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)

        summary = QLabel("先控制機器電源，再進行資料收集與推論。")
        summary.setObjectName("hintText")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        dryer_row = QHBoxLayout()
        dryer_row.setSpacing(12)
        self.start_button = QPushButton("啟動機器 (ON)")
        self.start_button.setProperty("primary", True)
        self.pause_button = QPushButton("暫停機器 (PAUSE)")
        self.stop_button = QPushButton("停止歸零 (STOP)")
        self.stop_button.setProperty("danger", True)
        dryer_row.addWidget(self.start_button)
        dryer_row.addWidget(self.pause_button)
        dryer_row.addWidget(self.stop_button)
        layout.addLayout(dryer_row)

        self.power_status_label = QLabel("控制狀態：待命")
        self.power_status_label.setObjectName("statusChip")
        self.power_status_label.setWordWrap(True)
        layout.addWidget(self.power_status_label)

        # 傳感器數據顯示
        self.sensor_data_label = QLabel("箱體溫度：-- ℃ | 濕度：-- %")
        self.sensor_data_label.setObjectName("hintText")
        layout.addWidget(self.sensor_data_label)

        self.preview_button = QPushButton("開啟獨立相機預覽")
        layout.addWidget(self.preview_button)

        self.advanced_toggle = QCheckBox("顯示 UART / 參數進階設定")
        layout.addWidget(self.advanced_toggle)

        self.advanced_frame = QFrame()
        self.advanced_frame.setObjectName("panel")
        advanced_layout = QVBoxLayout(self.advanced_frame)
        advanced_layout.setContentsMargins(16, 16, 16, 16)
        advanced_layout.setSpacing(14)

        uart_title = QLabel("UART 進階設定")
        uart_title.setObjectName("subsectionTitle")
        advanced_layout.addWidget(uart_title)

        uart_hint = QLabel(f"預設：{DEFAULT_SERIAL_PORT} / {SERIAL_BAUDRATE} {UART_FORMAT}")
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

        param_title = QLabel("乾燥參數設定")
        param_title.setObjectName("subsectionTitle")
        advanced_layout.addWidget(param_title)

        temp_row = QHBoxLayout()
        temp_label = QLabel("設定溫度 (℃)")
        temp_row.addWidget(temp_label)
        from PySide6.QtWidgets import QSpinBox
        self.temp_input = QSpinBox()
        self.temp_input.setRange(20, 80)
        self.temp_input.setValue(50)
        temp_row.addWidget(self.temp_input)
        self.set_temp_button = QPushButton("設定溫度")
        temp_row.addWidget(self.set_temp_button)
        advanced_layout.addLayout(temp_row)

        time_row = QHBoxLayout()
        time_label = QLabel("設定時間 (分鐘)")
        time_row.addWidget(time_label)
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 9999)
        self.time_input.setValue(60)
        time_row.addWidget(self.time_input)
        self.set_time_button = QPushButton("設定時間")
        time_row.addWidget(self.set_time_button)
        advanced_layout.addLayout(time_row)

        self.advanced_frame.setVisible(False)
        self.advanced_toggle.toggled.connect(self.advanced_frame.setVisible)
        layout.addWidget(self.advanced_frame)
