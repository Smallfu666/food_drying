# 果乾 Edge AI 桌面控制台

這是一個使用 `PySide6 + Python` 開發的原生桌面 GUI，目標是在 Raspberry Pi 5 上作為果乾教學系統的中央控制台，整合：

- 相機預覽
- MCU / UART 控制
- 資料收集
- YOLOv8 本地推論
- 模型資料夾管理

目前版本可先在 macOS 上用 `uv` 驗證，之後再搬到 Raspberry Pi 5 上測試。

## 功能

- 單欄式可捲動桌面 GUI
- 固定深色模式，適合 Raspberry Pi 桌面與教學現場投影
- PySide6 pop-out 相機預覽視窗
- 背景執行緒資料收集，並在資料收集區內顯示固定尺寸即時相機畫面
- 依小時切分的資料集輸出結構
- UART `on` / `off` / PWM 控制
- 掃描 `models/` 內的 `.pt` 與未來 `.hef`
- 內建 `Mock` 推論模式，沒有模型也能先測完整流程

## 專案結構

```text
app/
  core/
  services/
  ui/
datasets/
models/
main.py
pyproject.toml
```

## 在 macOS 上執行

1. 安裝相依

```bash
uv sync
```

如果你要使用自己的 `.pt` 模型做 YOLOv8 推論，請改成：

```bash
uv sync --extra yolo
```

2. 啟動程式

```bash
./.venv/bin/python main.py
```

## 在 Raspberry Pi 5 上執行

1. 安裝 Python 3.11+ 與 `uv`
2. 將整個專案複製到 Raspberry Pi 5
3. 建議先安裝中文字體：

```bash
./scripts/install_rpi_fonts.sh
```

如果不想執行 script，也可以手動安裝：

```bash
sudo apt update
sudo apt install -y fonts-noto-cjk fonts-noto-color-emoji
fc-cache -fv
```

4. 在專案目錄執行：

```bash
uv sync
./.venv/bin/python main.py
```

如果 Raspberry Pi 5 上要使用 `.pt` 模型推論，請改成：

```bash
uv sync --extra yolo
./.venv/bin/python main.py
```

注意事項：

- 需要在有桌面環境的情況下執行，因為相機預覽與推論結果需要顯示視窗
- UI 目前固定使用深色模式，不再提供切換
- 預設 UART port 是 `/dev/ttyAMA0`
- 如果 MCU 使用其他序列埠，可在 GUI 中直接修改
- 目前 `.pt` 會用本地 YOLOv8 backend 跑，`.hef` backend 介面已預留但尚未實作 Hailo-10H runtime
- 如果只想先測 GUI、相機與 Mock mode，用 `uv sync` 即可
- 如果要真的載入 `.pt` 模型，才需要 `uv sync --extra yolo`

## 如何使用

### 1. 硬體控制

- `開啟機器`：送出 `on`
- `關閉機器`：送出 `off`
- `開啟獨立相機預覽`：開啟 PySide6 預覽視窗，檢查鏡頭角度與位置
- `顯示 UART / 風扇進階設定`：展開 UART 連線、掃描序列埠與風扇 PWM 控制

UART 目前以「命令成功送出」作為主要成功條件；設備若沒有回傳字串，也可能屬於正常行為。

防呆規則：

- 資料收集執行中，不可按 `關閉機器`
- 推論執行中，不可按 `關閉機器`
- 需要先停止資料收集或推論，才能送出 `off`

### UART 實機使用方式

RPi 5 目前採用：

- Port: `/dev/ttyAMA0`
- Baudrate: `9600`
- Format: `8N1`
- Commands: `on` / `off`

接線方式：

- RPi Pin `6` -> 對方 `GND`
- RPi Pin `8` -> 對方 `RX`
- RPi Pin `10` -> 對方 `TX`

在 GUI 中：

1. 將序列埠設為 `/dev/ttyAMA0`
2. 點 `連線 UART`
3. 點 `開啟機器` 或 `關閉機器`

如果只是要先在終端測試 UART，可使用：

```bash
./.venv/bin/python scripts/uart_probe.py --port /dev/ttyAMA0 --command on
./.venv/bin/python scripts/uart_probe.py --port /dev/ttyAMA0 --command off
```

如果設備需要換行，可再試：

```bash
./.venv/bin/python scripts/uart_probe.py --port /dev/ttyAMA0 --command on --newline
```

如果你要把「沒有回應」也視為失敗，再加：

```bash
./.venv/bin/python scripts/uart_probe.py --port /dev/ttyAMA0 --command on --require-response
```

### 2. 資料收集

- 設定 `持續時間（小時）`
- 設定 `拍攝間隔（分鐘）`
- 按 `開始收集資料`
- 資料收集開始後，中間區塊會顯示目前相機即時畫面
- 系統會自動建立資料夾，例如：

```text
datasets/2026-04-01_14-30-00/
  hour_01/
  hour_02/
```

- 每次拍攝的照片會存在對應的小時資料夾中
- `開啟目前資料夾` 可直接打開資料集輸出目錄
- `開啟 AI Maker` 可直接打開 AI Maker 網站
- 資料收集中會暫停獨立相機預覽與推論按鈕，避免搶用同一台相機

### 3. 邊緣推論

- 將模型放進 `models/`
- 按 `掃描模型`
- 在下拉選單選擇模型
- 按 `開始推論`
- 系統會打開相機並在 OpenCV 視窗顯示即時推論結果
- `顯示除錯資訊 / 系統狀態` 可展開 log，預設會先隱藏，避免干擾教學流程

## AI Maker 訓練後的模型要放哪裡

如果你在 AI Maker 訓練好模型並下載回來，請把模型檔放到專案根目錄下的 `models/` 資料夾。

範例：

```text
food_drying/
  models/
    best.pt
```

也就是放在：

[`/Users/nick/Documents/projects/food_drying/models`](/Users/nick/Documents/projects/food_drying/models)

之後回到 GUI：

1. 按 `掃描模型`
2. 在下拉選單選擇你剛放進去的 `.pt`
3. 按 `開始推論`

如果 AI Maker 下載下來的是壓縮檔，先解壓縮，再把裡面的 `.pt` 模型檔放進 `models/`。

## 沒有模型時如何測試

如果目前還沒有自己的模型，可以直接選：

- `__mock__ (Mock)`

這樣一樣能測：

- 相機是否能開啟
- OpenCV pop-out 視窗是否正常
- UI 狀態 log 是否正常
- 推論流程是否能完整跑通

## 備註

- 目前是本地 YOLOv8 推論版本
- Hailo-10H 整合會在後續版本處理
- 未來若要接 Hailo，建議保留 `.pt` 與 `.hef` 雙後端架構
