# -*- coding: utf-8 -*-
"""全局深色主题 QSS 样式表"""

C = {
    "bg_root":    "#0b0d14",
    "bg_panel":   "#13161f",
    "bg_card":    "#1a1d27",
    "bg_input":   "#1e2233",
    "border":     "#252838",
    "border_hi":  "#353a52",
    "accent":     "#f0a500",
    "accent_dim": "#c07800",
    "blue":       "#4fc3f7",
    "orange":     "#ff8a65",
    "purple":     "#ce93d8",
    "green":      "#69f0ae",
    "red":        "#ef5350",
    "text_hi":    "#f0f2ff",
    "text_main":  "#d0d4e8",
    "text_sub":   "#8890a8",
    "text_dim":   "#454860",
    "scroll":     "#252838",
}

GLOBAL_QSS = f"""
* {{ box-sizing: border-box; outline: none; }}

QMainWindow, QWidget {{
    background-color: {C['bg_root']};
    color: {C['text_main']};
    font-family: 'Segoe UI', 'Microsoft YaHei UI', 'PingFang SC', sans-serif;
    font-size: 12px;
}}

QScrollBar:vertical {{ background: {C['bg_panel']}; width: 7px; border-radius: 4px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {C['scroll']}; border-radius: 4px; min-height: 24px; }}
QScrollBar::handle:vertical:hover {{ background: {C['border_hi']}; }}
QScrollBar:horizontal {{ background: {C['bg_panel']}; height: 7px; border-radius: 4px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {C['scroll']}; border-radius: 4px; min-width: 24px; }}
QScrollBar::handle:horizontal:hover {{ background: {C['border_hi']}; }}

QPushButton {{
    background: {C['bg_card']};
    border: 1px solid {C['border']};
    color: {C['text_main']};
    padding: 6px 16px;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton:hover {{
    background: {C['bg_input']};
    border-color: {C['accent']};
    color: {C['accent']};
}}
QPushButton:pressed {{ background: {C['bg_panel']}; border-color: {C['accent_dim']}; }}
QPushButton:disabled {{ color: {C['text_dim']}; border-color: {C['border']}; background: {C['bg_panel']}; }}

QPushButton#btnAccent {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {C['accent']}, stop:1 #e09000);
    color: #000; border: none; font-weight: 700; border-radius: 7px;
}}
QPushButton#btnAccent:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ffb820, stop:1 {C['accent']});
}}

QPushButton#btnDanger {{
    background: transparent; border: 1px solid #5a2020; color: #ef9090; border-radius: 7px;
}}
QPushButton#btnDanger:hover {{ background: #2a1010; border-color: {C['red']}; color: {C['red']}; }}

QComboBox {{
    background: {C['bg_input']}; border: 1px solid {C['border']};
    color: {C['text_main']}; padding: 5px 10px; border-radius: 7px; min-width: 140px;
}}
QComboBox:hover {{ border-color: {C['border_hi']}; }}
QComboBox:focus {{ border-color: {C['accent']}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent; border-right: 4px solid transparent;
    border-top: 5px solid {C['text_sub']}; margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background: {C['bg_card']}; border: 1px solid {C['border_hi']};
    color: {C['text_main']}; selection-background-color: {C['bg_input']};
    selection-color: {C['accent']}; border-radius: 6px; padding: 4px;
}}

QLineEdit {{
    background: {C['bg_input']}; border: 1px solid {C['border']};
    color: {C['text_main']}; padding: 5px 10px; border-radius: 7px;
}}
QLineEdit:hover {{ border-color: {C['border_hi']}; }}
QLineEdit:focus {{ border-color: {C['accent']}; }}
QLineEdit::placeholder {{ color: {C['text_dim']}; }}

QCheckBox {{ color: {C['text_sub']}; spacing: 7px; padding: 4px 6px; border-radius: 5px; }}
QCheckBox:hover {{ background: {C['bg_card']}; color: {C['text_main']}; }}
QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {C['border_hi']};
    border-radius: 3px; background: {C['bg_input']}; }}
QCheckBox::indicator:checked {{ background: {C['accent']}; border-color: {C['accent']}; image: none; }}
QCheckBox::indicator:hover {{ border-color: {C['accent']}; }}

QTableWidget {{
    background: {C['bg_panel']}; border: none; gridline-color: #0f1117;
    color: {C['text_sub']}; selection-background-color: {C['bg_card']};
    selection-color: {C['text_hi']}; alternate-background-color: #111420;
}}
QTableWidget::item {{ padding: 4px 10px; border-bottom: 1px solid #0f1117; }}
QTableWidget::item:hover {{ background: {C['bg_card']}; color: {C['text_hi']}; }}
QTableWidget::item:selected {{ background: #252a3a; color: {C['text_hi']}; }}
QHeaderView::section {{
    background: {C['bg_panel']}; color: {C['text_dim']}; font-size: 10px;
    font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;
    padding: 5px 10px; border: none; border-bottom: 2px solid {C['border']};
    border-right: 1px solid {C['border']};
}}
QHeaderView::section:hover {{ background: {C['bg_card']}; color: {C['text_main']}; }}

QSplitter::handle {{ background: {C['border']}; }}
QSplitter::handle:hover {{ background: {C['accent']}; }}
QSplitter::handle:horizontal {{ width: 2px; }}
QSplitter::handle:vertical {{ height: 2px; }}

QProgressBar {{
    background: {C['bg_input']}; border: none; border-radius: 4px;
    height: 5px; text-align: center; color: transparent;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {C['accent']}, stop:1 #ffcc44);
    border-radius: 4px;
}}

QToolTip {{ background: {C['bg_card']}; color: {C['text_hi']};
    border: 1px solid {C['border_hi']}; border-radius: 6px; padding: 6px 10px; font-size: 11px; }}

QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}

QLabel#labelAccent {{ color: {C['accent']}; font-weight: 700; }}
QLabel#labelDim {{ color: {C['text_dim']}; font-size: 11px; }}
QLabel#labelBadge {{ background: {C['bg_input']}; color: {C['text_sub']};
    border: 1px solid {C['border']}; border-radius: 10px; padding: 2px 10px; font-size: 11px; }}

QFrame#card {{ background: {C['bg_card']}; border: 1px solid {C['border']}; border-radius: 10px; }}
QFrame#separator {{ background: {C['border']}; max-height: 1px; min-height: 1px; }}

QMenu {{ background: {C['bg_card']}; border: 1px solid {C['border_hi']}; border-radius: 8px; padding: 4px; }}
QMenu::item {{ padding: 6px 20px; border-radius: 4px; }}
QMenu::item:selected {{ background: {C['bg_input']}; color: {C['accent']}; }}
"""


def get_colors():
    return C
