

file_path = r'c:\Users\naren\Work\Projects\proxy_notebooklm\backend\src\domains\platform\services\mascot_orchestrator.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines to delete: 1250 to 1887 (inclusive, 1-indexed)
# 0-indexed: 1249 to 1886
start_idx = 1249
end_idx = 1886

new_lines = lines[:start_idx] + lines[end_idx+1:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Successfully deleted lines {start_idx+1} to {end_idx+1}")
