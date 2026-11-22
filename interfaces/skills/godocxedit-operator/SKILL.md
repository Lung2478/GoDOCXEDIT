---
name: godocxedit-operator
description: Operate GoDOCXEDIT.exe via its official Headless CLI to safely audit, convert, and batch-rebuild legacy Office documents (.docx, .odt, .rtf, .html, .md, .txt) into 100% Microsoft Word and Google Docs mutually compatible files without modifying original source files.
---

# GoDOCXEDIT AI Operator Skill

Use this skill whenever the user asks you to audit, normalize, convert, or batch-rebuild personal or corporate Office documents for 100% Microsoft Word and Google Docs compatibility using **GoDOCXEDIT**.

## 1. Prerequisites & Binary Discovery
Locate `GoDOCXEDIT.exe` (downloaded from the official GoDOCXEDIT GitHub Releases):
- Check if the user provided an explicit path to `GoDOCXEDIT.exe`, or check the `GODOCXEDIT_EXE` environment variable, or the current working directory.
- Verify the binary before running batch work:
  ```powershell
  & $exe info --json
  ```
- Confirm `status == "ok"` and note the 15 `safeFonts` (`cjk`: `Microsoft JhengHei`, `PMingLiU`, `DFKai-SB`; `latin`: `Calibri`, `Arial`, `Times New Roman`, etc.).

## 2. Mandatory Safety Guardrails (NEVER VIOLATE)
1. **Never overwrite original source files**: Always pass a separate `--output` file path (for `convert`) or separate `--output` directory completely outside the source folder (for `batch`). GoDOCXEDIT CLI enforces this guardrail and returns exit code `2` (`NON_OVERWRITE_VIOLATION`) if violated.
2. **Always audit before large batch runs**: For folders with multiple documents, run `audit` first so the user knows which files contain non-intersection fonts or proprietary Microsoft Word effects.
3. **Always capture structured reports**: Pass `--json --report <report_path.json>` on every `audit`, `convert`, and `batch` call so you have complete, deterministic UTF-8 JSON results even in Windows `--windowed` environments.
4. **Remind users to back up and spot-check**: Remind users to keep backups of original files and manually spot-check high-stakes contracts or complex legacy MS-Word hand-drawn tables (such as irregular multi-grid resume forms) after batch rebuilding.

## 3. Standard 4-Step Workflow

### Step 1: Read-Only Compatibility Audit
```powershell
& $exe audit "<source_folder>" --json --report "<report_dir>\audit_report.json"
```
Read `<report_dir>\audit_report.json` and summarize:
- `summary.total`, `summary.needsNormalization`, `summary.cleanCompatible`, `summary.skipped`, `summary.failed`
- Top recurring `notices[].code` values (e.g. `FONT_NORMALIZED`, `PROPRIETARY_EFFECT_REMOVED`, `SHAPE_NORMALIZED`).

### Step 2: Confirm Corporate Font Standard (Optional)
Ask the user whether they want to preserve existing safe fonts or enforce a corporate dual-script font standard from the 15 `SAFE_FONTS`, such as:
- Traditional Chinese business standard: `--cjk-font "Microsoft JhengHei" --latin-font "Calibri"`
- Formal document standard: `--cjk-font "DFKai-SB" --latin-font "Times New Roman"`

### Step 3: Execute Safe Batch Rebuild (or Single Convert)
Batch directory rebuild:
```powershell
& $exe batch "<source_folder>" --output "<separate_output_folder>" --format docx --cjk-font "Microsoft JhengHei" --latin-font "Calibri" --json --report "<report_dir>\batch_report.json"
```
Single file conversion:
```powershell
& $exe convert "<input_file>" --output "<separate_output_file>" --json --report "<report_dir>\convert_report.json"
```

### Step 4: Verify Exit Code & Deliver Executive Summary
- Exit code `0`: All files succeeded. Present counts (`total`, `succeeded`, `normalized`, `skipped`) and key normalization notices.
- Exit code `1`: Partial error. List every item where `item.status == "error"` along with `item.error`.
- Exit code `2`: Invalid arguments, unsupported font name, or non-overwrite guardrail triggered. Correct parameters and retry.

## 4. Licensing Boundary Reminder
- This Skill file is provided under the **MIT License** (`LICENSE-INTERFACES`).
- `GoDOCXEDIT.exe` itself is governed by the **GoDOCXEDIT Proprietary Freeware EULA** (`LICENSE` / `LICENSE.zh-TW.md`): free for personal and internal enterprise use. Do not embed `GoDOCXEDIT.exe` into external commercial SaaS or third-party redistributed software without a Commercial License from GoXEDIT Official.
