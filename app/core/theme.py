from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class ThemePalette:
    name: str
    window: str
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


LIGHT_THEME = ThemePalette(
    name="light",
    window="#F4F7FB",
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
)

DARK_THEME = ThemePalette(
    name="dark",
    window="#0F172A",
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
    danger="#FB923C",
)


class ThemeManager:
    def __init__(self) -> None:
        self.current_theme = LIGHT_THEME

    def toggle(self) -> ThemePalette:
        self.current_theme = DARK_THEME if self.current_theme.name == "light" else LIGHT_THEME
        return self.current_theme

    def apply(self, app: QApplication) -> None:
        theme = self.current_theme
        app.setStyleSheet(
            f"""
            QWidget {{
                background-color: {theme.window};
                color: {theme.text};
                font-family: "SF Pro Text", "PingFang TC", "Noto Sans TC", "Helvetica Neue", "Arial";
                font-size: 14px;
            }}
            QMainWindow {{
                background-color: {theme.window};
            }}
            QFrame#panel {{
                background-color: {theme.panel};
                border: 1px solid {theme.border};
                border-radius: 18px;
            }}
            QFrame#topBar {{
                background-color: transparent;
            }}
            QLabel#titleLabel {{
                font-size: 24px;
                font-weight: 700;
            }}
            QLabel#sectionTitle {{
                font-size: 18px;
                font-weight: 700;
            }}
            QLabel#hintText {{
                color: {theme.muted_text};
                font-size: 12px;
            }}
            QLabel#valueChip {{
                background-color: {theme.panel_alt};
                border: 1px solid {theme.border};
                border-radius: 12px;
                padding: 6px 10px;
                font-weight: 600;
            }}
            QPushButton {{
                background-color: {theme.panel_alt};
                border: 1px solid {theme.border};
                border-radius: 12px;
                padding: 10px 14px;
                font-weight: 600;
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
                color: {theme.danger};
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit {{
                background-color: {theme.input_bg};
                border: 1px solid {theme.border};
                border-radius: 12px;
                padding: 10px 12px;
                selection-background-color: {theme.accent};
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
                font-family: "SF Mono", "Menlo", "Monaco", "Courier New";
                font-size: 12px;
            }}
            QScrollBar:vertical {{
                width: 12px;
                background: transparent;
                margin: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme.border};
                border-radius: 6px;
                min-height: 24px;
            }}
            """
        )
