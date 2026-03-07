import os
import re

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    # Replace VidyaOS -> VidyaOS
    new_content = content.replace("VidyaOS", "VidyaOS")
    
    # Replace vidyaos -> vidyaos (for docker containers, postgres db names, etc)
    new_content = new_content.replace("vidyaos", "vidyaos")

    if new_content != content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {filepath}")
        except Exception as e:
            print(f"Error writing {filepath}: {e}")


exclude_dirs = {'.git', 'node_modules', '.next', '.venv', '__pycache__', 'logs', '.pytest_cache'}
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if file.endswith(('.yml', '.yaml', '.md', '.py', '.ts', '.tsx', '.json', '.sh', '.bat', '.env.example', 'Makefile', '.txt', '.conf', '.js', '.mjs', '.css', '.html')):
            process_file(os.path.join(root, file))

print("Done renaming!")
