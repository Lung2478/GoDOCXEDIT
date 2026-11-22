# GoDOCXEDIT MCP Server Setup Guide

`godocxedit_mcp.py` 是一款零第三方依賴（純 Python 3 標準庫）的 `stdio` MCP Server 包裝器，依 **MIT License**（`LICENSE-INTERFACES`）釋出，讓任何支援 Model Context Protocol (MCP) 的 AI 客戶端（Antigravity、Claude Desktop、Cursor 等）一鍵掛載 `GoDOCXEDIT.exe` 的四大安全文件工具：

- `godocxedit_info`：查詢版本、支援格式與 15 款安全字型白名單
- `godocxedit_audit`：唯讀掃描檔案或資料夾之雙平台相容性風險
- `godocxedit_convert`：單檔正規化轉檔（嚴禁覆寫原檔）
- `godocxedit_batch`：遞迴批次重製公司舊檔資料夾至獨立輸出目錄（自動跳過 `~$` 鎖定檔）

---

## 前置需求 (Prerequisites)

1. 前往 **[GitHub Releases](https://github.com/Lung2478/GoDOCXEDIT/releases/latest)** 下載 `GoDOCXEDIT.exe` 並放置於固定路徑（例如 `C:\Tools\GoDOCXEDIT\GoDOCXEDIT.exe`）。
2. 本機已安裝 Python 3.9+（不需 `pip install` 任何額外套件）。

---

## MCP 設定範例 (Client Configuration)

於您的 AI 客戶端 MCP 設定檔（如 `mcp_config.json` / `claude_desktop_config.json`）加入以下項目：

```json
{
  "mcpServers": {
    "godocxedit": {
      "command": "python",
      "args": [
        "C:/Tools/GoDOCXEDIT/interfaces/mcp/godocxedit_mcp.py"
      ],
      "env": {
        "GODOCXEDIT_EXE": "C:/Tools/GoDOCXEDIT/GoDOCXEDIT.exe"
      }
    }
  }
}
```

設定完成後，即可直接對 AI 下達自然語言指令，例如：
- 「請先用 `godocxedit_audit` 幫我掃描 `D:\CompanyDocs\Legacy` 裡面有哪些舊 Word 檔含有非交集字型。」
- 「請用 `godocxedit_batch` 把 `D:\CompanyDocs\Legacy` 批次重製到 `D:\CompanyDocs\WordDocsReady`，中文統一微軟正黑體、英文統一 Calibri，完成後給我摘要報告。」
