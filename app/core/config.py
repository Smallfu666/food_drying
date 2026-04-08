from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = PROJECT_ROOT / "datasets"
MODELS_DIR = PROJECT_ROOT / "models"
AI_MAKER_URL = "https://aimaker.com.tw/zh-TW"

DEFAULT_PREVIEW_RESOLUTION = (1280, 720)
DEFAULT_CAPTURE_RESOLUTION = (2560, 1440)
SUPPORTED_MODEL_SUFFIXES = {".pt", ".hef"}
SERIAL_BAUDRATE = 9600
DEFAULT_SERIAL_PORT = "/dev/ttyAMA0"
UART_ON_COMMAND = "on"
UART_OFF_COMMAND = "off"
WINDOW_TITLE = "果乾 Edge AI 控制台"
