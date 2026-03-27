#!/usr/bin/env python3
"""Show sample AI responses from the database."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "demo.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Sample AI Responses (Real LLM-generated):")
print("=" * 80)

# Get a few different modes
cursor.execute("""
    SELECT mode, query_text, response_text 
    FROM ai_queries 
    WHERE mode IN ('qa', 'mindmap', 'flowchart', 'socratic', 'quiz')
    ORDER BY mode, rowid
    LIMIT 5
""")

for mode, query, response in cursor.fetchall():
    print(f"\n{'='*80}")
    print(f"Mode: {mode.upper()}")
    print(f"Query: {query}")
    print(f"{'-'*80}")
    # Show first 500 chars of response
    resp_preview = response[:500] if len(response) > 500 else response
    if len(response) > 500:
        resp_preview += "..."
    print(f"Response:\n{resp_preview}")

conn.close()
