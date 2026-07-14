# -*- coding: utf-8 -*-
"""matplotlib 散点图组件"""
import matplotlib
matplotlib.use('QtAgg')

# 不 import matplotlib.pyplot，避免触发 Windows 系统目录下的 matplotlibrc 编码问题
# 直接操作 matplotlib.rcParams
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import Qt
from styles import C, get_colors

matplotlib.rcParams.update({
    'axes.facecolor':    C['bg_panel'],
    'figure.facecolor':  C['bg_panel'],
    'axes.edgecolor':    C['border_hi'],
    'axes.labelcolor':   C['text_sub'],
    'xtick.color':       C['text_dim'],
    'ytick.color':       C['text_dim'],
    'text.color':        C['text_main'],
    'grid.color':        C['border'],
    'grid.alpha':        0.4,
})

PALETTE = [C['accent'], C['blue'], C['orange'], C['purple'], C['green']]


class ChartWidget(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(7, 5), dpi=120)
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self.ax.tick_params(labelsize=8)
        self.fig.tight_layout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.df = None
        self.x_key = "Flow"
        self.y_key = "Modulus"
        self.annotate_idx = None
        self.color_col = "f1_cat"
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_hover)
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)

    def set_data(self, df):
        self.df = df

    def set_axes(self, x_key, y_key):
        self.x_key = x_key
        self.y_key = y_key

    def set_color_by(self, col):
        self.color_col = col

    def draw_chart(self, highlight_indices=None):
        if self.df is None:
            self.ax.clear()
            self.ax.set_title("请先导入数据", color=C['text_dim'])
            self.draw()
            return
        df = self.df.copy()
        numeric = ["Flow", "VST", "Izod", "Modulus", "PCR", "GF", "FR_num"]
        for col in [self.x_key, self.y_key]:
            if col in numeric:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        x = df[self.x_key].dropna()
        y = df[self.y_key].dropna()
        idx = x.index.intersection(y.index)
        x, y = x.loc[idx], y.loc[idx]
        labels = df.loc[idx, "Grade"].astype(str)

        self.ax.clear()
        self.ax.set_facecolor(C['bg_panel'])

        # 颜色
        if self.color_col in df.columns:
            cats = df.loc[idx, self.color_col].fillna("Other").unique()
            color_map = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(cats)}
            colors = [color_map.get(v, C['text_dim']) for v in df.loc[idx, self.color_col].fillna("Other")]
        else:
            colors = C['accent']

        # 高亮点
        if highlight_indices:
            mask = np.array([i in set(highlight_indices) for i in idx])
            self.ax.scatter(x[~mask], y[~mask], c=colors, s=30, alpha=0.75, zorder=2)
            self.ax.scatter(x[mask], y[mask], c=C['green'], s=80, alpha=1, zorder=3,
                            edgecolors='white', linewidths=1)
        else:
            self.ax.scatter(x, y, c=colors, s=30, alpha=0.75, zorder=2)

        # 标注悬停
        if self.annotate_idx and self.annotate_idx in idx:
            i = idx.get_loc(self.annotate_idx)
            self.ax.annotate(labels.iloc[i], (x.iloc[i], y.iloc[i]),
                             color=C['accent'], fontsize=8,
                             bbox=dict(boxstyle='round,pad=0.3', facecolor=C['bg_card'],
                                       edgecolor=C['accent'], alpha=0.9),
                             zorder=10)

        self.ax.set_xlabel(self.x_key, fontsize=9)
        self.ax.set_ylabel(self.y_key, fontsize=9)
        self.ax.grid(True, alpha=0.3)
        self.ax.tick_params(labelsize=8)
        self.fig.tight_layout()
        self.draw()

    def _on_hover(self, event):
        if self.df is None or not len(event.xdata): return
        if event.xdata is None: return
        dists = ((self.df[self.x_key].astype(float) - float(event.xdata))**2 +
                 (self.df[self.y_key].astype(float) - float(event.ydata))**2)
        nearest = dists.idxmin() if not dists.isna().all() else None
        if nearest != self.annotate_idx:
            self.annotate_idx = nearest
            self.draw_chart()

    def _on_click(self, event):
        if self.df is None or not event.xdata: return
        dists = ((self.df[self.x_key].astype(float) - float(event.xdata))**2 +
                 (self.df[self.y_key].astype(float) - float(event.ydata))**2
                 ).dropna()
        nearest = dists.idxmin() if len(dists) else None
        if nearest is not None:
            from PyQt6.QtWidgets import QApplication
            win = QApplication.instance().property('_mainWindow')
            if win:
                win.highlight_material(nearest)

    def export_png(self, path):
        self.fig.savefig(path, dpi=300, bbox_inches='tight', facecolor=C['bg_panel'])
