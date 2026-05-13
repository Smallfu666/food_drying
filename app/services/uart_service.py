from __future__ import annotations

import json
import threading
from typing import Iterable, Callable

from app.core.config import (
    DEFAULT_SERIAL_PORT,
    SERIAL_BAUDRATE,
    UART_CMD_ON,
    UART_CMD_STOP,
    UART_CMD_PAUSE,
    UART_CMD_SET_TEMP,
    UART_CMD_SET_TIME,
)
from app.core.logger import AppLogger

try:
    import serial
    from serial.tools import list_ports
except Exception:  # pragma: no cover
    serial = None
    list_ports = None


class UARTService:
    def __init__(self, logger: AppLogger) -> None:
        self.logger = logger
        self._serial_connection = None
        self._simulation_mode = serial is None
        self._last_port = DEFAULT_SERIAL_PORT
        self._read_thread = None
        self._running = False
        self._status_callback: Callable[[dict], None] | None = None

        if self._simulation_mode:
            self.logger.warning("未載入 pyserial，UART 會以模擬模式執行。")

    @property
    def is_connected(self) -> bool:
        return bool(self._serial_connection and self._serial_connection.is_open)

    @property
    def last_port(self) -> str:
        return self._last_port

    def set_status_callback(self, callback: Callable[[dict], None]) -> None:
        self._status_callback = callback

    def available_ports(self) -> list[str]:
        ports: Iterable = list_ports.comports() if list_ports else []
        return [port.device for port in ports]

    def connect(self, port: str | None = None, baudrate: int = SERIAL_BAUDRATE) -> bool:
        selected_port = port or DEFAULT_SERIAL_PORT
        self._last_port = selected_port

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
            self._start_reading()
            self.logger.info(f"UART 已連線到 {selected_port}。")
            return True
        except Exception as error:
            self._simulation_mode = True
            self.logger.warning(f"UART 連線失敗，改用模擬模式：{error}")
            return False

    def disconnect(self) -> None:
        self._stop_reading()
        if self._serial_connection and self._serial_connection.is_open:
            self._serial_connection.close()
            self.logger.info("UART 已中斷連線。")
        self._serial_connection = None

    def _start_reading(self) -> None:
        if self._read_thread and self._read_thread.is_alive():
            return
        self._running = True
        self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._read_thread.start()

    def _stop_reading(self) -> None:
        self._running = False
        if self._read_thread:
            self._read_thread.join(timeout=1.5)
            self._read_thread = None

    def _read_loop(self) -> None:
        while self._running and self._serial_connection and self._serial_connection.is_open:
            try:
                if self._serial_connection.in_waiting > 0:
                    line = self._serial_connection.readline().decode("utf-8").strip()
                    if not line:
                        continue
                    
                    if line.startswith("[{") and line.endswith("}]"):
                        try:
                            data_list = json.loads(line)
                            if data_list and isinstance(data_list, list):
                                self._handle_status_update(data_list[0])
                        except json.JSONDecodeError:
                            self.logger.error(f"解析 UART JSON 失敗: {line}")
                    else:
                        self.logger.info(f"[UART 接收] {line}")
            except Exception as e:
                self.logger.error(f"UART 讀取錯誤: {e}")
                break

    def _handle_status_update(self, status: dict) -> None:
        raw_data = status.get("data", "")
        # 解析通訊協議 V1.2 Data 格式
        # 0267010c -> 010c = 26.8C
        # 026891 -> 91 = 145 = 72.5%
        # 實際應用中會根據需求提取更多資訊
        if self._status_callback:
            self._status_callback(status)

    def send(self, payload: str) -> bool:
        message = payload.strip()
        if self._simulation_mode or not self._serial_connection or not self._serial_connection.is_open:
            self.logger.info(f"[SIM UART] {message}")
            return False

        self._serial_connection.write(f"{message}\n".encode("utf-8"))
        self.logger.info(f"[UART] 已送出：{message}")
        return True

    def power_on(self) -> bool:
        return self.send(UART_CMD_ON)

    def pause(self) -> bool:
        return self.send(UART_CMD_PAUSE)

    def stop(self) -> bool:
        return self.send(UART_CMD_STOP)

    def set_temperature(self, temp: int) -> bool:
        return self.send(f"{UART_CMD_SET_TEMP}{temp}")

    def set_time(self, minutes: int) -> bool:
        return self.send(f"{UART_CMD_SET_TIME}{minutes}")
