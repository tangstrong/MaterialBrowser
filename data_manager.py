# -*- coding: utf-8 -*-
"""数据管理：Excel读取 + SQLite + 异步Worker"""
import os, sqlite3, logging, numpy as np, pandas as pd
from datetime import datetime
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)

REQUIRED_COLS = ["Grade"]
NUMERIC_COLS  = ["Flow", "VST", "Izod", "Modulus", "PCR", "GF"]
TEXT_COLS     = ["Grade", "MWB", "Customer", "SMD", "IMCare", "SpecComp", "PropHigh", "f1_cat", "PH3"]
DB_PATH       = os.path.join(os.path.expanduser("~"), ".material_browser", "materials.db")

AXES_DEF = [
    {"key": "Flow",    "label": "Flow (MFR)",               "unit": "g/10min"},
    {"key": "FR",      "label": "Flame Rating (FR)",        "unit": ""},
    {"key": "VST",     "label": "VST B120 (Heat Resist.)", "unit": "°C"},
    {"key": "Izod",    "label": "Impact Strength (Notched)", "unit": "kJ/m²"},
    {"key": "Modulus", "label": "Modulus",                   "unit": "MPa"},
    {"key": "PCR",     "label": "PCR Content",              "unit": "%"},
    {"key": "GF",      "label": "GF Content",                "unit": "%"},
]

FILTER_DEFS = {
    "f1": {
        "label":  "🏷️  Series",
        "values": ["Makrolon", "Bayblend", "Apec XT"],
    },
    "f2": {
        "label":  "⚗️  Special Component",
        "values": ["FGF", "GF", "Mineral", "PC/ASA", "PCR", "SicoPC", "UV"],
    },
    "f3": {
        "label":  "🎯  MWB",
        "values": ["Baseload", "CIOT", "For all", "NB", "Network", "New energy", "Power", "Sem-conductity"],
    },
    "f5": {
        "label":  "✨  Property Highlight",
        "values": ["Chemical resistance", "GWFI", "High GWIT", "Mold release improve",
                   "NIA-PFAS", "Thermal conductive", "Translucent", "Transparent",
                   "f1", "f2", "hydrolysis resistance", "low reflection"],
    },
}

COLOR_MAP = {
    "Makrolon": "#4fc3f7",
    "Bayblend": "#ff8a65",
    "Apec XT":  "#ce93d8",
}


def parse_fr(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return np.nan, False
    s = str(v).strip()
    if s.lower() == "non-fr":
        return 4.0, True
    try:
        return float(s), False
    except ValueError:
        return np.nan, False


def infer_f1_cat(grade: str) -> str:
    g = str(grade).strip().upper()
    if g.startswith("M."):  return "Makrolon"
    if g.startswith("B."):  return "Bayblend"
    if g.startswith("A."):  return "Apec XT"
    return "Makrolon"


def normalize_speccomp(v) -> list:
    if not v or (isinstance(v, float) and np.isnan(v)):
        return []
    return [s.strip() for s in str(v).replace(" ", "").split("/") if s.strip()]


def fmt_val(v):
    if v is None: return "—"
    if isinstance(v, float):
        if np.isnan(v): return "—"
        return str(int(v)) if v == int(v) else f"{v:.2f}"
    return str(v)


def load_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    if "FR" in df.columns:
        parsed = df["FR"].apply(parse_fr)
        df["FR_num"]   = [p[0] for p in parsed]
        df["FR_nonfr"] = [p[1] for p in parsed]
    else:
        df["FR_num"]   = np.nan
        df["FR_nonfr"] = False
    sc_col = "SpecComp" if "SpecComp" in df.columns else None
    if sc_col:
        df["SpecComp_list"] = df[sc_col].apply(normalize_speccomp)
    else:
        df["SpecComp_list"] = [[] for _ in range(len(df))]
    if "f1_cat" not in df.columns:
        df["f1_cat"] = df["Grade"].apply(infer_f1_cat)
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in TEXT_COLS:
        if col in df.columns:
            df[col] = df[col].where(df[col].notna(), None)
    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def validate_dataframe(df: pd.DataFrame) -> tuple[bool, list]:
    errors = []
    for col in REQUIRED_COLS:
        if col not in df.columns:
            errors.append(f"缺少必填列: {col}")
    if df.empty:
        errors.append("Excel 文件没有数据行")
    if "Grade" in df.columns:
        dupes = df["Grade"].duplicated().sum()
        if dupes:
            errors.append(f"发现 {dupes} 条重复 Grade，将保留最后一条")
    return len(errors) == 0, errors


def ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            Grade TEXT PRIMARY KEY, f1_cat TEXT, PH3 TEXT, MWB TEXT,
            Customer TEXT, SMD TEXT, IMCare TEXT, SpecComp TEXT, PropHigh TEXT,
            Flow REAL, FR_raw TEXT, FR_num REAL, FR_nonfr INTEGER,
            VST REAL, Izod REAL, Modulus REAL, PCR REAL, GF REAL, updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def upsert_dataframe(df: pd.DataFrame):
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().isoformat()
    rows = []
    for _, r in df.iterrows():
        rows.append((
            str(r.get("Grade", "")),
            str(r.get("f1_cat", "") or ""),
            str(r.get("PH3", "") or ""),
            str(r.get("MWB", "") or ""),
            str(r.get("Customer", "") or ""),
            str(r.get("SMD", "") or ""),
            str(r.get("IMCare", "") or ""),
            str(r.get("SpecComp", "") or ""),
            str(r.get("PropHigh", "") or ""),
            float(r["Flow"])    if pd.notna(r.get("Flow"))    else None,
            str(r.get("FR", "") or ""),
            float(r["FR_num"])  if pd.notna(r.get("FR_num"))  else None,
            int(bool(r.get("FR_nonfr", False))),
            float(r["VST"])     if pd.notna(r.get("VST"))     else None,
            float(r["Izod"])    if pd.notna(r.get("Izod"))    else None,
            float(r["Modulus"]) if pd.notna(r.get("Modulus")) else None,
            float(r["PCR"])     if pd.notna(r.get("PCR"))     else None,
            float(r["GF"])      if pd.notna(r.get("GF"))      else None,
            now,
        ))
    conn.executemany("""
        INSERT INTO materials VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(Grade) DO UPDATE SET
            f1_cat=excluded.f1_cat, PH3=excluded.PH3, MWB=excluded.MWB,
            Customer=excluded.Customer, SMD=excluded.SMD, IMCare=excluded.IMCare,
            SpecComp=excluded.SpecComp, PropHigh=excluded.PropHigh,
            Flow=excluded.Flow, FR_raw=excluded.FR_raw, FR_num=excluded.FR_num,
            FR_nonfr=excluded.FR_nonfr, VST=excluded.VST, Izod=excluded.Izod,
            Modulus=excluded.Modulus, PCR=excluded.PCR, GF=excluded.GF,
            updated_at=excluded.updated_at
    """, rows)
    conn.commit()
    conn.close()
    logger.info(f"Upserted {len(rows)} rows to SQLite")


def load_from_db() -> pd.DataFrame:
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM materials ORDER BY Grade", conn)
    conn.close()
    return df


# ── PyQt6 Worker ────────────────────────────────────────────────────────────────
class DataWorker(QObject):
    finished  = pyqtSignal()
    error     = pyqtSignal(str)
    progress  = pyqtSignal(str)
    dataReady = pyqtSignal(pd.DataFrame)

    def __init__(self, excel_path=None, parent=None):
        super().__init__(parent)
        self.excel_path = excel_path

    def run(self):
        try:
            if self.excel_path and os.path.isfile(self.excel_path):
                self.progress.emit(f"读取 Excel: {os.path.basename(self.excel_path)}")
                df = load_excel(self.excel_path)
                valid, errs = validate_dataframe(df)
                if not valid:
                    self.error.emit("\n".join(errs))
                    return
                self.progress.emit("写入 SQLite…")
                upsert_dataframe(df)
                self.progress.emit("加载完成")
                self.dataReady.emit(df)
            else:
                self.progress.emit("从 SQLite 加载…")
                df = load_from_db()
                if df.empty:
                    self.error.emit("SQLite 无数据，请先导入 Excel 文件")
                    return
                self.dataReady.emit(df)
        except Exception as e:
            logger.exception("DataWorker error")
            self.error.emit(str(e))
        finally:
            self.finished.emit()
