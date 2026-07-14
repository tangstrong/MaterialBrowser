# MaterialBrowser — Covestro 材料浏览器

科思创改性塑料材料数据分析工具，基于 PyQt6 原生桌面应用。

## 功能

- 📊 **散点图**：Flow / VST / Izod / Modulus / PCR / GF 任意XY轴组合
- 🔍 **多维筛选**：系列、特殊成分、MWB、特性标签 + 数值范围
- 📋 **数据表格**：排序、搜索、点击联动高亮
- 💾 **SQLite 持久化**：首次导入 Excel，后续秒开
- 📤 **导出 PNG**：散点图一键导出 300dpi 高清图

## 构建 Windows EXE

1. 上传此文件夹到 GitHub 仓库
2. 点击 **Actions → Build Windows EXE → Run workflow**
3. 等待 5-8 分钟，下载 `dist/MaterialBrowser` 文件夹
4. 双击 `MaterialBrowser.exe` 运行

## 本地运行（需要 Python）

```bash
pip install -r requirements.txt
python main.py
```

## Excel 格式

必填列：`Grade`（材料牌号）

可选数值列：`Flow`, `VST`, `Izod`, `Modulus`, `PCR`, `GF`, `FR`

分类列：`f1_cat`, `MWB`, `Customer`, `IMCare`, `SpecComp`, `PropHigh`
