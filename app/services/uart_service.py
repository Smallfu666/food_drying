from __future__ import annotations

from typing import Iterable

from app.core.config import DEFAULT_SERIAL_PORT, SERIAL_BAUDRATE
from app.core.logger import AppLogger

try:
    import serial
    from serial.tools import list_ports
except Exception:  # pragma: no cover - optional dependency in development
    serial = None
    list_ports = None


class UARTService:
    def __init__(self, logger: AppLogger) -> None:
        self.logger = logger
        self._serial_connection = None
        self._simulation_mode = serial is None

        if self._simulation_mode:
            self.logger.warning("未載入 pyserial，UART 會以模擬模式執行。")

    def available_ports(self) -> list[str]:
        ports: Iterable = list_ports.comports() if list_ports else []
        return [port.device for port in ports]

    def connect(self, port: str | None = None, baudrate: int = SERIAL_BAUDRATE) -> bool:
        selected_port = port or DEFAULT_SERIAL_PORT

        if serial is None:
            self._simulation_mode = True
            self.logger.warning(f"模擬 UART 連線：{selected_port} @ {baudrate}")
            return False

        if self._serial_connection and self._serial_connection.is_open:
            self.logger.info("UART 已經連線。")
            return True

        try:
            self._serial_connection = serial.Serial(selected_port, baudrate=baudrate, timeout=1)
            self._simulation_mode = False
            self.logger.info(f"UART 已連線到 {selected_port}。")
            return True
        except Exception as error:
            self._simulation_mode = True
            self.logger.warning(f"UART 連線失敗，改用模擬模式：{error}")
            return False

    def disconnect(self) -> None:
        if self._serial_connection and self._serial_connection.is_open:
            self._serial_connection.close()
            self.logger.info("UART 已中斷連線。")
        self._serial_connection = None

    def send(self, payload: str) -> None:
        message = payload.strip()
        if self._simulation_mode or not self._serial_connection or not self._serial_connection.is_open:
            self.logger.info(f"[SIM UART] {message}")
            return

        self._serial_connection.write(f"{message}\n".encode("utf-8"))
        self.logger.info(f"[UART] 已送出：{message}")

    def send_start(self) -> None:
        self.send("START")

    def send_stop(self) -> None:
        self.send("STOP")

    def send_fan_pwm(self, pwm_value: int) -> None:
        clipped_value = max(0, min(100, pwm_value))
        self.send(f"PWM:{clipped_value}")
