from __future__ import annotations

import re
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
AUDIT_REPORT = BACKEND_DIR.parent / "documentation" / "ocr_system_audit_report.md"

ROUTE_DECORATOR = re.compile(r"@router\.(post|put|patch)\(\"([^\"]+)\"\)")
PREFIX_PATTERN = re.compile(r'APIRouter\(prefix="([^"]+)"')


def _collect_upload_routes() -> set[str]:
    routes: set[str] = set()
    route_dirs = [
        BACKEND_DIR / "src" / "domains",
    ]
    for root in route_dirs:
        for path in root.rglob("routes/*.py"):
            text = path.read_text(encoding="utf-8")
            if "UploadFile" not in text:
                continue
            prefix_match = PREFIX_PATTERN.search(text)
            prefix = prefix_match.group(1) if prefix_match else ""
            lines = text.splitlines()
            for idx, line in enumerate(lines):
                match = ROUTE_DECORATOR.search(line)
                if not match:
                    continue
                route_path = match.group(2)
                block_lines: list[str] = []
                for candidate in lines[idx:]:
                    if block_lines and candidate.startswith("@router."):
                        break
                    if block_lines and (candidate.startswith("def ") or candidate.startswith("async def ")):
                        break
                    block_lines.append(candidate)
                while idx + len(block_lines) < len(lines):
                    next_line = lines[idx + len(block_lines)]
                    block_lines.append(next_line)
                    if next_line.rstrip().endswith("):"):
                        break
                block = "\n".join(block_lines)
                if "UploadFile" in block:
                    routes.add(f"{prefix}{route_path}")
    return routes


def _collect_audit_routes() -> dict[str, str]:
    if not AUDIT_REPORT.exists():
        return {}
    lines = AUDIT_REPORT.read_text(encoding="utf-8").splitlines()
    routes: dict[str, str] = {}
    for line in lines:
        if "| `/api/" in line:
            parts = [part.strip() for part in line.split("|") if part.strip()]
            if len(parts) >= 5:
                routes[parts[0].strip("`")] = parts[4]
            elif parts:
                routes[parts[0].strip("`")] = ""
    return routes


def test_upload_routes_are_audited():
    upload_routes = _collect_upload_routes()
    audited_routes = _collect_audit_routes()

    missing = sorted(route for route in upload_routes if route not in audited_routes)
    assert not missing, (
        "OCR audit report is missing UploadFile routes. "
        "Add these routes to documentation/ocr_system_audit_report.md: "
        + ", ".join(missing)
    )

    invalid_policy = sorted(
        route for route, policy in audited_routes.items()
        if route in upload_routes and policy not in {"`ocr_required`", "`ocr_optional`", "`ocr_not_applicable`"}
    )
    assert not invalid_policy, (
        "OCR audit report is missing OCR policy tags for routes: "
        + ", ".join(invalid_policy)
    )
