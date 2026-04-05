import json
from collections import defaultdict
import os

try:
    with open('ruff_errors.json', 'r', encoding='utf-8-sig') as f:
        errors = json.load(f)
        
    summary = defaultdict(lambda: defaultdict(list))
    for e in errors:
        file_path = os.path.relpath(e['filename'], os.getcwd())
        summary[e['code']][file_path].append(e)

    with open('ruff_errors.txt', 'w', encoding='utf-8') as f_out:
        for code in sorted(summary.keys()):
            f_out.write(f"\n--- {code} ---\n")
            for file_path, errs in summary[code].items():
                f_out.write(f"{file_path}: {len(errs)} error(s)\n")
                for err in errs:
                    f_out.write(f"  Line {err['location']['row']}: {err['message']}\n")
except Exception as e:
    print(f"Error: {e}")
