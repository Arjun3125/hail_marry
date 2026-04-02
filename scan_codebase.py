import os
import ast
import re


def scan_python_file(filepath):
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                results.append(f"- **Class**: `{node.name}`")
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        results.append(f"  - **Method**: `{method.name}`")
            elif isinstance(node, ast.FunctionDef) and getattr(node, "col_offset", 0) == 0:
                results.append(f"- **Function**: `{node.name}`")
    except Exception as e:
        results.append(f"- *Error parsing {filepath}: {e}*")
    return results


def scan_ts_file(filepath):
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        classes = re.findall(r"(?:export\s+)?class\s+(\w+)", content)
        for c in classes:
            results.append(f"- **Class**: `{c}`")

        funcs = re.findall(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)", content)
        for func_name in funcs:
            results.append(f"- **Function**: `{func_name}`")

        arrows = re.findall(
            r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>",
            content,
        )
        for arrow_name in arrows:
            results.append(f"- **Arrow Function / Component**: `{arrow_name}`")

    except Exception:
        pass
    return results


def main():
    base_dir = r"c:\Users\naren\Work\Projects\proxy_notebooklm"
    output_file = os.path.join(base_dir, "VidyaOS_Features_List.md")

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# VidyaOS Detailed Codebase Features & Functions\n\n")
        out.write("This document provides an exhaustive scan of all classes, methods, components, and functions organized by module.\n\n")

        out.write("## 1. Backend (FastAPI / Python)\n\n")
        backend_dir = os.path.join(base_dir, "backend")
        for root, dirs, files in os.walk(backend_dir):
            if ".venv" in root or "__pycache__" in root or "node_modules" in root:
                continue
            py_files = [f for f in files if f.endswith(".py")]
            if py_files:
                rel_dir = os.path.relpath(root, base_dir)
                out.write(f"### `{rel_dir}`\n")
                for py_file in py_files:
                    filepath = os.path.join(root, py_file)
                    funcs = scan_python_file(filepath)
                    if funcs:
                        out.write(f"#### File: `{py_file}`\n")
                        for func in funcs:
                            out.write(f"{func}\n")
                        out.write("\n")

        out.write("---\n\n## 2. Frontend (Next.js / TypeScript)\n\n")
        frontend_dir = os.path.join(base_dir, "frontend", "src")
        for root, dirs, files in os.walk(frontend_dir):
            if "node_modules" in root or ".next" in root:
                continue
            ts_files = [f for f in files if f.endswith((".ts", ".tsx"))]
            if ts_files:
                rel_dir = os.path.relpath(root, base_dir)
                out.write(f"### `{rel_dir}`\n")
                for ts_file in ts_files:
                    filepath = os.path.join(root, ts_file)
                    funcs = scan_ts_file(filepath)
                    if funcs:
                        out.write(f"#### File: `{ts_file}`\n")
                        for func in funcs:
                            out.write(f"{func}\n")
                        out.write("\n")


if __name__ == "__main__":
    main()
