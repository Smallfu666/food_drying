# Project Overview

**Name:** food-drying-gui (果乾 Edge AI 控制台)
**Type:** Python Desktop Application
**Purpose:** A central desktop control console for an educational fruit drying Edge AI system, designed primarily for the Raspberry Pi 5. It integrates camera preview, hardware control via UART (for fan/power), image dataset collection, and local edge inference (YOLOv8) into a single, scrollable UI.

## Key Technologies
- **Language:** Python 3.11+
- **GUI Framework:** PySide6 (Qt)
- **Computer Vision:** OpenCV (`opencv-python`)
- **Hardware Communication:** `pyserial` (UART)
- **Machine Learning:** YOLOv8 (`ultralytics` - optional dependency)
- **Dependency Management:** `uv`

## Architecture
The application is structured into clearly separated domains:
- `app/core/`: Configuration, centralized logging, and UI theme management.
- `app/services/`: Business logic and hardware interactions (e.g., `CameraService`, `UARTService`, `DataCollectionService`, `InferenceService`).
- `app/ui/`: PySide6 view components, including the `MainWindow`, pop-out `CameraPreviewWindow`, and modular panels (`HardwarePanel`, `CollectionPanel`, `InferencePanel`).
- `datasets/`: Automatically generated directory for saving images during the data collection process (organized by timestamp).
- `models/`: Directory for placing trained models (e.g., `.pt` files).
- `scripts/`: Utility scripts (e.g., `uart_probe.py` for testing serial connections).

## Building and Running

### 1. Installation
The project uses `uv` for fast dependency management.

For basic GUI, camera, and mock inference testing:
```bash
uv sync
```

To enable actual YOLOv8 `.pt` model inference:
```bash
uv sync --extra yolo
```

*(On Raspberry Pi 5, you may need to install fonts via `./scripts/install_rpi_fonts.sh` first to ensure correct UI rendering.)*

### 2. Execution
Run the main application script using the virtual environment created by `uv`:
```bash
./.venv/bin/python main.py
```

## Development Conventions

- **Typing:** Extensive use of Python type hints is expected. Files often include `from __future__ import annotations`.
- **UI Event Handling:** Relies heavily on Qt's Signal/Slot mechanism. The `MainWindow` defines a `MainWindowSignals` class to coordinate state changes between services and UI panels.
- **Concurrency:** Services that perform blocking operations (like data collection loops or hardware access) should run safely without freezing the PySide6 main thread (e.g., using QThread or threading, as seen with camera locks).
- **Hardcoded Styling:** The application enforces a fixed dark mode theme (`ThemeManager`) optimized for Raspberry Pi displays in educational environments.
- **Graceful Degradation:** The UI implements safeguards (e.g., disabling the power-off button during data collection or inference) and offers a "Mock" inference mode when no actual models are present in the `models/` directory.