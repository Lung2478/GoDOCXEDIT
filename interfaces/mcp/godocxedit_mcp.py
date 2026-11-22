#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GoDOCXEDIT Zero-Dependency MCP Server (stdio JSON-RPC 2.0)
License: MIT License (see LICENSE-INTERFACES) -- applies ONLY to this MCP
wrapper script, NOT to GoDOCXEDIT.exe (governed by LICENSE / EULA).

Exposes 4 safe Headless CLI tools to any MCP-compatible AI client
(Antigravity, Claude Desktop, Cursor, etc.):
  - godocxedit_info    : Query version, formats, and 15 SAFE_FONTS whitelist
  - godocxedit_audit   : Read-only compatibility audit of a file or directory
  - godocxedit_convert : Single-file normalization to a distinct output path
  - godocxedit_batch   : Batch-rebuild a directory to a separate output folder

Configuration:
  Set environment variable `GODOCXEDIT_EXE` to the absolute path of
  `GoDOCXEDIT.exe` (or pass `--exe <path>` as a CLI argument).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional

SERVER_NAME = "godocxedit-mcp"
SERVER_VERSION = "1.9.0"
PROTOCOL_VERSION = "2024-11-05"


def _resolve_exe_path(cli_exe: Optional[str]) -> str:
    candidates = [
        cli_exe,
        os.environ.get("GODOCXEDIT_EXE"),
        os.path.join(os.getcwd(), "GoDOCXEDIT.exe"),
    ]
    for cand in candidates:
        if cand and os.path.isfile(cand):
            return os.path.abspath(cand)
    return cli_exe or os.environ.get("GODOCXEDIT_EXE") or "GoDOCXEDIT.exe"


def _run_godocxedit(exe_path: str, sub_args: List[str]) -> Dict[str, Any]:
    if not os.path.isfile(exe_path):
        return {
            "status": "error",
            "message": (
                f"GoDOCXEDIT.exe not found at '{exe_path}'. "
                "Please download GoDOCXEDIT.exe from GitHub Releases and set GODOCXEDIT_EXE."
            ),
        }

    with tempfile.NamedTemporaryFile(prefix="godocxedit_mcp_", suffix=".json", delete=False) as tf:
        report_path = tf.name

    try:
        cmd = [exe_path, *sub_args, "--json", "--report", report_path]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            timeout=600,
        )
        if os.path.isfile(report_path) and os.path.getsize(report_path) > 0:
            with open(report_path, "r", encoding="utf-8") as rf:
                data = json.load(rf)
            data["exitCode"] = proc.returncode
            return data

        raw_out = (proc.stdout or "").strip()
        if raw_out.startswith("{"):
            try:
                data = json.loads(raw_out)
                data["exitCode"] = proc.returncode
                return data
            except Exception:
                pass

        return {
            "status": "error" if proc.returncode != 0 else "ok",
            "exitCode": proc.returncode,
            "stdout": raw_out,
            "stderr": (proc.stderr or "").strip(),
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "GoDOCXEDIT CLI execution timed out (600s)."}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
    finally:
        try:
            if os.path.exists(report_path):
                os.remove(report_path)
        except OSError:
            pass


TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "name": "godocxedit_info",
        "description": (
            "Query GoDOCXEDIT version, supported import/export document formats, "
            "and the 15 Microsoft Word & Google Docs mutually compatible SAFE_FONTS."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "godocxedit_audit",
        "description": (
            "Perform a read-only compatibility audit on a single document or directory. "
            "Detects non-intersection fonts and proprietary Microsoft Word effects without modifying files."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {
                    "type": "string",
                    "description": "Absolute path to a source document or folder to inspect.",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Recursively scan subdirectories (default: true).",
                    "default": True,
                },
                "extensions": {
                    "type": "string",
                    "description": "Optional comma-separated extension filter, e.g. '.docx,.odt,.rtf'.",
                },
            },
            "required": ["input_path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "godocxedit_convert",
        "description": (
            "Convert and normalize a single document into a 100% Microsoft Word & Google Docs "
            "compatible output file. Refuses to overwrite the original input file."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_file": {"type": "string", "description": "Source document file path."},
                "output": {
                    "type": "string",
                    "description": "Distinct destination file path (must differ from input_file).",
                },
                "format": {
                    "type": "string",
                    "enum": ["docx", "odt", "rtf", "html", "md", "txt"],
                    "description": "Optional target format (defaults to output extension or docx).",
                },
                "cjk_font": {
                    "type": "string",
                    "description": "Optional SAFE_FONTS CJK override (Microsoft JhengHei, PMingLiU, DFKai-SB).",
                },
                "latin_font": {
                    "type": "string",
                    "description": "Optional SAFE_FONTS Latin override (e.g. Calibri, Arial, Times New Roman).",
                },
            },
            "required": ["input_file", "output"],
            "additionalProperties": False,
        },
    },
    {
        "name": "godocxedit_batch",
        "description": (
            "Recursively batch-rebuild legacy Office documents in a folder into a separate "
            "output directory for 100% Microsoft Word & Google Docs compatibility. "
            "Strictly refuses outputting inside the source directory and skips ~$ lock files."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_dir": {"type": "string", "description": "Source folder containing legacy documents."},
                "output": {
                    "type": "string",
                    "description": "Separate destination folder outside input_dir.",
                },
                "format": {
                    "type": "string",
                    "enum": ["docx", "odt", "rtf", "html", "md", "txt"],
                    "default": "docx",
                },
                "recursive": {"type": "boolean", "default": True},
                "extensions": {
                    "type": "string",
                    "description": "Optional comma-separated extension filter, e.g. '.docx,.odt,.rtf'.",
                },
                "cjk_font": {"type": "string", "description": "Optional SAFE_FONTS CJK override."},
                "latin_font": {"type": "string", "description": "Optional SAFE_FONTS Latin override."},
            },
            "required": ["input_dir", "output"],
            "additionalProperties": False,
        },
    },
]


def _dispatch_tool(exe_path: str, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "godocxedit_info":
        return _run_godocxedit(exe_path, ["info"])

    if name == "godocxedit_audit":
        cmd = ["audit", str(arguments["input_path"])]
        if arguments.get("recursive") is False:
            cmd.append("--no-recursive")
        if arguments.get("extensions"):
            cmd.extend(["--extensions", str(arguments["extensions"])])
        return _run_godocxedit(exe_path, cmd)

    if name == "godocxedit_convert":
        cmd = ["convert", str(arguments["input_file"]), "--output", str(arguments["output"])]
        if arguments.get("format"):
            cmd.extend(["--format", str(arguments["format"])])
        if arguments.get("cjk_font"):
            cmd.extend(["--cjk-font", str(arguments["cjk_font"])])
        if arguments.get("latin_font"):
            cmd.extend(["--latin-font", str(arguments["latin_font"])])
        return _run_godocxedit(exe_path, cmd)

    if name == "godocxedit_batch":
        cmd = ["batch", str(arguments["input_dir"]), "--output", str(arguments["output"])]
        if arguments.get("format"):
            cmd.extend(["--format", str(arguments["format"])])
        if arguments.get("recursive") is False:
            cmd.append("--no-recursive")
        if arguments.get("extensions"):
            cmd.extend(["--extensions", str(arguments["extensions"])])
        if arguments.get("cjk_font"):
            cmd.extend(["--cjk-font", str(arguments["cjk_font"])])
        if arguments.get("latin_font"):
            cmd.extend(["--latin-font", str(arguments["latin_font"])])
        return _run_godocxedit(exe_path, cmd)

    return {"status": "error", "message": f"Unknown tool: {name}"}


def _write_rpc(message: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def serve_stdio(exe_path: str) -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params") or {}

        # Notifications without id require no response
        if req_id is None and method.startswith("notifications/"):
            continue

        if method == "initialize":
            _write_rpc(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    },
                }
            )
        elif method == "ping":
            _write_rpc({"jsonrpc": "2.0", "id": req_id, "result": {}})
        elif method == "tools/list":
            _write_rpc({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_SCHEMA}})
        elif method == "tools/call":
            tool_name = str(params.get("name", ""))
            tool_args = params.get("arguments") or {}
            res = _dispatch_tool(exe_path, tool_name, tool_args)
            is_err = res.get("status") == "error" or res.get("exitCode", 0) not in (0, None)
            _write_rpc(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(res, ensure_ascii=False, indent=2),
                            }
                        ],
                        "isError": bool(is_err),
                    },
                }
            )
        else:
            _write_rpc(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="GoDOCXEDIT Zero-Dependency MCP Server (stdio)")
    parser.add_argument("--exe", help="Path to GoDOCXEDIT.exe (overrides GODOCXEDIT_EXE env var)")
    args = parser.parse_args()
    serve_stdio(_resolve_exe_path(args.exe))


if __name__ == "__main__":
    main()
