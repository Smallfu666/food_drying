#!/usr/bin/env bash
set -euo pipefail

sudo apt update
sudo apt install -y fonts-noto-cjk fonts-noto-color-emoji
fc-cache -fv

echo "Noto CJK fonts installed. Restart the GUI to apply the font changes."
