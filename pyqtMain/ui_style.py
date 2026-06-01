# -*- coding: utf-8 -*-
"""应用全局 QSS，在 initUi 中一次性应用。"""

APP_STYLESHEET = """
QMainWindow, QWidget#mainCentral {
    background-color: #F0F2F5;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 10pt;
    color: #1F2937;
}
QTabWidget::pane {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    background: #FFFFFF;
    top: -1px;
}
QTabBar::tab {
    background: #E5E7EB;
    color: #4B5563;
    padding: 10px 28px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-width: 72px;
}
QTabBar::tab:selected {
    background: #FFFFFF;
    color: #2563EB;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background: #D1D5DB;
}
QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    margin-top: 14px;
    padding: 12px 10px 10px 10px;
    font-weight: bold;
    color: #374151;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #2563EB;
}
QPushButton {
    background-color: #FFFFFF;
    color: #374151;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 6px 14px;
    min-height: 22px;
}
QPushButton:hover {
    background-color: #F3F4F6;
    border-color: #9CA3AF;
}
QPushButton:pressed {
    background-color: #E5E7EB;
}
QPushButton#btn_1_shoudong {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    font-weight: bold;
}
QPushButton#btn_1_shoudong:hover {
    background-color: #1D4ED8;
}
QPushButton#btn_1_shoudong:pressed {
    background-color: #1E40AF;
}
QPushButton#clear_btn {
    background-color: #FEF2F2;
    color: #B91C1C;
    border: 1px solid #FECACA;
}
QPushButton#clear_btn:hover {
    background-color: #FEE2E2;
}
QLineEdit, QComboBox, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 4px 8px;
    selection-background-color: #BFDBFE;
}
/* 接单群/飞单群：宽度以 main.ui 的 geometry 为准，不随群名撑开 */
QComboBox#cbx_2_1,
QComboBox#cbx_2_2 {
    max-width: 211px;
    min-width: 211px;
}
QComboBox#cbx_2_1 QAbstractItemView,
QComboBox#cbx_2_2 QAbstractItemView {
    min-width: 280px;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 1px solid #2563EB;
}
QTextBrowser#chat_view {
    background-color: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 8px;
}
/* 主窗口全局 QSS 后，QTextBrowser 自带滚动条常变窄/不可见，需单独指定 */
QTextBrowser#chat_view QScrollBar:vertical {
    width: 12px;
    background: #E5E7EB;
    margin: 2px 0 2px 2px;
    border-radius: 6px;
}
QTextBrowser#chat_view QScrollBar::handle:vertical {
    background: #9CA3AF;
    border-radius: 6px;
    min-height: 28px;
}
QTextBrowser#chat_view QScrollBar::handle:vertical:hover {
    background: #6B7280;
}
QTextBrowser#chat_view QScrollBar::add-line:vertical,
QTextBrowser#chat_view QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
}
QTextBrowser#chat_view QScrollBar:horizontal {
    height: 12px;
    background: #E5E7EB;
    margin: 2px 2px 2px 0;
    border-radius: 6px;
}
QTextBrowser#chat_view QScrollBar::handle:horizontal {
    background: #9CA3AF;
    border-radius: 6px;
    min-width: 28px;
}
QTextBrowser#chat_view QScrollBar::handle:horizontal:hover {
    background: #6B7280;
}
QTextBrowser#chat_view QScrollBar::add-line:horizontal,
QTextBrowser#chat_view QScrollBar::sub-line:horizontal {
    width: 0px;
    background: none;
}
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    gridline-color: #F3F4F6;
}
QHeaderView::section {
    background-color: #F3F4F6;
    color: #374151;
    padding: 6px;
    border: none;
    font-weight: bold;
}
QCheckBox, QRadioButton {
    spacing: 8px;
    color: #374151;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
}
QLabel#lb_1_fdCount {
    color: #1E40AF;
    font-size: 13pt;
    font-weight: bold;
}
QLabel#lb_1_7 {
    color: #6B7280;
    font-size: 9pt;
}
QLabel#lb_1_0 {
    background-color: #EEF2FF;
    color: #4338CA;
    border-radius: 4px;
    padding: 2px 8px;
}
"""


def apply_app_style(window):
    window.setStyleSheet(APP_STYLESHEET)
    if hasattr(window, "centralwidget"):
        window.centralwidget.setObjectName("mainCentral")
