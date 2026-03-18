import os
import shutil
import re
from pathlib import Path

# Domains mapping
DOMAINS = {
    "identity": {
        "models": ["user.py", "tenant.py", "token_blacklist.py", "invitation.py", "onboarding.py", "role.py"],
        "routes": ["auth.py", "enterprise.py", "invitations.py", "onboarding.py"],
        "services": ["auth.py", "saml_sso.py", "team_invite.py", "onboarding.py", "token_blacklist.py"],
        "schemas": ["auth.py", "enterprise.py", "invitations.py", "onboarding.py", "user.py", "tenant.py"]
    },
    "academic": {
        "models": ["student.py", "teacher.py", "parent.py", "class_subject.py", "attendance.py", "marks.py", "exam.py", "assignment.py", "test_series.py"],
        "routes": ["students.py", "teacher.py", "parent.py"],
        "services": ["attendance.py", "exam.py", "assignment.py", "report_card.py", "leaderboard.py", "whatsapp.py"],
        "schemas": ["student.py", "teacher.py", "parent.py", "attendance.py", "exam.py", "assignment.py"]
    },
    "administrative": {
        "models": ["billing.py", "fee.py", "admission.py", "library.py", "incident.py"],
        "routes": ["admin.py", "superadmin.py", "billing.py", "fees.py", "admission.py", "library.py"],
        "services": ["admin.py", "billing.py", "fee_management.py", "admission.py", "library.py", "incident.py", "compliance.py"],
        "schemas": ["admin.py", "billing.py", "fee.py", "admission.py", "library.py", "incident.py", "compliance.py"]
    },
    "ai_engine": {
        "models": ["ai_job.py", "knowledge_graph.py", "document.py"],
        "routes": ["ai.py", "ai_jobs.py", "audio.py", "video.py", "discovery.py", "documents.py", "openai_compat.py"],
        "services": ["ai_queue.py", "doc_watcher.py", "knowledge_graph.py", "llm_providers.py", "docs_chatbot.py"],
        "schemas": ["ai_runtime.py", "ai_jobs.py", "audio.py", "video.py", "documents.py", "knowledge_graph.py", "openai_compat.py"]
    },
    "platform": {
        "models": ["webhook.py", "alert.py", "trace.py"],
        "routes": ["support.py", "i18n.py", "demo.py", "demo_management.py", "notifications.py"],
        "services": ["alerting.py", "metrics_registry.py", "startup_checks.py", "sentry_config.py", "structured_logging.py", "telemetry.py", "runtime_scheduler.py", "observability_notifier.py", "trace_backend.py", "i18n.py", "plugin_registry.py", "webhooks.py"],
        "schemas": ["support.py", "i18n.py", "demo.py", "webhooks.py", "trace.py", "alert.py"]
    }
}

def main():
    base_dir = Path("c:/Users/naren/Work/Projects/proxy_notebooklm/backend")
    src_domains = base_dir / "src" / "domains"
    
    # 1. Create Directories
    for domain in DOMAINS:
        for folder in ["models", "routes", "services", "schemas"]:
            (src_domains / domain / folder).mkdir(parents=True, exist_ok=True)
            # Create __init__.py files
            (src_domains / domain / folder / "__init__.py").touch(exist_ok=True)
            (src_domains / domain / "__init__.py").touch(exist_ok=True)
            
    # 2. Build mapping and move files
    # Dictionary mapping old dot-path to new dot-path, e.g., "models.user" -> "src.domains.identity.models.user"
    import_map = {}
    
    # Track files moved, relative path
    moved_files = []
    
    for domain, categories in DOMAINS.items():
        for category, files in categories.items():
            for filename in files:
                old_path = base_dir / category / filename
                if old_path.exists():
                    new_path = src_domains / domain / category / filename
                    shutil.move(old_path, new_path)
                    
                    # Store import mapping without the .py extension
                    module_name = filename.replace(".py", "")
                    if module_name != "__init__":
                        old_dot = f"{category}.{module_name}"
                        new_dot = f"src.domains.{domain}.{category}.{module_name}"
                        import_map[old_dot] = new_dot
                        
    # 3. What about files not explicitly mapped? Move them to platform by default or leave them?
    # Let's leave them for now to avoid breaking too widely if unmapped.

    # 4. Search and Replace Imports in ALL python files
    print(f"Built {len(import_map)} import mappings. Updating files...")
    all_py_files = list(base_dir.rglob("*.py"))
    
    for py_file in all_py_files:
        # Ignore venv or node_modules if present
        if ".venv" in py_file.parts or "node_modules" in py_file.parts:
            continue
            
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            original = content
            # Strategy: replace "from src.domains.identity.models.user import" -> "from src.domains.identity.models.user import"
            # and "import src.domains.identity.models.user" -> "import src.domains.identity.models.user"
            
            for old_dot, new_dot in import_map.items():
                content = re.sub(rf"\bfrom {old_dot}\b", f"from {new_dot}", content)
                content = re.sub(rf"\bimport {old_dot}\b", f"import {new_dot}", content)
                
            if original != content:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Updated imports in {py_file.name}")
                    
        except Exception as e:
            print(f"Failed to process {py_file}: {e}")
            
    # Let's also move the `ai` folder into `src/domains/ai_engine/ai`
    ai_folder = base_dir / "ai"
    if ai_folder.exists() and ai_folder.is_dir():
        new_ai_target = src_domains / "ai_engine" / "ai"
        if not new_ai_target.exists():
            shutil.move(str(ai_folder), str(new_ai_target))
            print(f"Moved ai folder to {new_ai_target}")
            
        # Update references from "ai." to "src.domains.ai_engine.ai."
        for py_file in all_py_files:
            if ".venv" in py_file.parts: continue
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                orig = content
                content = re.sub(r"\bfrom ai\.", "from src.domains.ai_engine.ai.", content)
                content = re.sub(r"\bimport ai\.", "import src.domains.ai_engine.ai.", content)
                if orig != content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Updated ai. imports in {py_file.name}")
            except Exception as e:
                pass

if __name__ == "__main__":
    main()
    print("Migration complete.")
