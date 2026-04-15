from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class ThemePalette:
    name: str
    window: str
    window_accent: str
    panel: str
    panel_alt: str
    text: str
    muted_text: str
    border: str
    accent: str
    accent_hover: str
    accent_pressed: str
    subtle_hover: str
    input_bg: str
    danger: str
    danger_bg: str
    danger_hover: str


LIGHT_THEME = ThemePalette(
    name="light",
    window="#F4F7FB",
    window_accent="#E7F5EF",
    panel="#FFFFFF",
    panel_alt="#F8FAFC",
    text="#112033",
    muted_text="#617286",
    border="#D9E2EC",
    accent="#0F766E",
    accent_hover="#0D9488",
    accent_pressed="#115E59",
    subtle_hover="#EEF4F8",
    input_bg="#FFFFFF",
    danger="#C2410C",
    danger_bg="#FFF1F2",
    danger_hover="#FFE4E6",
)

DARK_THEME = ThemePalette(
    name="dark",
    window="#0F172A",
    window_accent="#12312D",
    panel="#111827",
    panel_alt="#1E293B",
    text="#E5EEF8",
    muted_text="#9FB1C5",
    border="#334155",
    accent="#14B8A6",
    accent_hover="#2DD4BF",
    accent_pressed="#0F766E",
    subtle_hover="#1E293B",
    input_bg="#0B1120",
    danger="#FB7185",
    danger_bg="#3A1A24",
    danger_hover="#4A1F2B",
)


class ThemeManager:
    def __init__(self) -> None:
        self.current_theme = DARK_THEME

    def toggle(self) -> ThemePalette:
        self.current_theme = DARK_THEME if self.current_theme.name == "light" else LIGHT_THEME
        return self.current_theme

    def apply(self, app: QApplication) -> None:
        theme = self.current_theme
        app.setStyleSheet(
            f"""
            QWidget {{
                background-color: transparent;
                color: {theme.text};
                font-family: "Noto Sans CJK TC", "Noto Sans TC", "Source Han Sans TW", "PingFang TC", "Microsoft JhengHei", "DejaVu Sans";
                font-size: 14px;
            }}
            QMainWindow {{
                background-color: {theme.window};
            }}
            QScrollArea#mainScrollArea {{
                border: none;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {theme.window_accent},
                    stop: 0.34 {theme.window},
                    stop: 1 {theme.window}
                );
            }}
            QScrollArea#mainScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
            QWidget#contentColumn {{
                background-color: transparent;
            }}
            QFrame#heroPanel {{
                background-color: {theme.panel};
                border: 1px solid {theme.border};
                border-radius: 24px;
            }}
            QFrame#panel {{
                background-color: {theme.panel};
                border: 1px solid {theme.border};
                border-radius: 22px;
            }}
            QFrame#topBar {{
                background-color: transparent;
            }}
            QLabel#heroBadge {{
                background-color: {theme.panel_alt};
                border: 1px solid {theme.border};
                border-radius: 12px;
                color: {theme.accent_pressed};
                font-size: 12px;
                font-weight: 700;
                padding: 6px 10px;
            }}
            QLabel#stepBadge {{
                background-color: {theme.accent};
                border-radius: 14px;
                color: white;
                font-size: 12px;
                font-weight: 800;
                padding: 6px 10px;
            }}
            QLabel#titleLabel {{
                font-size: 28px;
                font-weight: 800;
            }}
            QLabel#sectionTitle {{
                font-size: 20px;
                font-weight: 800;
            }}
            QLabel#subsectionTitle {{
                font-size: 15px;
                font-weight: 800;
            }}
            QLabel#hintText {{
                color: {theme.muted_text};
                font-size: 12px;
            }}
            QLabel#fieldLabel {{
                color: {theme.muted_text};
                font-size: 12px;
                font-weight: 700;
            }}
            QLabel#valueChip {{
                background-color: {theme.panel_alt};
                border: 1px solid {theme.border};
                border-radius: 12px;
                padding: 6px 10px;
                font-weight: 600;
            }}
            QLabel#statusChip {{
                background-color: {theme.panel_alt};
                border: 1px solid {theme.border};
                border-radius: 14px;
                color: {theme.text};
                padding: 10px 12px;
                font-weight: 700;
            }}
            QLabel#cameraPreview {{
                background-color: {theme.input_bg};
                border: 1px solid {theme.border};
                border-radius: 18px;
                color: {theme.muted_text};
                font-weight: 700;
            }}
            QPushButton {{
                background-color: {theme.panel_alt};
                border: 1px solid {theme.border};
                border-radius: 14px;
                padding: 12px 16px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {theme.subtle_hover};
            }}
            QPushButton:pressed {{
                padding-top: 11px;
                padding-bottom: 9px;
            }}
            QPushButton[primary="true"] {{
                background-color: {theme.accent};
                color: white;
                border: none;
            }}
            QPushButton[primary="true"]:hover {{
                background-color: {theme.accent_hover};
            }}
            QPushButton[primary="true"]:pressed {{
                background-color: {theme.accent_pressed};
            }}
            QPushButton[danger="true"] {{
                background-color: {theme.danger_bg};
                border: 1px solid {theme.danger};
                color: {theme.danger};
            }}
            QPushButton[danger="true"]:hover {{
                background-color: {theme.danger_hover};
            }}
            QPushButton[danger="true"]:pressed {{
                background-color: {theme.danger_bg};
            }}
            QPushButton:disabled {{
                background-color: {theme.input_bg};
                border: 1px solid {theme.border};
                color: {theme.muted_text};
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit {{
                background-color: {theme.input_bg};
                border: 1px solid {theme.border};
                border-radius: 14px;
                padding: 11px 12px;
                selection-background-color: {theme.accent};
            }}
            QSpinBox::up-button,
            QSpinBox::down-button,
            QDoubleSpinBox::up-button,
            QDoubleSpinBox::down-button {{
                width: 0;
                border: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 28px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme.panel};
                border: 1px solid {theme.border};
                selection-background-color: {theme.accent};
                selection-color: white;
            }}
            QSlider::groove:horizontal {{
                height: 6px;
                background: {theme.border};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {theme.accent};
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            QCheckBox {{
                spacing: 8px;
                font-weight: 600;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 11px;
                border: 1px solid {theme.border};
                background-color: {theme.panel_alt};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme.accent};
                border: none;
            }}
            QPlainTextEdit {{
                font-family: "Noto Sans Mono CJK TC", "Noto Sans Mono", "DejaVu Sans Mono", "Menlo", "Monaco";
                font-size: 12px;
            }}
            QScrollBar:vertical {{
                width: 16px;
                background: {theme.panel_alt};
                margin: 0;
                border-left: 1px solid {theme.border};
            }}
            QScrollBar::handle:vertical {{
                background: {theme.muted_text};
                border-radius: 7px;
                margin: 3px;
                min-height: 24px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme.accent};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
                border: none;
                background: transparent;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            QScrollBar:horizontal {{
                height: 0;
                background: transparent;
            }}
            """
        )
