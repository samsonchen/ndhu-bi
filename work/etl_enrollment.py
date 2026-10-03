# /// script
# requires-python = ">=3.10"
# dependencies = ["xlrd", "pandas"]
# ///
"""把 114-1 在學人數統計表 (.xls) 轉成 系所 × 學制 × 性別 的整齊 CSV。"""
import re
from pathlib import Path

import pandas as pd
import xlrd

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / "東華大學統計資料" / "在學人數統計表").glob("114-1*.xls"))
OUT = ROOT / "work" / "enrollment_114-1.csv"

# 區段標題 -> program_raw
SECTIONS = {"博士班": "博士班", "碩士班": "碩士班", "碩專班": "碩士在職專班", "學士班": "學士班"}
# 欄位位置（0 起算）：A 學制別, B 學院, C 系所, D 分組, F 總計女, G 總計男
COL_PROGRAM, COL_COLLEGE, COL_DEPT, COL_FEMALE, COL_MALE = 0, 1, 2, 5, 6


def text(v):
    return str(v).strip() if v != "" else ""


def num(v):
    return int(v) if v != "" else 0


def main():
    sheet = xlrd.open_workbook(SRC, formatting_info=True).sheet_by_index(0)  # 只讀第一個工作表
    # 系所欄中，被合併範圍「往下涵蓋」的列（不含範圍第一列）才是合法的空白
    covered = {r for lo, hi, clo, _ in sheet.merged_cells if clo == COL_DEPT for r in range(lo + 1, hi)}
    program, college, dept = None, None, None
    rows = []
    for r in range(4, sheet.nrows):  # 前 4 列是標題與「總計」
        a = text(sheet.cell_value(r, COL_PROGRAM))
        if a.startswith("備註"):
            break
        if a:
            head = a.split()[0]
            if head in SECTIONS:
                program = SECTIONS[head]
                if "合計" in a:  # 「博士班 合計1」等合計列
                    college = dept = None
                    continue
        # 合併儲存格：只有範圍第一格有值，其餘往下沿用
        c = text(sheet.cell_value(r, COL_COLLEGE))
        d = text(sheet.cell_value(r, COL_DEPT))
        college = c or college
        if not d and r not in covered:
            # 空白但不在任何合併範圍內（報表手誤，例如 R21 的應用物理博士班）：
            # 這是下一個系所的第一列，系所名稱取自往下第一個有值的儲存格
            d = next(text(sheet.cell_value(k, COL_DEPT)) for k in range(r + 1, sheet.nrows)
                     if text(sheet.cell_value(k, COL_DEPT)))
        dept = d or dept
        if not (college and dept):
            continue
        clean_college = re.sub(r"\s*[（(].*?[)）]", "", college).strip()
        for gender, col in (("女", COL_FEMALE), ("男", COL_MALE)):
            rows.append((clean_college, dept, program, gender, num(sheet.cell_value(r, col))))

    df = pd.DataFrame(rows, columns=["college", "dept_raw", "program_raw", "gender", "count"])
    # 同系所、同學制下的多個分組加總；sort=False 保持報表順序
    df = df.groupby(["college", "dept_raw", "program_raw", "gender"], sort=False, as_index=False)["count"].sum()
    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"{len(df)} 列，總人數 {df['count'].sum()} -> {OUT}")


if __name__ == "__main__":
    main()
