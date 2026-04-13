"""Lightweight architecture drift checks for the cleanup migration."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND_SRC = ROOT / "backend" / "src"

ROUTE_IMPORT_PATTERN = re.compile(r"from\s+src\.[\w\.]+\.routes\.")
SYS_PATH_PATTERN = re.compile(r"sys\.path\.(insert|append)\(")
FASTAPI_IMPORT_PATTERN = re.compile(r"from\s+fastapi\s+import|import\s+fastapi")

ALLOWED_ROUTE_IMPORT_FILES = {
    ROOT / "backend" / "src" / "interfaces" / "rest_api" / "whatsapp" / "router.py",
    ROOT / "backend" / "src" / "interfaces" / "http" / "demo" / "router.py",
    ROOT / "backend" / "src" / "interfaces" / "http" / "compat" / "router.py",
    ROOT / "backend" / "src" / "interfaces" / "http" / "ai" / "router.py",
    ROOT / "backend" / "src" / "interfaces" / "http" / "identity" / "router.py",
    ROOT / "backend" / "src" / "interfaces" / "http" / "academic" / "router.py",
    ROOT / "backend" / "src" / "interfaces" / "http" / "administrative" / "router.py",
    ROOT / "backend" / "src" / "interfaces" / "http" / "mascot" / "router.py",
    ROOT / "backend" / "src" / "interfaces" / "http" / "platform" / "router.py",
    ROOT / "backend" / "src" / "interfaces" / "whatsapp" / "router.py",
}


def iter_python_files(base: Path):
    for path in base.rglob("*.py"):
        if "__pycache__" not in path.parts:
            yield path


def main() -> int:
    failures: list[str] = []

    for path in iter_python_files(BACKEND_SRC):
        content = path.read_text(encoding="utf-8")
        if SYS_PATH_PATTERN.search(content):
            failures.append(f"{path.relative_to(ROOT)}: app code must not mutate sys.path")

        if ROUTE_IMPORT_PATTERN.search(content) and path not in ALLOWED_ROUTE_IMPORT_FILES:
            failures.append(f"{path.relative_to(ROOT)}: route-to-route import detected")

        if "domains" in path.parts and "domain" in path.parts and FASTAPI_IMPORT_PATTERN.search(content):
            failures.append(f"{path.relative_to(ROOT)}: domain layer must not import FastAPI")

    if failures:
        print("Architecture drift detected:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Architecture guard checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
