# P2 做出 BI 網頁（35 分鐘）

分兩步：先把 CSV 轉成網頁讀得到的 `docs/data.js`，再請 AI 做網頁。

## P2-1 把資料送到網頁（約 3 分鐘）

```text
請用 Python + uv 寫 work/build_data.py，讀 data/enrollment.csv、data/leave.csv、data/dept_mapping.csv（這三個檔案有 BOM，請用 utf-8-sig 讀取），產出 docs/data.js，然後執行它。

docs/data.js 的格式固定如下（陣列裡每一列的欄位順序依 fields）：

window.NDHU_DATA = {
  semesters: ["111-1", "111-2", ...],          // 由舊到新
  depts: [{ dept, college, aliases: [...] }],  // 來自 dept_mapping.csv，aliases 拆成陣列
  enrollment: {
    fields: ["semester", "college", "dept", "degree", "gender", "count"],
    rows: [[...], ...]
  },
  leave: {
    fields: ["semester", "college", "dept", "degree", "gender", "reason", "reason_group", "new_leave", "on_leave_end"],
    rows: [[...], ...]
  }
};

- enrollment、leave 都先依 fields 裡除了人數以外的欄位加總
- 輸出成精簡 JSON（不換行、不縮排），UTF-8
- 用 uv 的 inline script metadata 宣告需要的套件
- 不要修改 data/ 裡的檔案
- 完成後告訴我 enrollment 和 leave 各有幾列、檔案多大
```

## P2-2 做網頁（約 30 分鐘）

```text
/frontend-design 請做一個 BI 網頁，存成 docs/index.html（單一檔案）。

技術：
- 用 <script src="data.js"></script> 讀 window.NDHU_DATA，不要用 fetch，直接雙擊 index.html 就要能開
- 圖表用 ECharts，從這個網址載入：https://cdnjs.cloudflare.com/ajax/libs/echarts/5.5.1/echarts.min.js
- ECharts 載入失敗時（例如沒有網路），頁面顯示一行提示
- 本機檔案只用相對路徑
- 介面全部用繁體中文，手機上卡片改成一欄

頁面最上方是全域篩選列，改任何一個條件，下面四張圖都要同步更新：
- 學院：多選，沒選視為全部
- 系所：多選，只列出已選學院底下的系所，沒選視為全部；選項文字顯示「系所名（舊名：A、B）」，沒有舊名就只顯示系所名
- 學位別：學士、碩士、博士，多選，至少保留一個
- 性別：全部、女、男
- 學期區間：可以拖拉兩端的 slider
- 顯示方式：合計 / 分開比較。合計是把篩選結果加總成一個數列；分開比較是每個已選系所各一個數列，沒選系所時改成每個已選學院各一個數列，學院也沒選時就是每個學院各一個數列
- 休學人數指標：學期間休學（預設）/ 學期底休學狀態

四張卡片：
1. 學生人數消長：折線圖，x 軸是學期，可切換成長條圖
2. 休學人數消長：折線圖，x 軸是學期，可切換成長條圖
3. 休學原因分佈：圓餅圖，取前 6 名，其餘合併成「其餘原因」（資料裡本來就有一個原因叫「其他」，不要混在一起）；圖下方用小字列出「其餘原因」包含哪些細類和各自人數；可切換成長條圖。這張圖不受「顯示方式」影響，永遠是合計
4. 各系休學比例：橫向長條圖，由高到低排序；可切換成散佈圖（x 是在學人數、y 是休學比例、泡泡大小是休學人數）
   - 永遠以系所為單位，不受「顯示方式」和「休學人數指標」影響
   - 休學比例 = 學期間休學人數 ÷ 在學人數，兩者都用所選學期區間加總
   - 卡片下方加一行註腳說明這個定義

動畫：
- 每張卡片右上角有圖型切換鈕，切換時用 ECharts 的 universalTransition 做變形動畫
- 篩選條件改變時，資料要平滑更新，不要整張圖清掉重畫

篩選結果沒有資料時，卡片顯示一行提示文字。

頁尾：
- 資料來源：國立東華大學在學人數統計表、休學人數統計表（111-1 至 114-1）
- 一個連結指向這個 repo 在 GitHub 上的頁面（從 git remote 取得網址），讓讀者可以下載原始資料

完成後告訴我怎麼在電腦上打開它檢查。
```

## 看結果

用瀏覽器打開 `docs/index.html`（需要網路，圖表元件從網路載入）。試試看：
- 只選一個學院，切換「合計 / 分開比較」
- 切換每張卡片的圖型，看轉場動畫
- 拖拉學期區間

看到不對的地方，直接用中文告訴 Claude 哪裡不對，例如「圓餅圖下面沒有列出其餘原因的細類」。

---

改一改（選做）：
- 把圓餅圖改成南丁格爾玫瑰圖
- 加一個深色模式切換
- 第 4 張卡片只顯示在學人數超過 100 人的系所，看看排名有沒有變
