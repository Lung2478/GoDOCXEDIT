#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GoDOCXEDIT Sample Batch Rebuild Script (Python 3)
License: MIT License (see LICENSE-INTERFACES). Applies ONLY to this script,
NOT to GoDOCXEDIT.exe (governed by LICENSE / EULA).

Example:
    python batch_rebuild_office_docs.py \
        --exe "C:/Tools/GoDOCXEDIT/GoDOCXEDIT.exe" \
        --input "D:/LegacyOfficeDocs" \
        --output "D:/WordAndGoogleDocsReady" \
        --cjk-font "Microsoft JhengHei" \
        --latin-font "Calibri"
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


def run_cli(exe_path: str, cli_args: list[str], report_path: str) -> tuple[int, dict]:
    cmd = [exe_path, *cli_args, "--json", "--report", report_path]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdin=subprocess.DEVNULL,
    )
    if os.path.isfile(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            return proc.returncode, json.load(f)
    return proc.returncode, {
        "status": "error",
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe 2-step batch rebuild wrapper for GoDOCXEDIT.exe")
    parser.add_argument("--exe", required=True, help="Path to GoDOCXEDIT.exe")
    parser.add_argument("--input", required=True, help="Source directory containing legacy Office files")
    parser.add_argument("--output", required=True, help="Separate output directory outside --input")
    parser.add_argument("--format", default="docx", choices=["docx", "odt", "rtf", "html", "md", "txt"])
    parser.add_argument("--cjk-font", default="Microsoft JhengHei")
    parser.add_argument("--latin-font", default="Calibri")
    args = parser.parse_args()

    report_dir = os.path.join(os.path.abspath(args.output), "_godocxedit_reports")
    os.makedirs(report_dir, exist_ok=True)
    audit_report = os.path.join(report_dir, "audit_report.json")
    batch_report = os.path.join(report_dir, "batch_report.json")

    print("=== Step 1: Read-Only Compatibility Audit ===")
    rc_audit, audit_data = run_cli(args.exe, ["audit", args.input], audit_report)
    print(json.dumps(audit_data.get("summary", audit_data), ensure_ascii=False, indent=2))
    if rc_audit == 2:
        return 2

    print("\n=== Step 2: Safe Batch Rebuild ===")
    rc_batch, batch_data = run_cli(
        args.exe,
        [
            "batch",
            args.input,
            "--output",
            args.output,
            "--format",
            args.format,
            "--cjk-font",
            args.cjk_font,
            "--latin-font",
            args.latin_font,
        ],
        batch_report,
    )
    print(json.dumps(batch_data.get("summary", batch_data), ensure_ascii=False, indent=2))
    print(f"\nFull JSON report written to: {batch_report}")
    return rc_batch


if __name__ == "__main__":
    sys.exit(main())
