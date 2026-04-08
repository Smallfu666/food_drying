from __future__ import annotations

import argparse
import sys
import time

try:
    import serial
except ImportError as error:  # pragma: no cover - runtime dependency check
    print("找不到 pyserial，請先安裝相依後再執行。", file=sys.stderr)
    raise SystemExit(1) from error


DEFAULT_PORT = "/dev/ttyAMA0"
DEFAULT_BAUDRATE = 9600
DEFAULT_TIMEOUT = 1.0
DEFAULT_SETTLE = 0.2
POLL_INTERVAL = 0.05


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simple UART probe for Raspberry Pi <-> MCU wiring verification.",
    )
    parser.add_argument("--port", default=DEFAULT_PORT, help="Serial device path.")
    parser.add_argument("--baudrate", type=int, default=DEFAULT_BAUDRATE, help="Serial baudrate.")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Read timeout in seconds.")
    parser.add_argument(
        "--command",
        choices=["on", "off"],
        help="Send a single command and wait for the response.",
    )
    parser.add_argument(
        "--newline",
        action="store_true",
        help="Append newline when sending commands.",
    )
    parser.add_argument(
        "--require-response",
        action="store_true",
        help="Treat missing response as a failure instead of a successful send.",
    )
    parser.add_argument(
        "--settle",
        type=float,
        default=DEFAULT_SETTLE,
        help="Wait time after port open before the first command.",
    )
    return parser


def send_command(connection: serial.Serial, command: str, append_newline: bool) -> bool:
    payload = f"{command}\n" if append_newline else command
    try:
        connection.write(payload.encode("utf-8"))
        connection.flush()
    except Exception as error:
        print(f"[TX ERROR] {error}", file=sys.stderr)
        return False

    print(f"[TX] {command}")
    return True


def read_response(connection: serial.Serial, timeout: float) -> str:
    deadline = time.monotonic() + max(timeout, 0.0)
    buffer = bytearray()

    while time.monotonic() < deadline:
        waiting = connection.in_waiting
        if waiting > 0:
            buffer.extend(connection.read(waiting))
            if b"\n" in buffer:
                break
        else:
            time.sleep(POLL_INTERVAL)

    if not buffer:
        return ""

    return buffer.decode("utf-8", errors="replace").strip()


def run_single_command(
    connection: serial.Serial,
    command: str,
    append_newline: bool,
    timeout: float,
    require_response: bool,
) -> int:
    if not send_command(connection, command, append_newline):
        print("結果：命令送出失敗。")
        return 1

    response = read_response(connection, timeout)

    if response:
        print(f"[RX] {response}")
    else:
        print("[RX] 沒有收到任何回應")

    if response.lower() == command.lower():
        print("結果：命令已送出，且收到預期回應。")
        return 0

    if response:
        print("結果：命令已送出，設備有回應，但內容和預期不同。")
        return 0

    if require_response:
        print("結果：命令已送出，但沒有收到回應。請檢查 TX/RX/GND、baudrate、newline 設定。")
        return 3

    print("結果：命令已成功送出。設備沒有回應也可能是正常行為。")
    return 0


def run_interactive(connection: serial.Serial, append_newline: bool, timeout: float) -> int:
    print("Interactive mode 已啟動。")
    print("輸入 on 或 off 送出命令；輸入 read 只讀取回應；輸入 quit 離開。")

    while True:
        try:
            raw_input_value = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n離開測試。")
            return 0

        if not raw_input_value:
            continue

        command = raw_input_value.lower()

        if command in {"quit", "exit", "q"}:
            print("離開測試。")
            return 0

        if command == "read":
            response = read_response(connection, timeout)
            print(f"[RX] {response}" if response else "[RX] 沒有收到任何回應")
            continue

        if not send_command(connection, raw_input_value, append_newline):
            continue
        response = read_response(connection, timeout)
        print(f"[RX] {response}" if response else "[RX] 沒有收到任何回應")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    print("UART 測試開始")
    print(f"Port: {args.port}")
    print(f"Baudrate: {args.baudrate}")
    print(f"Timeout: {args.timeout}s")
    print("接線應為：RPi Pin 6 -> GND, Pin 8 -> 對方 RX, Pin 10 -> 對方 TX")

    try:
        connection = serial.Serial(
            port=args.port,
            baudrate=args.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0,
            write_timeout=max(args.timeout, 0.0),
        )
    except Exception as error:
        print(f"無法開啟序列埠：{error}", file=sys.stderr)
        return 1

    with connection:
        print("序列埠已開啟。")
        time.sleep(max(args.settle, 0.0))

        connection.reset_input_buffer()
        connection.reset_output_buffer()

        if args.command:
            return run_single_command(
                connection,
                args.command,
                args.newline,
                args.timeout,
                args.require_response,
            )

        return run_interactive(connection, args.newline, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
