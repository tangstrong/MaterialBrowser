# -*- coding: utf-8 -*-
"""主窗口"""
import os, sys, logging
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QLineEdit, QLabel, QFileDialog, QMessageBox,
    QSplitter, QScrollArea, QFrame, QCheckBox, QProgressBar, QToolBar,
    QHeaderView, QAbstractItemView, QApplication, QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread, pyqtSlot, QSize
from PyQt6.QtGui import QAction
from styles import C, GLOBAL_QSS, get_colors
from data_manager import (
    DataWorker, AXES_DEF, FILTER_DEFS, COLOR_MAP,
    fmt_val, DB_PATH,
)
from chart_widget import ChartWidget

logger = logging.getLogger(__name__)


class MainWindow(QWidget):
    def __init__(self, excel_path=None):
        super().__init__()
        self.df = None
        self.filtered_df = None
        self.excel_path = excel_path
        self._build_ui()
        self._load_data()
        QApplication.instance().setProperty('_mainWindow', self)

    # ── UI 建构 ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setWindowTitle("MaterialBrowser — Covestro 材料浏览器")
        self.setMinimumSize(1200, 700)
        self.move(100, 80)

        # 主布局
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # 左侧栏
        sidebar = self._build_sidebar()
        sidebar.setFixedWidth(260)

        # 主内容区
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(8)

        # 工具栏
        toolbar = self._build_toolbar()
        content_layout.addWidget(toolbar)

        # 散点图
        self.chart = ChartWidget()
        self.chart.setMinimumHeight(320)
        content_layout.addWidget(self.chart, stretch=2)

        # 表格
        self.table = self._build_table()
        content_layout.addWidget(self.table, stretch=3)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(sidebar)
        splitter.addWidget(content)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

    def _build_sidebar(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("card")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        # 标题
        lbl = QLabel("🔍 材料筛选")
        lbl.setObjectName("labelAccent")
        lbl.setStyleSheet(f"font-size:14px; font-weight:700; margin-bottom:4px;")
        lay.addWidget(lbl)

        # 文件信息
        self.file_lbl = QLabel("未加载数据")
        self.file_lbl.setObjectName("labelDim")
        lay.addWidget(self.file_lbl)

        sep = QFrame(); sep.setObjectName("separator"); lay.addWidget(sep)

        # 筛选器
        self.filter_widgets = {}
        for fid, fdef in FILTER_DEFS.items():
            group = QVBoxLayout()
            title = QLabel(fdef["label"])
            title.setStyleSheet(f"font-size:11px; color:{C['text_dim']}; margin-top:4px;")
            group.addWidget(title)
            for val in fdef["values"]:
                cb = QCheckBox(val)
                cb.setStyleSheet(f"font-size:11px; padding:2px 4px;")
                cb.stateChanged.connect(self._on_filter_changed)
                group.addWidget(cb)
            lay.addLayout(group)
            self.filter_widgets[fid] = group

        sep2 = QFrame(); sep2.setObjectName("separator"); lay.addWidget(sep2)

        # 数值筛选
        num_lbl = QLabel("📊 数值范围筛选")
        num_lbl.setStyleSheet(f"font-size:11px; color:{C['text_dim']};")
        lay.addWidget(num_lbl)

        self.num_filters = {}
        for ax in AXES_DEF:
            key = ax["key"]
            if key not in ["Flow", "VST", "Izod", "Modulus", "PCR", "GF"]: continue
            row = QHBoxLayout()
            lbl2 = QLabel(f"{key}:")
            lbl2.setStyleSheet(f"font-size:10px; color:{C['text_sub']}; min-width:50px;")
            lo = QLineEdit(); lo.setPlaceholderText("min"); lo.setFixedWidth(55)
            lo.setStyleSheet("font-size:11px; padding:3px 6px;")
            hi = QLineEdit(); hi.setPlaceholderText("max"); hi.setFixedWidth(55)
            hi.setStyleSheet("font-size:11px; padding:3px 6px;")
            for w in [lo, hi]:
                w.textChanged.connect(self._on_filter_changed)
            row.addWidget(lbl2); row.addWidget(lo); row.addWidget(hi)
            lay.addLayout(row)
            self.num_filters[key] = {"lo": lo, "hi": hi}

        lay.addStretch()
        return frame

    def _build_toolbar(self) -> QWidget:
        bar = QToolBar()
        bar.setMovable(False)
        bar.setIconSize(QSize(16, 16))
        bar.setStyleSheet(f"background:{C['bg_panel']}; border:none; padding:4px;")

        self.btn_import = QPushButton("📂 导入 Excel")
        self.btn_import.setObjectName("btnAccent")
        self.btn_import.clicked.connect(self._import_excel)
        bar.addWidget(self.btn_import)

        bar.addSeparator()

        # X轴
        lbl_x = QLabel("X 轴:")
        lbl_x.setStyleSheet(f"color:{C['text_sub']}; font-size:11px;")
        bar.addWidget(lbl_x)
        self.cb_x = QComboBox()
        for ax in AXES_DEF:
            self.cb_x.addItem(ax["label"], ax["key"])
        self.cb_x.currentIndexChanged.connect(self._on_axis_changed)
        bar.addWidget(self.cb_x)

        bar.addSpacing(10)

        # Y轴
        lbl_y = QLabel("Y 轴:")
        lbl_y.setStyleSheet(f"color:{C['text_sub']}; font-size:11px;")
        bar.addWidget(lbl_y)
        self.cb_y = QComboBox()
        for ax in AXES_DEF:
            self.cb_y.addItem(ax["label"], ax["key"])
        self.cb_y.setCurrentIndex(4)  # Modulus default
        self.cb_y.currentIndexChanged.connect(self._on_axis_changed)
        bar.addWidget(self.cb_y)

        bar.addSpacing(10)

        # 导出
        btn_export = QPushButton("💾 导出图表 PNG")
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export.clicked.connect(self._export_chart)
        bar.addWidget(btn_export)

        bar.addWidget(QLabel())  # spacer
        self.status_lbl = QLabel("就绪")
        self.status_lbl.setObjectName("labelDim")
        bar.addWidget(self.status_lbl)

        return bar

    def _build_table(self) -> QTableWidget:
        t = QTableWidget()
        t.setAlternatingRowColors(True)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.verticalHeader().setVisible(False)
        t.setShowGrid(False)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        t.setSortingEnabled(True)
        t.itemClicked.connect(self._on_table_click)
        return t

    # ── 数据加载 ────────────────────────────────────────────────────────────────
    def _load_data(self):
        self.status_lbl.setText("加载中…")
        self.thread = QThread()
        self.worker = DataWorker(excel_path=self.excel_path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.dataReady.connect(self._on_data_ready)
        self.worker.error.connect(self._on_data_error)
        self.worker.progress.connect(self.status_lbl.setText)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    @pyqtSlot(pd.DataFrame)
    def _on_data_ready(self, df):
        self.df = df
        self.file_lbl.setText(f"共 {len(df)} 条记录")
        self._apply_filters()
        self._populate_table(self.df)
        self.status_lbl.setText(f"已加载 {len(df)} 条")

    @pyqtSlot(str)
    def _on_data_error(self, msg):
        QMessageBox.warning(self, "错误", msg)

    # ── 筛选 ──────────────────────────────────────────────────────────────────
    @pyqtSlot()
    def _on_filter_changed(self):
        self._apply_filters()

    def _apply_filters(self):
        if self.df is None: return
        df = self.df.copy()

        # 分类筛选
        for fid, layout in self.filter_widgets.items():
            checked = [cb.text() for cb in layout.findChildren(QCheckBox) if cb.isChecked()]
            if not checked: continue
            col_map = {"f1": "f1_cat", "f2": "SpecComp", "f3": "MWB", "f5": "PropHigh"}
            col = col_map.get(fid)
            if col and col in df.columns:
                if fid == "f2":
                    mask = df[col].apply(
                        lambda v: any(c in str(v) if pd.notna(v) else "" for c in checked)
                    )
                    df = df[mask]
                else:
                    df = df[df[col].isin(checked)]

        # 数值筛选
        for key, w in self.num_filters.items():
            if key not in df.columns: continue
            lo_val = w["lo"].text().strip()
            hi_val = w["hi"].text().strip()
            if lo_val:
                try: df = df[df[key].astype(float) >= float(lo_val)]
                except: pass
            if hi_val:
                try: df = df[df[key].astype(float) <= float(hi_val)]
                except: pass

        self.filtered_df = df
        self._populate_table(df)
        self._update_chart()

    # ── 散点图 ────────────────────────────────────────────────────────────────
    def _update_chart(self):
        x_key = self.cb_x.currentData()
        y_key = self.cb_y.currentData()
        self.chart.set_data(self.filtered_df or self.df)
        self.chart.set_axes(x_key, y_key)
        self.chart.draw_chart()

    @pyqtSlot()
    def _on_axis_changed(self):
        self._update_chart()

    # ── 表格 ──────────────────────────────────────────────────────────────────
    def _populate_table(self, df):
        if df is None or df.empty:
            self.table.setRowCount(0)
            return
        cols = ["Grade", "f1_cat", "Flow", "FR_raw", "VST", "Izod", "Modulus", "PCR", "GF", "MWB", "Customer", "IMCare"]
        show_cols = [c for c in cols if c in df.columns]
        self.table.setColumnCount(len(show_cols))
        self.table.setHorizontalHeaderLabels(show_cols)
        self.table.setRowCount(len(df))
        for ri, (_, row) in enumerate(df.iterrows()):
            for ci, col in enumerate(show_cols):
                v = row.get(col, None)
                item = QTableWidgetItem(fmt_val(v) if col != "Grade" else str(v) if v else "")
                if col == "Grade":
                    item.setForeground(QApplication.palette().highlightedText())
                elif col in NUMERIC_COLS and col in df.columns:
                    try:
                        num = float(row[col])
                        if not np.isnan(num): item.setText(str(int(num)) if num == int(num) else f"{num:.2f}")
                    except: pass
                self.table.setItem(ri, ci, item)
        self.table.resizeColumnsToContents()
        self.table.verticalHeader() or None
        if show_cols:
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

    def _on_table_click(self, item):
        row = item.row()
        grade = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
        if self.df is not None:
            match = self.df[self.df["Grade"] == grade]
            if not match.empty:
                self._highlight_material(match.index[0])

    # ── 高亮 ──────────────────────────────────────────────────────────────────
    @pyqtSlot(int)
    def highlight_material(self, idx):
        self._highlight_material(idx)

    def _highlight_material(self, idx):
        if self.filtered_df is not None and idx in self.filtered_df.index:
            df_to_chart = self.filtered_df
        else:
            df_to_chart = self.df
        if df_to_chart is not None:
            self.chart.set_data(df_to_chart)
            self._update_chart()

        # 高亮表格行
        for i in range(self.table.rowCount()):
            grade_item = self.table.item(i, 0)
            if grade_item and self.df is not None and idx in self.df.index:
                if self.table.item(i, 0).text() == str(self.df.at[idx, "Grade"]):
                    self.table.selectRow(i)
                    self.table.scrollToItem(self.table.item(i, 0))
                    break

    # ── 操作 ──────────────────────────────────────────────────────────────────
    def _import_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 Excel 文件", "", "Excel 文件 (*.xlsx *.xls);;所有文件 (*)"
        )
        if path:
            self.excel_path = path
            self._load_data()

    def _export_chart(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "导出图表", "material_chart.png", "PNG 图片 (*.png)"
        )
        if path:
            self.chart.export_png(path)
            QMessageBox.information(self, "导出成功", f"图表已保存:\n{path}")
