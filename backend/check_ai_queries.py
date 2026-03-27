#!/usr/bin/env python3
"""Quick script to check AI query logs in the database."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "demo.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("AI Query Logs Summary:")
print("=" * 80)

cursor.execute("SELECT mode, query_text, citation_count FROM ai_queries ORDER BY mode")
rows = cursor.fetchall()

for mode, query, citations in rows:
    print(f"{mode:12} | {query[:50]:50} | citations: {citations}")

cursor.execute("SELECT COUNT(*) FROM ai_queries")
total = cursor.fetchone()[0]

print("=" * 80)
print(f"Total queries: {total}")

# Count by mode
print("\nBy mode:")
cursor.execute("SELECT mode, COUNT(*) FROM ai_queries GROUP BY mode ORDER BY COUNT(*) DESC")
for mode, count in cursor.fetchall():
    print(f"  {mode}: {count}")

conn.close()
