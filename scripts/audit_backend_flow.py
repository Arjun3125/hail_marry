import os
import ast
from pathlib import Path
import json

def get_fastapi_endpoints(backend_dir):
    endpoints = []
    routes_dir = Path(backend_dir) / "routes"
    all_files = []
    
    for root, _, files in os.walk(backend_dir):
        if "venv" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                all_files.append(Path(root) / f)

    routers = {}
    for path in all_files:
        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if getattr(target, "id", None) and isinstance(node.value, ast.Call):
                            if getattr(node.value.func, "id", None) == "APIRouter":
                                prefix = ""
                                for kw in node.value.keywords:
                                    if kw.arg == "prefix" and hasattr(kw.value, "value"):
                                        prefix = kw.value.value
                                routers[target.id] = {"path": str(path), "prefix": prefix}
                                
                if isinstance(node, ast.FunctionDef):
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                            method = dec.func.attr.upper()
                            if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                                route_path = ""
                                if dec.args and hasattr(dec.args[0], "value"):
                                    route_path = dec.args[0].value
                                endpoints.append({
                                    "file": str(path.relative_to(backend_dir)),
                                    "function": node.name,
                                    "method": method,
                                    "route": route_path,
                                    "router_name": dec.func.value.id if hasattr(dec.func.value, "id") else None
                                })
        except Exception:
            pass
            
    for ep in endpoints:
        r_name = ep.get("router_name")
        if r_name and r_name in routers:
            prefix = routers[r_name]["prefix"]
            ep["full_route"] = prefix + ep["route"]
        else:
            ep["full_route"] = ep["route"]
            
    return endpoints

if __name__ == "__main__":
    backend_dir = r"c:\Users\naren\Work\Projects\proxy_notebooklm\backend"
    endpoints = get_fastapi_endpoints(backend_dir)
    with open(r"c:\Users\naren\Work\Projects\proxy_notebooklm\backend_endpoints.json", "w", encoding="utf-8") as f:
        json.dump(endpoints, f, indent=2)
