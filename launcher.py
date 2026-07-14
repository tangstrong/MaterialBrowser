# -*- coding: utf-8 -*-
"""
启动器 — 捕获所有启动错误写入 log 文件
"""
import sys, os, traceback

LOG_PATH = os.path.join(os.path.dirname(sys.executable), "startup.log")

def log(msg):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=" * 40)
log("MaterialBrowser 启动中...")
log(f"时间: {__import__('datetime').datetime.now()}")
log(f"Python: {sys.version}")
log(f"Executable: {sys.executable}")
log(f"CWD: {os.getcwd()}")
log(f"Args: {sys.argv}")

try:
    log("导入 PyQt6...")
    sys.stdout.flush()
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    log("PyQt6 导入成功")

    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    log("QApplication 创建成功")

    # 深色主题
    from styles import GLOBAL_QSS
    app.setStyleSheet(GLOBAL_QSS)
    log("主题设置成功")

    from ui_main import MainWindow
    log("MainWindow 导入成功")

    win = MainWindow()
    log("MainWindow 实例化成功")

    win.show()
    log("主窗口显示 — 进入事件循环")
    sys.stdout.flush()

    log("=== 启动成功 ===")
    sys.exit(app.exec())

except Exception as e:
    tb = traceback.format_exc()
    log(f"启动失败: {e}")
    log(tb)
    sys.stderr.write(f"启动失败: {e}\n{tb}\n")
    sys.stderr.flush()
    input("按回车键退出...")
    sys.exit(1)
