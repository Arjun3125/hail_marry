import os
import shutil
import re
from pathlib import Path

BACKEND_DIR = Path(r"c:\Users\naren\Work\Projects\proxy_notebooklm\backend")
SRC_DIR = BACKEND_DIR / "src"
AI_ENGINE_DIR = SRC_DIR / "domains" / "ai_engine"
PLATFORM_DIR = SRC_DIR / "domains" / "platform"

# Define directories to move into platform
DIRS_TO_MOVE = ["models", "schemas", "services"]

IMPORT_REWRITES = [
    # General package renames
    ("src.domains.platform.models", "src.domains.platform.models"),
    ("src.domains.platform.schemas", "src.domains.platform.schemas"),
    ("src.domains.platform.services", "src.domains.platform.services")
]

def process():
    print("🚀 Starting AI Engine Models/Schemas/Services Migration Script...")
    
    # 1. Move files
    for d_name in DIRS_TO_MOVE:
        source_dir = AI_ENGINE_DIR / d_name
        target_dir = PLATFORM_DIR / d_name
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        if source_dir.exists():
            for fpath in source_dir.iterdir():
                if fpath.is_file() and fpath.name != "__init__.py" and fpath.suffix == ".py":
                    target_file = target_dir / fpath.name
                    print(f"Moving {fpath.relative_to(BACKEND_DIR)} -> {target_file.relative_to(BACKEND_DIR)}")
                    shutil.move(str(fpath), str(target_file))
        else:
            print(f"⚠️ Source {source_dir.relative_to(BACKEND_DIR)} not found.")

    # 2. Rewrite internal imports across the codebase
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
                # Direct imports: `import src.domains.platform.models...`
                content = re.sub(r'\b' + re.escape(old_imp) + r'\b', new_imp, content)
                
            if content != original_content:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Updated imports in {fpath.relative_to(BACKEND_DIR)}")
                
        except Exception as e:
            print(f"❌ Failed to process {fpath}: {str(e)}")

    print("\n🗑️ Deleting src/domains/ai_engine entirely...")
    if AI_ENGINE_DIR.exists():
        shutil.rmtree(str(AI_ENGINE_DIR))
        print("✅ Deleted ai_engine domain directory.")

    print("\n✅ Migration complete! Run `pytest` to catch any remaining issues.")

if __name__ == "__main__":
    process()
