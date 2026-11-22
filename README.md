# GoDOCXEDIT

**Microsoft Word & Google Docs 100% 雙向完全相容之離線商務文件編輯器 ＋ AI 批次自動化引擎**  
*100% Mutually Compatible Offline Desktop Word Processor & Headless AI Automation Engine for Microsoft Word & Google Docs*

---

## 1. 產品定位與核心特色 (Overview & Key Features)

**GoDOCXEDIT** 隸屬於 **GoXEDIT** 離線桌面生產力家族，是一款開箱即用的 Windows 單一離線執行檔（`GoDOCXEDIT.exe`）。本軟體嚴格鎖定 **Microsoft Word** 與 **Google Docs** 兩大平台的 **100% 交集**，確保編修或轉換完成的 `.docx` 文件在桌面版 Word 與雲端 Google Docs 之間來回開啟時，字型、版面、表格、目錄、浮水印與向量流程圖皆不跑版、不跳字。

- **15 款雙平台交集安全字型 ＋ 中英雙語系自動切分**：完整支援 3 款繁體中文字型（微軟正黑體、新細明體、標楷體）與 12 款跨平台西文字型，底層自動寫入四重字型槽位綁定，徹底消除中英混排字型跳號。
- **完整多格式雙向互通**：預設儲存為 `.docx`；支援開啟／匯入與另存／匯出 `.docx`、`.odt`、`.rtf`、`.html`、`.md`、`.txt`，並支援 1:1 預覽列印與 `.pdf` 匯出。
- **專業商務文件引擎**：支援 7 種國際標準紙張（`A3`~`A5`、`B4`~`B5`、`Letter`、`Legal`）、同份文件多節直橫混排、雙軌目錄（保留原始頁碼或動態掃描）、複雜跨欄跨列合併與巢狀表格、文字／圖片浮水印、嵌入式向量繪圖畫布（14 款幾何圖形 ＋ 4 種磁吸連結線／箭頭）。
- **專為 AI 代理打造的 Headless CLI ＋ MCP Server ＋ Agent Skill**：同一支 `GoDOCXEDIT.exe` 內建無頭指令列介面，可由 AI 模型一行指令安全盤點（`audit`）並批次重製（`batch`）企業既有舊 Office 文件，內建絕不覆寫原檔安全防呆與結構化 JSON 報告。

---

## 2. 下載與完整性驗證 (Download & SHA-256 Verification)

請前往本倉庫之 **[GitHub Releases (Latest)](https://github.com/Lung2478/GoDOCXEDIT/releases/latest)** 下載最新發行包：

- `GoDOCXEDIT.exe`：Windows 100% 離線單一執行檔（免安裝、免網路、支援 GUI 編輯與 Headless CLI）
- `Quick_Start_Manual_zh-TW.docx`：正體中文詳盡快速入門活體手冊（亦提供線上版 [`docs/Quick_Start_Manual_zh-TW.md`](./docs/Quick_Start_Manual_zh-TW.md)）
- `Quick_Start_Manual_en.docx`：English Comprehensive Quick Start Manual (also online at [`docs/Quick_Start_Manual_en.md`](./docs/Quick_Start_Manual_en.md))
- `SHA256SUMS.txt`：發佈檔案之 SHA-256 雜湊校驗碼

下載完成後，企業 IT 或個人使用者可於 PowerShell 驗證執行檔完整性：

```powershell
Get-FileHash .\GoDOCXEDIT.exe -Algorithm SHA256
# 比對輸出值是否與 Releases 中的 SHA256SUMS.txt 完全一致
```

---

## 3. 讓 AI 自動操作 GoDOCXEDIT（批次重製企業舊檔）(AI Automation & Headless CLI)

GoDOCXEDIT 提供完整、零依賴且採 **MIT 授權** 的公開 AI 操作介面套件（位於 [`interfaces/`](./interfaces/)），支援主流 AI 代理（Antigravity、Claude、Codex、Cursor 等）安全操作 `GoDOCXEDIT.exe`：

```powershell
# 1. 唯讀盤點舊檔資料夾相容性風險（不改動任何檔案）
.\GoDOCXEDIT.exe audit .\legacy_office_docs --json --report .\audit_report.json

# 2. 一行指令批次重製為 100% Word & Google Docs 相容 .docx（輸出至獨立目錄，絕不覆寫原檔）
.\GoDOCXEDIT.exe batch .\legacy_office_docs --output .\compatible_docs --cjk-font "Microsoft JhengHei" --latin-font "Calibri" --json --report .\batch_report.json
```

**官方 AI 操作介面資源導覽**：
- **CLI 完整指令與 JSON Schema 規格**：[`docs/AI_CLI_REFERENCE.md`](./docs/AI_CLI_REFERENCE.md)
- **AI Agent 標準操作技能檔（Skill）**：[`interfaces/skills/godocxedit-operator/SKILL.md`](./interfaces/skills/godocxedit-operator/SKILL.md)
- **零依賴 Python MCP Server（stdio）**：[`interfaces/mcp/godocxedit_mcp.py`](./interfaces/mcp/godocxedit_mcp.py)（安裝教學見 [`interfaces/mcp/README.md`](./interfaces/mcp/README.md)）
- **PowerShell / Python 批次腳本範例**：[`interfaces/examples/`](./interfaces/examples/)

---

## 4. 授權條款與商業授權 (Licensing & Commercial Inquiries)

本倉庫採用 **雙層授權架構**：

1. **GoDOCXEDIT 軟體執行檔本體 (`GoDOCXEDIT.exe`)**：依專有免費軟體終端使用者授權協議（Proprietary Freeware EULA）發佈，詳見英文正式版 [`LICENSE`](./LICENSE) 與正體中文版 [`LICENSE.zh-TW.md`](./LICENSE.zh-TW.md)。
   - **個人與企業內部使用完全免費**（包含企業內部由 AI 代理批次重製自家舊 Office 檔案）。
   - 未經書面商業授權，禁止再散布轉售、白牌換名、對外提供商業 SaaS／轉檔代工服務或逆向反編譯。
2. **公開 AI 操作介面與呼叫範例 (`interfaces/` 目錄)**：另行依 **MIT License** 釋出（詳見 [`LICENSE-INTERFACES`](./LICENSE-INTERFACES)），方便開發者與企業 IT 自由整合至各類 AI 工作流；該 MIT 授權不及於軟體執行檔本體。
3. **第三方開源元件宣告**：詳見 [`THIRD_PARTY_NOTICES.txt`](./THIRD_PARTY_NOTICES.txt)。

> **商業授權宣告 (Commercial Licensing Notice)**  
> 本免費授權涵蓋標準版之個人與企業內部使用。若貴公司需要 OEM 內嵌整合、專屬客製開發、企業級大量舊檔重製顧問、或專屬技術支援與 SLA，請聯繫 GoXEDIT 官方取得商業授權。  
> *This free license covers personal and internal enterprise use of the Standard Edition. If your organization requires OEM embedded integration, dedicated custom development, enterprise-scale legacy document rebuilding consulting, or dedicated technical support and SLA, please contact GoXEDIT Official for a Commercial License.*

**官方商業授權聯繫管道**：
- GoXEDIT 官方網站聯絡表單
- 本倉庫 **[GitHub Issues（商用洽詢表單）](https://github.com/Lung2478/GoDOCXEDIT/issues/new?template=commercial_inquiry.md)**（標籤：`commercial-inquiry`）

---

## 5. 免責聲明與備份提醒 (Disclaimer & Backup Warning)

本軟體係「依現狀（AS IS）」免費提供，不附帶任何明示或默示擔保。在對重要個人或企業檔案執行任何正規化或 AI 自動化批次轉換作業前，**請務必先行保留所有原始檔案之獨立完整備份**；因 Microsoft Word 與 Google Docs 各自存在超出雙平台交集之專屬排版特性，轉換完成之文件於正式對外發佈或歸檔前應由人工抽檢確認。完整免責條款請參閱 [`LICENSE`](./LICENSE) 與 [`LICENSE.zh-TW.md`](./LICENSE.zh-TW.md)。

---

Copyright (c) 2026 GoXEDIT Project (Lung2478). All Rights Reserved.
