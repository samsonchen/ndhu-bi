# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas"]
# ///
"""把 data/ 的三個 CSV 整理成網頁可直接載入的 docs/data.js（window.BI_DATA）。

資料用「維度表 + 索引列」的格式存放，讓檔案小一點：
  semesters / colleges / depts / degrees / genders / reasons   各維度的值
  enrollment : [學期, 系所, 學位別, 性別, 在學人數]
  leave      : [學期, 系所, 學位別, 性別, 休學原因, 學期間休學, 學期底休學狀態]
除了人數以外的欄位，都是該維度表的索引（從 0 起算）。學院由系所決定（depts[i].college）。
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "docs" / "data.js"

read = lambda name: pd.read_csv(DATA / name, encoding="utf-8-sig")
enrollment, leave, mapping = read("enrollment.csv"), read("leave.csv"), read("dept_mapping.csv")

# 先加總：丟掉 dept_raw、program_raw、identity 等網頁用不到的欄位
enrollment = enrollment.groupby(["semester", "dept", "degree", "gender"], as_index=False)["count"].sum()
leave = leave.groupby(["semester", "dept", "degree", "gender", "reason"], as_index=False)[
    ["new_leave", "on_leave_end"]].sum()

# 維度表（學期與學位別用固定順序，其餘照資料排序）
semesters = sorted(set(enrollment.semester) | set(leave.semester))
degrees = ["學士", "碩士", "博士"]
genders = ["女", "男"]
reasons = sorted(leave.reason.unique())
mapping = mapping.sort_values(["college", "dept"]).reset_index(drop=True)
colleges = list(dict.fromkeys(mapping.college))
depts = [
    {
        "name": r.dept,
        "college": colleges.index(r.college),
        "aliases": r.aliases.split(";") if isinstance(r.aliases, str) and r.aliases else [],
    }
    for r in mapping.itertuples()
]

idx = lambda values: {v: i for i, v in enumerate(values)}
S, D, DEG, G, R = idx(semesters), idx(mapping.dept), idx(degrees), idx(genders), idx(reasons)

data = {
    "semesters": semesters,
    "colleges": colleges,
    "depts": depts,
    "degrees": degrees,
    "genders": genders,
    "reasons": reasons,
    "enrollment": [
        [S[r.semester], D[r.dept], DEG[r.degree], G[r.gender], int(r.count)]
        for r in enrollment.itertuples() if r.count
    ],
    "leave": [
        [S[r.semester], D[r.dept], DEG[r.degree], G[r.gender], R[r.reason], int(r.new_leave), int(r.on_leave_end)]
        for r in leave.itertuples() if r.new_leave or r.on_leave_end
    ],
}

OUT.parent.mkdir(exist_ok=True)
OUT.write_text("window.BI_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
               encoding="utf-8")

# 核對：從輸出的資料重新算一次，必須和原始 CSV 一致
rows = data["enrollment"]
total_114_1 = sum(r[4] for r in rows if semesters[r[0]] == "114-1")
src_114_1 = int(read("enrollment.csv").query("semester == '114-1'")["count"].sum())
assert total_114_1 == src_114_1 == 10035, (total_114_1, src_114_1)
assert sum(r[5] for r in data["leave"]) == int(read("leave.csv").new_leave.sum())
assert sum(r[6] for r in data["leave"]) == int(read("leave.csv").on_leave_end.sum())
print(f"114-1 在學人數合計 {total_114_1}（核對通過）")
print(f"在學 {len(rows)} 列、休學 {len(data['leave'])} 列、系所 {len(depts)} 個、學院 {len(colleges)} 個")
print(f"{OUT}  {OUT.stat().st_size:,} bytes")
