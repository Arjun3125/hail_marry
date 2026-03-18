import os
from pathlib import Path

domains = {
    "identity": {
        "routes": ["auth", "enterprise", "invitations", "onboarding"]
    },
    "academic": {
        "routes": ["students", "teacher", "parent"]
    },
    "administrative": {
        "routes": ["admin", "superadmin", "billing", "fees", "admission", "library"]
    },
    "ai_engine": {
        "routes": ["ai", "ai_jobs", "audio", "video", "discovery", "documents", "openai_compat"]
    },
    "platform": {
        "routes": ["support", "i18n", "demo", "demo_management", "notifications"]
    }
}

base_dir = Path("c:/Users/naren/Work/Projects/proxy_notebooklm/backend")

# 1. Generate Domain Routers
for domain_name, data in domains.items():
    router_content = "from fastapi import APIRouter\n\n"
    
    # Imports
    for rt in data["routes"]:
        router_content += f"from .routes import {rt}\n"
        
    router_content += "\nrouter = APIRouter()\n"
    
    # Includes
    for rt in data["routes"]:
        router_content += f"router.include_router({rt}.router)\n"
        
    router_file = base_dir / "src" / "domains" / domain_name / "router.py"
    with open(router_file, "w", encoding="utf-8") as f:
        f.write(router_content)
    print(f"Created {router_file}")

# 2. Rewrite main.py
main_py_path = base_dir / "main.py"
with open(main_py_path, "r", encoding="utf-8") as f:
    main_content = f.read()

# Remove old massive route imports
import re
# Regex to remove lines like: from routes import auth as auth_routes
# and app.include_router(auth_routes.router)
main_lines = main_content.split('\n')
new_lines = []
skip_mode = False
for line in main_lines:
    if "from routes import" in line or "app.include_router(" in line or "from routes" in line:
        continue
    new_lines.append(line)

new_main = "\n".join(new_lines)

# Inject the new domain routers right before the demo seed logic
injection_point = "\n# ── Auto-seed in DEMO_MODE ──"

domain_imports = """
# ==============================================================================
# Domain-Driven Design (DDD) Bounded Context Routers
# ==============================================================================
from src.domains.identity.router import router as identity_router
from src.domains.academic.router import router as academic_router
from src.domains.administrative.router import router as administrative_router
from src.domains.ai_engine.router import router as ai_engine_router
from src.domains.platform.router import router as platform_router

app.include_router(identity_router)
app.include_router(academic_router)
app.include_router(administrative_router)
app.include_router(ai_engine_router)
app.include_router(platform_router)

"""
new_main = new_main.replace(injection_point, domain_imports + injection_point)

with open(main_py_path, "w", encoding="utf-8") as f:
    f.write(new_main)
print("Updated main.py to use DDD routers")
