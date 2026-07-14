# -*- coding: utf-8 -*-
"""
MaterialBrowser - 程序入口
"""
import sys, os, logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# ── 日志 ─────────────────────────────────────────────────────────────────────
LOG_DIR = Path.home() / ".material_browser"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger(__name__)


# ── 入口 ─────────────────────────────────────────────────────────────────────
def main():
    logger.info("=== MaterialBrowser 启动 ===")

    # 允许外部拖入 Excel 文件
    excel_path = None
    for arg in sys.argv[1:]:
        if os.path.isfile(arg) and arg.endswith((".xlsx", ".xls")):
            excel_path = arg
            logger.info(f"接受拖入文件: {excel_path}")
            break

    app = QApplication(sys.argv)

    # 深色主题
    from styles import GLOBAL_QSS
    app.setStyleSheet(GLOBAL_QSS)

    from ui_main import MainWindow
    win = MainWindow(excel_path=excel_path)
    win.show()

    logger.info("主窗口已显示")
    sys.exit(app.exec())
