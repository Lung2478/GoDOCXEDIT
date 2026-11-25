# GoDOCXEDIT Headless CLI 與 AI 操作接口參考手冊
# GoDOCXEDIT Headless CLI & AI Automation Reference (`v1.9.1`)

本文件定義 `GoDOCXEDIT.exe` 的無頭指令列介面（Headless CLI），專為 AI 代理（Antigravity、Claude、Codex、Cursor 等）與企業 IT 自動化管線設計，可在完全不啟動桌面視窗的情況下，安全稽核、轉換並批次重製舊 Office 文件為 **Microsoft Word & Google Docs 雙向交集相容**檔案。

---

## 1. 基本呼叫模式與安全鐵律 (Invocation & Safety Guardrails)

同一支 `GoDOCXEDIT.exe` 支援雙模態：
- **GUI 模式**：雙擊執行檔或傳入單純檔案路徑（`GoDOCXEDIT.exe report.docx`）即開啟桌面編輯視窗。
- **Headless CLI 模式**：第一個參數為 `info`、`audit`、`convert`、`batch` 或 `--help` / `--version` 時，立即以純無頭模式執行並回傳標準退出碼，不啟動任何視窗。

**內建強制安全防呆**：
1. **嚴禁覆寫原檔（Non-Overwrite Guardrail）**：`convert` 拒絕輸出路徑與輸入檔案相同；`batch` 拒絕 `--output` 目錄等於或位於輸入目錄內部，違規一律回傳退出碼 `2`（`NON_OVERWRITE_VIOLATION`）。
2. **自動跳過鎖定與暫存檔**：自動略過 MS Office 鎖定檔（`~$*`）、隱藏檔（`.*`）與暫存檔（`*.tmp`）。
3. **原子寫入（Atomic Write）**：所有輸出文件與 `--report` JSON 報表皆先寫入 `.godocxedit.tmp` 再以 `os.replace()` 原子替換，避免中斷產生損毀檔案。
4. **Windows 主控台輸出建議**：因 `GoDOCXEDIT.exe` 採無黑框視窗封裝，由程式／AI 透過 `subprocess` 擷取 stdout 管線時可直接讀取 UTF-8 JSON；若於互動式 PowerShell 呼叫，建議一律加上 `--report <path.json>` 確保完整擷取結構化報表。

---

## 2. 退出碼契約 (Exit Code Contract)

| 退出碼 (Exit Code) | 語意說明 (Meaning) | 建議 AI 代理後續動作 |
| :---: | :--- | :--- |
| `0` | 全部作業成功完成 (`status: "ok"`) | 讀取 JSON 報告摘要並向使用者回報結果與正規化項目。 |
| `1` | 部分檔案失敗或 I/O 讀取錯誤 (`status: "partial_error"` / `"error"`) | 檢視 `items[]` 中 `status == "error"` 之個別檔案與錯誤訊息並向使用者回報。 |
| `2` | 參數錯誤、字型不在 15 款安全白名單、輸入路徑不存在或觸發防覆寫保護 (`NON_OVERWRITE_VIOLATION`) | 依 `message` 修正指令參數（例如指定獨立的 `--output` 路徑）後重試。 |

---

## 3. 四組核心子指令規格 (Subcommand Reference)

### 3.1 `info` — 查詢版本、支援格式與 15 款安全字型白名單

```powershell
GoDOCXEDIT.exe info --json [--report info.json]
```

**JSON 回傳範例**：
```json
{
  "status": "ok",
  "command": "info",
  "app": "GoDOCXEDIT",
  "version": "1.9.1",
  "compatibility": "Microsoft Word & Google Docs Mutual Intersection",
  "license": "Freeware EULA (Free for Personal & Internal Enterprise Use)",
  "supportedImportExtensions": [".docx", ".odt", ".rtf", ".html", ".htm", ".txt", ".md"],
  "supportedExportFormats": ["docx", "odt", "rtf", "html", "md", "txt"],
  "safeFonts": {
    "all": ["Calibri", "Arial", "Arial Black", "Verdana", "Tahoma", "Trebuchet MS", "Impact", "Times New Roman", "Georgia", "Cambria", "Garamond", "Courier New", "Microsoft JhengHei", "PMingLiU", "DFKai-SB"],
    "cjk": ["Microsoft JhengHei", "PMingLiU", "DFKai-SB"],
    "latin": ["Calibri", "Arial", "Arial Black", "Verdana", "Tahoma", "Trebuchet MS", "Impact", "Times New Roman", "Georgia", "Cambria", "Garamond", "Courier New"]
  },
  "safeDrawingShapes": ["rect", "roundRect", "ellipse", "diamond", "triangle", "parallelogram", "hexagon", "star5", "textBox", "wedgeRoundRectCallout", "rightArrow", "leftArrow", "upArrow", "downArrow"]
}
```

---

### 3.2 `audit` — 唯讀相容性掃描（絕不修改任何檔案）

```powershell
GoDOCXEDIT.exe audit <input_path> [--recursive | --no-recursive] [--extensions .docx,.odt,.rtf] [--json] [--report audit.json]
```

| 參數 | 必填 | 說明 |
| :--- | :---: | :--- |
| `input_path` | 是 | 單一檔案或欲掃描之資料夾路徑。 |
| `--recursive` / `--no-recursive` | 否 | 當 `input_path` 為資料夾時是否遞迴掃描子目錄（預設 `--recursive`）。 |
| `--extensions` | 否 | 逗號分隔副檔名過濾器（例如 `.docx,.odt,.rtf`），預設掃描全部 7 種支援格式。 |
| `--json` | 否 | 以標準 UTF-8 JSON 格式輸出至 stdout。 |
| `--report <path>` | 否 | 將完整 JSON 稽核報表原子寫入指定路徑。 |

**關鍵回傳欄位 (`summary`)**：
- `total`：納入掃描之檔案總數
- `succeeded`：成功解析數
- `needsNormalization`：含有非雙平台交集字型或單一平台特效、建議透過 `batch` 正規化重製之檔案數
- `cleanCompatible`：原本即完全相容之檔案數
- `skipped`：略過之鎖定檔／暫存檔數
- `failed`：無法讀取或損毀之檔案數

---

### 3.3 `convert` — 單一檔案正規化轉檔

```powershell
GoDOCXEDIT.exe convert <input_file> --output <output_file> [--format docx|odt|rtf|html|md|txt] [--cjk-font "Microsoft JhengHei"] [--latin-font "Calibri"] [--json] [--report convert.json]
```

| 參數 | 必填 | 說明 |
| :--- | :---: | :--- |
| `input_file` | 是 | 來源檔案路徑（支援 `.docx`/`.odt`/`.rtf`/`.html`/`.htm`/`.md`/`.txt`）。 |
| `-o`, `--output` | 是 | 目標輸出檔案路徑（**必須不同於 `input_file`**）。 |
| `--format` | 否 | 輸出格式（`docx` / `odt` / `rtf` / `html` / `md` / `txt`）；未指定時自動依 `--output` 副檔名判斷，預設 `docx`。 |
| `--cjk-font` | 否 | 選用；將所有中文字元區段統一為指定安全中文字型（須為 15 款 `SAFE_FONTS` 之一，建議 `Microsoft JhengHei`、`PMingLiU` 或 `DFKai-SB`）。 |
| `--latin-font` | 否 | 選用；將所有英文／數字區段統一為指定安全西文字型（例如 `Calibri`、`Arial`、`Times New Roman`）。 |
| `--json` / `--report` | 否 | 輸出結構化 JSON 至 stdout 或指定報表檔。 |

---

### 3.4 `batch` — 企業舊檔資料夾遞迴批次重製

```powershell
GoDOCXEDIT.exe batch <input_dir> --output <output_dir> [--format docx] [--recursive | --no-recursive] [--extensions .docx,.odt,.rtf] [--cjk-font "Microsoft JhengHei"] [--latin-font "Calibri"] [--json] [--report batch_report.json]
```

| 參數 | 必填 | 說明 |
| :--- | :---: | :--- |
| `input_dir` | 是 | 包含舊 Office 文件的來源資料夾。 |
| `-o`, `--output` | 是 | 獨立的目標輸出資料夾（**嚴禁等於或位於 `input_dir` 內部**），輸出時將自動鏡像保留原始子資料夾層級。 |
| `--format` | 否 | 統一目標格式（預設 `docx`）。 |
| `--recursive` / `--no-recursive` | 否 | 是否遞迴處理所有子資料夾（預設 `--recursive`）。 |
| `--extensions` | 否 | 副檔名過濾器（例如 `.docx,.odt,.rtf`）。 |
| `--cjk-font` / `--latin-font` | 否 | 企業統一標準雙語字型指定（自動進行中英字元切分並寫入四重 `<w:rFonts>` 綁定）。 |
| `--json` / `--report` | 否 | 輸出結構化 JSON 與完整逐檔正規化明細。 |

---

## 4. AI 代理執行企業批次重製標準作業流程 (Recommended AI Agent SOP)

1. **步驟 1 — 確認環境 (`info`)**：執行 `GoDOCXEDIT.exe info --json` 確認版本與 15 款安全字型清單。
2. **步驟 2 — 唯讀盤點 (`audit`)**：對企業舊檔目錄執行 `audit --json --report audit.json`，向使用者彙報總檔數、需要正規化的檔案比例、常見不相容字型或特效。
3. **步驟 3 — 提醒原檔備份並選定獨立輸出目錄**：確認輸出目錄完全獨立於來源目錄，絕不改動原檔。
4. **步驟 4 — 執行批次重製 (`batch`)**：依使用者確認的中英標準字型執行 `batch --output <new_dir> --json --report batch.json`。
5. **步驟 5 — 摘要交付報告**：解析 `batch.json` 之 `summary` 與 `items[]`，列出成功數、已正規化項目明細與任何異常檔案，並提醒使用者對關鍵合約或複雜 MS-Word 傳統手繪履歷表格進行人工抽檢。

---

## 5. 授權與免責聲明 (License & Disclaimer)

- 本介面規格文件與 `interfaces/` 下之範例腳本／Skill／MCP 包裝器依 **MIT License** 釋出（見 `LICENSE-INTERFACES`）。
- `GoDOCXEDIT.exe` 軟體執行檔本體依 **Freeware EULA** 授權（見 `LICENSE` / `LICENSE.zh-TW.md`）：個人與企業內部使用完全免費；如需 OEM 內嵌整合、專屬客製開發、企業級大量舊檔重製顧問或專屬技術支援與 SLA，請聯繫 GoXEDIT 官方取得商業授權。
- 執行任何批次重製前，請務必自行備份所有原始檔案。
