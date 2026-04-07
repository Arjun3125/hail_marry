#!/usr/bin/env python3
"""Run the local production-readiness gate and emit a markdown report.

This script only covers automatable local checks. It does not attempt live
external WhatsApp/device validation.
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
DEFAULT_OUTPUT = ROOT / "production_readiness_report.md"


@dataclass(frozen=True)
class GateCommand:
    name: str
    argv: list[str]
    workdir: Path


def _python() -> str:
    return sys.executable


def _playwright_binary() -> str:
    if os.name == "nt":
        return str(FRONTEND / "node_modules" / ".bin" / "playwright.cmd")
    return "npx"


def _powershell() -> str:
    return r"C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe"


def _npm_build_command() -> list[str]:
    if os.name == "nt":
        return ["npm.cmd", "run", "build"]
    return ["npm", "run", "build"]


def _format_command(argv: list[str]) -> str:
    return subprocess.list2cmdline(argv) if os.name == "nt" else " ".join(argv)


def build_gate_commands() -> list[GateCommand]:
    python = _python()
    playwright_bin = _playwright_binary()
    return [
        GateCommand(
            name="Backend mascot routes",
            argv=[python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "backend/tests/test_mascot_routes.py"],
            workdir=ROOT,
        ),
        GateCommand(
            name="Backend mascot WhatsApp adapter",
            argv=[python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "backend/tests/test_mascot_whatsapp_adapter.py"],
            workdir=ROOT,
        ),
        GateCommand(
            name="Backend alerting",
            argv=[python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "backend/tests/test_alerting.py"],
            workdir=ROOT,
        ),
        GateCommand(
            name="OCR benchmark gate",
            argv=[python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "backend/tests/evaluation/test_ocr_benchmark.py"],
            workdir=ROOT,
        ),
        GateCommand(
            name="Grounding suite",
            argv=[python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "backend/tests/evaluation/test_textbook_feature_grounding.py"],
            workdir=ROOT,
        ),
        GateCommand(
            name="Backend compile",
            argv=[
                python,
                "-m",
                "py_compile",
                "backend/src/domains/platform/routes/mascot.py",
                "backend/src/domains/platform/routes/whatsapp.py",
                "backend/src/domains/platform/services/mascot_orchestrator.py",
                "backend/src/domains/platform/services/alerting.py",
                "backend/config.py",
            ],
            workdir=ROOT,
        ),
        GateCommand(
            name="Frontend build",
            argv=_npm_build_command(),
            workdir=FRONTEND,
        ),
    ]


def run_command(cmd: GateCommand) -> dict:
    started = time.time()
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    env.setdefault("CI", "true")
    completed = subprocess.run(
        cmd.argv,
        cwd=str(cmd.workdir),
        shell=False,
        capture_output=True,
        text=True,
        env=env,
    )
    ended = time.time()
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    snippet_parts = []
    if stdout:
        snippet_parts.append(stdout)
    if stderr:
        snippet_parts.append(stderr)
    snippet = "\n".join(snippet_parts).strip()
    if len(snippet) > 4000:
        snippet = snippet[:4000].rstrip() + "\n...[truncated]"
    return {
        "name": cmd.name,
        "command": _format_command(cmd.argv),
        "workdir": str(cmd.workdir),
        "exit_code": completed.returncode,
        "duration_seconds": round(ended - started, 2),
        "status": "Pass" if completed.returncode == 0 else "Fail",
        "output": snippet or "(no output)",
    }


def render_report(results: list[dict], generated_at: str) -> str:
    overall_ok = all(item["exit_code"] == 0 for item in results)
    lines = [
        "# Production Readiness Report",
        "",
        f"Generated at: {generated_at}",
        f"Host OS: {platform.platform()}",
        "",
        "## Summary",
        "",
        f"- Local production gate: {'PASS' if overall_ok else 'FAIL'}",
        "- External live staging: not executed by this script",
        "",
        "## Gate Results",
        "",
        "| Check | Status | Duration (s) | Exit code |",
        "| --- | --- | ---: | ---: |",
    ]
    for item in results:
        lines.append(
            f"| {item['name']} | {item['status']} | {item['duration_seconds']} | {item['exit_code']} |"
        )
    lines.extend([
        "",
        "## Detailed Output",
        "",
    ])
    for item in results:
        lines.extend([
            f"### {item['name']}",
            "",
            f"- command: `{item['command']}`",
            f"- workdir: `{item['workdir']}`",
            f"- status: `{item['status']}`",
            f"- duration_seconds: `{item['duration_seconds']}`",
            "",
            "```text",
            item["output"],
            "```",
            "",
        ])
    lines.extend([
        "## External Work Still Required",
        "",
        "- live WhatsApp/device staging pass",
        "- evidence capture and sign-off",
        "- any staging-only fixes found during the live run",
        "",
        "Primary docs:",
        "",
        "- `documentation/mascot_whatsapp_staging_manual_test_script.md`",
        "- `documentation/mascot_whatsapp_staging_evidence_template.md`",
        "- `documentation/mascot_release_gate.md`",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local production-readiness gate.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Markdown report output path")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    args = parser.parse_args()

    commands = build_gate_commands()
    if args.dry_run:
        for cmd in commands:
            print(f"[{cmd.name}] {_format_command(cmd.argv)} (cwd={cmd.workdir})")
        return 0

    results = [run_command(cmd) for cmd in commands]
    generated_at = datetime.now(timezone.utc).isoformat()
    report = render_report(results, generated_at)
    output_path = Path(args.output)
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote report to {output_path}")
    return 0 if all(item["exit_code"] == 0 for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
