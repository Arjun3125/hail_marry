import os
import shutil
import re
from pathlib import Path

BACKEND_DIR = Path(r"c:\Users\naren\Work\Projects\proxy_notebooklm\backend")
SRC_DIR = BACKEND_DIR / "src"
AI_ENGINE_DIR = SRC_DIR / "domains" / "ai_engine" / "ai"

# Define the moves mapping (source_file, target_directory, target_filename)
MOVES = [
    # Infrastructure: LLM
    ("cache.py", "infrastructure/llm", "cache.py"),
    ("providers.py", "infrastructure/llm", "providers.py"),
    ("embeddings.py", "infrastructure/llm", "embeddings.py"),
    
    # Infrastructure: Vector Store
    ("vector_store.py", "infrastructure/vector_store", "vector_store.py"),
    ("retrieval.py", "infrastructure/vector_store", "retrieval.py"),
    ("ingestion.py", "infrastructure/vector_store", "ingestion.py"),
    ("ocr_service.py", "infrastructure/vector_store", "ocr_service.py"),
    ("connectors.py", "infrastructure/vector_store", "connectors.py"),
    ("hyde.py", "infrastructure/vector_store", "hyde.py"),
    ("citation_linker.py", "infrastructure/vector_store", "citation_linker.py"),

    # Interfaces: REST API
    ("agent_orchestrator.py", "interfaces/rest_api/ai", "agent_orchestrator.py"),
    ("discovery_workflows.py", "interfaces/rest_api/ai", "discovery_workflows.py"),
    ("teacher_workflows.py", "interfaces/rest_api/ai", "teacher_workflows.py"),
    ("workflows.py", "interfaces/rest_api/ai", "workflows.py"),
    ("ingestion_workflows.py", "interfaces/rest_api/ai", "ingestion_workflows.py"),

    # Interfaces: WhatsApp Bot
    ("whatsapp_agent.py", "interfaces/whatsapp_bot", "agent.py"),
]

# We also need to move the router.py from ai_engine to interfaces/rest_api/ai
ROUTER_MOVE = (SRC_DIR / "domains" / "ai_engine" / "router.py", SRC_DIR / "interfaces" / "rest_api" / "ai" / "router.py")

IMPORT_REWRITES = []

# Generate import rewrite rules based on moves
for s_name, t_dir, t_name in MOVES:
    old_module = "src.domains.ai_engine.ai." + s_name.replace(".py", "")
    new_module = "src." + t_dir.replace("/", ".") + "." + t_name.replace(".py", "")
    IMPORT_REWRITES.append((old_module, new_module))

# Router module rewrite
IMPORT_REWRITES.append(("src.interfaces.rest_api.ai.router", "src.interfaces.rest_api.ai.router"))

def process():
    print("🚀 Starting AI Engine Refactoring Script...")
    
    # 1. Create target directories
    for _, t_dir, _ in MOVES:
        target_path = SRC_DIR / Path(t_dir)
        target_path.mkdir(parents=True, exist_ok=True)
    
    # Also create the rest API ai dir for the router
    (SRC_DIR / "interfaces" / "rest_api" / "ai").mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files in new directories
    for d in ["infrastructure", "infrastructure/llm", "infrastructure/vector_store", "interfaces", "interfaces/rest_api", "interfaces/rest_api/ai", "interfaces/whatsapp_bot"]:
        init_file = SRC_DIR / Path(d) / "__init__.py"
        if not init_file.exists():
            init_file.touch()

    # 2. Move files
    for s_name, t_dir, t_name in MOVES:
        source_file = AI_ENGINE_DIR / s_name
        target_file = SRC_DIR / Path(t_dir) / t_name
        
        if source_file.exists():
            print(f"Moving {source_file.relative_to(BACKEND_DIR)} -> {target_file.relative_to(BACKEND_DIR)}")
            shutil.move(str(source_file), str(target_file))
        else:
            print(f"⚠️ Source {source_file.relative_to(BACKEND_DIR)} not found, might already be moved.")

    if ROUTER_MOVE[0].exists():
        print(f"Moving router: {ROUTER_MOVE[0].relative_to(BACKEND_DIR)} -> {ROUTER_MOVE[1].relative_to(BACKEND_DIR)}")
        shutil.move(str(ROUTER_MOVE[0]), str(ROUTER_MOVE[1]))
        
    # 3. Rewrite internal imports inside the python files
    print("\n📝 Rewriting imports across the codebase...")
    py_files = list(BACKEND_DIR.rglob("*.py"))
    
    for fpath in py_files:
        if "__pycache__" in str(fpath) or ".venv" in str(fpath):
            continue
            
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                
            original_content = content
            
            for old_imp, new_imp in IMPORT_REWRITES:
                # Direct imports: `import src.infrastructure.llm.cache`
                content = re.sub(r'\b' + re.escape(old_imp) + r'\b', new_imp, content)
                # From imports: `from src.infrastructure.llm.cache import ...` -> `from src.infrastructure.llm.cache import ...`
                
            if content != original_content:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Updated imports in {fpath.relative_to(BACKEND_DIR)}")
                
        except Exception as e:
            print(f"❌ Failed to process {fpath}: {str(e)}")

    print("\n✅ Migration complete! Run `pytest` to catch any remaining issues.")

if __name__ == "__main__":
    process()
