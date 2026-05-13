# 果乾 Edge AI 桌面控制台

這是一個使用 `PySide6 + Python` 開發的原生桌面 GUI，目標是在 Raspberry Pi 5 上作為果乾教學系統的中央控制台，整合：

- 相機預覽
- MCU / UART 控制 (通訊協議 V1.2)
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
- UART `ON` / `STOP` / `PAUSE` 控制
- 支援 `SETTEMP` (設定溫度) 與 `SETTIME` (設定時間) 指令
- 即時解析並顯示來自 Wio Terminal 的 JSON 格式感測器數據 (溫度、濕度)
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

### 1. 硬體控制 (通訊協議 V1.2)

- `啟動機器 (ON)`：送出 `ON` 開始運作
- `暫停機器 (PAUSE)`：送出 `PAUSE` 暫停運作並保持時間
- `停止歸零 (STOP)`：送出 `STOP` 停止機器並將時間歸零
- `設定溫度`：在進階面板設定乾燥溫度 (送出 `SETTEMPxx`)
- `設定時間`：在進階面板設定乾燥分鐘數 (送出 `SETTIMExxxx`)
- `感測器狀態`：介面會即時顯示解析自 UART 的箱體溫度與濕度
- `開啟獨立相機預覽`：開啟 PySide6 預覽視窗，檢查鏡頭角度與位置

UART 會自動解析 JSON 格式的回傳數據，並將 16 進位數值轉換為易讀的攝氏溫度與百分比濕度。

防呆規則：

- 資料收集執行中，不可按 `停止歸零`
- 推論執行中，不可按 `停止歸零`
- 需要先停止資料收集或推論，才能送出 `STOP`

### UART 實機使用方式

RPi 5 目前採用：

- Port: `/dev/ttyAMA0`
- Baudrate: `115200`
- Format: `8N1`
- Protocol Version: `V1.2`

接線方式：

- RPi Pin `6` -> Wio Terminal `GND`
- RPi Pin `8` -> Wio Terminal `RX`
- RPi Pin `10` -> Wio Terminal `TX`

在 GUI 中：

1. 將序列埠設為 `/dev/ttyAMA0`
2. 點 `連線 UART`
3. 使用 `啟動`、`暫停` 或 `停止` 按鈕控制機器
4. 在「參數進階設定」中調整溫度與時間並按下設定鈕

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

之後回到 GUI：

1. 按 `掃描模型`
2. 在下拉選單選擇你剛放進去的 `.pt`
3. 按 `開始推論`

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
