"""Quick analysis of _create_user_and_login usage in test_mascot_routes.py."""
import re

src = open("tests/test_mascot_routes.py", encoding="utf-8").read()

# Find all unique emails
emails = re.findall(r'email="([^"]+)"', src)
unique = set(emails)
print(f"Total email params: {len(emails)}")
print(f"Unique emails: {len(unique)}")

# Find duplicates
from collections import Counter
c = Counter(emails)
dups = [(e, n) for e, n in c.items() if n > 1]
if dups:
    print(f"\nDuplicated emails: {dups}")

# Count how many tests call _create_user_and_login
tests = re.findall(r'^def (test_\w+)\(', src, re.MULTILINE)
tests_with_create = []
for m in re.finditer(r'^def (test_\w+)\(', src, re.MULTILINE):
    name = m.group(1)
    # Find the body until the next def
    start = m.end()
    next_def = src.find('\ndef test_', start)
    if next_def == -1:
        next_def = len(src)
    body = src[start:next_def]
    if '_create_user_and_login' in body:
        count = body.count('_create_user_and_login')
        tests_with_create.append((name, count))

print(f"\nTotal tests: {len(tests)}")
print(f"Tests calling _create_user_and_login: {len(tests_with_create)}")
print(f"Tests with multiple calls: {[(n, c) for n, c in tests_with_create if c > 1]}")
