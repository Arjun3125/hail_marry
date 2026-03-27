#!/usr/bin/env python3
"""
Generate demo AI history data for all demo students.
Creates folders and populates AI query history with realistic timestamps.
"""
import os
import json
import sqlite3
import random
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta, timezone

# Paths
DB_PATH = Path(__file__).parent / "demo.db"

# Demo IDs
DEMO_TENANT_ID = "00000000000000000000000000000001"
STUDENT_IDS = [
    "00000000000000000000000000000041",  # Arjun
    "00000000000000000000000000000042",  # Priya
    "00000000000000000000000000000043",  # Rahul
    "00000000000000000000000000000044",  # Sneha
    "00000000000000000000000000000045",  # Aditya
]

# Sample AI interactions for realistic demo data
SAMPLE_QUERIES = {
    "qa": [
        ("What is the quadratic formula?", "The quadratic formula is x = (-b ± √(b²-4ac)) / 2a. It helps solve any quadratic equation of the form ax² + bx + c = 0."),
        ("Explain photosynthesis in simple terms", "Photosynthesis is how plants make food using sunlight, water, and CO2. It happens in the chloroplasts and produces glucose and oxygen."),
        ("Who was Shylock in Merchant of Venice?", "Shylock is a Jewish moneylender and the main antagonist. He's known for demanding a pound of flesh as collateral."),
        ("What caused the Revolt of 1857?", "The revolt was caused by political, economic, and social grievances against British rule, including the cartridge incident."),
        ("How do I solve linear equations?", "Isolate the variable by performing the same operation on both sides. Move constants to one side and variables to the other."),
    ],
    "study_guide": [
        ("Study guide for Chemical Bonding", "## Chemical Bonding Study Guide\\n\\n### Ionic Bonds\\n- Transfer of electrons\\n- Metal + Non-metal\\n\\n### Covalent Bonds\\n- Sharing of electrons\\n- Non-metal + Non-metal\\n\\n### Key Points\\n- Electronegativity difference determines bond type\\n- Ionic compounds conduct electricity when dissolved"),
        ("Help me understand Trigonometry", "## Trigonometry Basics\\n\\n### SOH CAH TOA\\n- Sin = Opposite/Hypotenuse\\n- Cos = Adjacent/Hypotenuse\\n- Tan = Opposite/Adjacent\\n\\n### Special Angles\\n- sin(30°) = 1/2\\n- cos(45°) = √2/2\\n- tan(60°) = √3"),
    ],
    "quiz": [
        ("Quiz on Indian Independence", '{"questions": [{"question": "Who led the Salt March?", "options": ["Nehru", "Gandhi", "Bose", "Patel"], "correct": "B"}, {"question": "When did India gain independence?", "options": ["1945", "1946", "1947", "1948"], "correct": "C"}]}'),
        ("Quiz on Photosynthesis", '{"questions": [{"question": "What gas do plants absorb?", "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"], "correct": "B"}, {"question": "Where does photosynthesis occur?", "options": ["Roots", "Stem", "Chloroplasts", "Nucleus"], "correct": "C"}]}'),
    ],
    "mindmap": [
        ("Mind map for World War II", '{"label": "World War II", "children": [{"label": "Causes", "children": [{"label": "Treaty of Versailles"}, {"label": "Economic Crisis"}, {"label": "Rise of Fascism"}]}, {"label": "Major Events", "children": [{"label": "Invasion of Poland"}, {"label": "Pearl Harbor"}, {"label": "D-Day"}]}, {"label": "Outcomes", "children": [{"label": "UN Formation"}, {"label": "Cold War Begins"}]}]}'),
        ("Mind map for Cell Structure", '{"label": "Cell", "children": [{"label": "Nucleus", "children": [{"label": "DNA"}, {"label": "Nucleolus"}]}, {"label": "Cytoplasm", "children": [{"label": "Mitochondria"}, {"label": "Ribosomes"}, {"label": "Golgi Body"}]}, {"label": "Cell Membrane"}]}'),
    ],
    "flowchart": [
        ("How does digestion work?", "graph TD; A[Food Intake] --> B[Mechanical Digestion]; B --> C[Chemical Digestion]; C --> D[Absorption]; D --> E[Circulation]; E --> F[Waste Elimination]"),
        ("Steps to solve quadratic equations", "graph TD; A[Identify coefficients a,b,c] --> B{Is a=0?}; B -->|Yes| C[Linear equation]; B -->|No| D[Calculate discriminant]; D --> E{Discriminant > 0?}; E -->|Yes| F[Two real roots]; E -->|No| G[Check other cases]")
    ],
    "flashcards": [
        ("Flashcards for Physics formulas", '[{"front": "Newton\'s Second Law", "back": "F = ma (Force = mass × acceleration)"}, {"front": "Kinetic Energy", "back": "KE = ½mv²"}, {"front": "Potential Energy", "back": "PE = mgh"}, {"front": "Ohm\'s Law", "back": "V = IR"}]'),
        ("Flashcards for Biology terms", '[{"front": "Mitosis", "back": "Cell division producing two identical daughter cells"}, {"front": "Photosynthesis", "back": "Process converting light energy into chemical energy"}, {"front": "Osmosis", "back": "Movement of water across a semi-permeable membrane"}, {"front": "Diffusion", "back": "Movement of molecules from high to low concentration"}]'),
    ],
    "socratic": [
        ("I think gravity pulls everything down equally", "That's a thoughtful observation! But consider this: if you drop a feather and a hammer from the same height on Earth, do they land at the same time? What about on the Moon?"),
        ("Plants get their food from soil", "Interesting idea! But if that were true, wouldn't the soil eventually run out of nutrients? What else might plants need to grow? Have you noticed they grow toward light?"),
    ],
    "concept_map": [
        ("Concept map for Ecosystem", '{"nodes": [{"id": "1", "label": "Ecosystem"}, {"id": "2", "label": "Producers"}, {"id": "3", "label": "Consumers"}, {"id": "4", "label": "Decomposers"}, {"id": "5", "label": "Energy Flow"}], "edges": [{"from": "1", "to": "2", "label": "contains"}, {"from": "1", "to": "3", "label": "contains"}, {"from": "1", "to": "4", "label": "contains"}, {"from": "2", "to": "5", "label": "provides"}]}'),
    ],
}


def generate_title(query: str, mode: str) -> str:
    """Generate a concise title from query."""
    # Simple heuristic-based title generation
    words = query.split()
    if len(words) <= 5:
        return query
    
    # Remove common stop words and take first 3-5 meaningful words
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", 
                  "being", "have", "has", "had", "do", "does", "did", "will",
                  "would", "could", "should", "may", "might", "must", "shall",
                  "can", "need", "dare", "ought", "used", "to", "for", "in",
                  "on", "at", "by", "with", "from", "about", "me", "my", "i",
                  "help", "create", "generate", "explain", "what", "how"}
    
    meaningful = [w for w in words[:8] if w.lower() not in stop_words]
    title = " ".join(meaningful[:5])
    return title if title else query[:50]


def create_folders_for_student(conn, student_id: str) -> list:
    """Create demo folders for a student."""
    cursor = conn.cursor()
    folders = []
    
    folder_data = [
        ("Mathematics", "blue"),
        ("Science", "green"),
        ("English Literature", "purple"),
        ("History", "orange"),
        ("Exam Prep", "red"),
        ("Quick Access", "yellow"),
    ]
    
    for name, color in folder_data:
        folder_id = uuid4().hex
        cursor.execute("""
            INSERT INTO ai_folders (id, tenant_id, user_id, name, color, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            folder_id,
            DEMO_TENANT_ID,
            student_id,
            name,
            color,
            datetime.now(timezone.utc).isoformat()
        ))
        folders.append({"id": folder_id, "name": name, "color": color})
    
    return folders


def create_history_item(conn, student_id: str, mode: str, query: str, response: str, 
                        folder_id: str = None, is_pinned: bool = False, days_ago: int = 0):
    """Create a single AI history item."""
    cursor = conn.cursor()
    
    item_id = uuid4().hex
    created_at = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(0, 23))
    
    title = generate_title(query, mode)
    token_usage = random.randint(200, 1500)
    response_time = random.randint(800, 3500)
    citation_count = random.randint(0, 5)
    
    cursor.execute("""
        INSERT INTO ai_queries (id, tenant_id, user_id, query_text, mode, response_text,
                               token_usage, response_time_ms, citation_count, created_at,
                               title, is_pinned, folder_id, trace_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item_id,
        DEMO_TENANT_ID,
        student_id,
        query,
        mode,
        response,
        token_usage,
        response_time,
        citation_count,
        created_at.isoformat(),
        title,
        is_pinned,
        folder_id,
        f"demo-trace-{uuid4().hex[:12]}",
    ))
    
    return item_id


def generate_student_history(conn, student_id: str, folders: list):
    """Generate diverse AI history for a student."""
    # Distribute items across last 30 days
    
    # Create 5-8 QA items
    for _ in range(random.randint(5, 8)):
        query, response = random.choice(SAMPLE_QUERIES["qa"])
        folder = random.choice([None, folders[0]["id"], folders[1]["id"]])  # Math/Science
        days_ago = random.randint(0, 30)
        create_history_item(conn, student_id, "qa", query, response, folder, False, days_ago)
    
    # Create 2-3 study guides
    for _ in range(random.randint(2, 3)):
        query, response = random.choice(SAMPLE_QUERIES["study_guide"])
        folder = random.choice([folders[0]["id"], folders[1]["id"]])  # Math/Science
        days_ago = random.randint(3, 25)
        create_history_item(conn, student_id, "study_guide", query, response, folder, False, days_ago)
    
    # Create 2-3 quizzes
    for _ in range(random.randint(2, 3)):
        query, response = random.choice(SAMPLE_QUERIES["quiz"])
        folder = random.choice([folders[2]["id"], folders[3]["id"]])  # English/History
        days_ago = random.randint(5, 28)
        is_pinned = random.random() > 0.7  # 30% chance of being pinned
        create_history_item(conn, student_id, "quiz", query, response, folder, is_pinned, days_ago)
    
    # Create 2-4 mind maps
    for _ in range(random.randint(2, 4)):
        query, response = random.choice(SAMPLE_QUERIES["mindmap"])
        folder = random.choice([folders[3]["id"], folders[4]["id"]])  # History/Exam Prep
        days_ago = random.randint(1, 20)
        create_history_item(conn, student_id, "mindmap", query, response, folder, False, days_ago)
    
    # Create 2-3 flowcharts
    for _ in range(random.randint(2, 3)):
        query, response = random.choice(SAMPLE_QUERIES["flowchart"])
        folder = random.choice([folders[1]["id"], folders[4]["id"]])  # Science/Exam Prep
        days_ago = random.randint(2, 15)
        create_history_item(conn, student_id, "flowchart", query, response, folder, False, days_ago)
    
    # Create 3-4 flashcard sets
    for _ in range(random.randint(3, 4)):
        query, response = random.choice(SAMPLE_QUERIES["flashcards"])
        folder = random.choice([folders[0]["id"], folders[1]["id"], folders[4]["id"]])
        days_ago = random.randint(1, 10)
        is_pinned = random.random() > 0.6  # 40% chance of being pinned
        create_history_item(conn, student_id, "flashcards", query, response, folder, is_pinned, days_ago)
    
    # Create 1-2 socratic dialogs
    for _ in range(random.randint(1, 2)):
        query, response = random.choice(SAMPLE_QUERIES["socratic"])
        days_ago = random.randint(0, 7)  # More recent
        create_history_item(conn, student_id, "socratic", query, response, None, False, days_ago)
    
    # Create 1-2 concept maps
    for _ in range(random.randint(1, 2)):
        query, response = random.choice(SAMPLE_QUERIES["concept_map"])
        folder = folders[1]["id"]  # Science
        days_ago = random.randint(1, 14)
        create_history_item(conn, student_id, "concept_map", query, response, folder, False, days_ago)
    
    # Create some "yesterday's work" items (1-2 days ago)
    for _ in range(random.randint(2, 4)):
        mode = random.choice(["qa", "mindmap", "flowchart", "flashcards"])
        query, response = random.choice(SAMPLE_QUERIES[mode])
        days_ago = random.choice([1, 2])
        create_history_item(conn, student_id, mode, query, response, None, False, days_ago)


def main():
    print("=" * 70)
    print("Generating Demo AI History Data")
    print("=" * 70)
    print()
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Check if new columns exist, add them if needed
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(ai_queries)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if "title" not in columns:
            print("Adding new columns to ai_queries table...")
            cursor.execute("ALTER TABLE ai_queries ADD COLUMN title TEXT")
            cursor.execute("ALTER TABLE ai_queries ADD COLUMN is_pinned BOOLEAN DEFAULT 0")
            cursor.execute("ALTER TABLE ai_queries ADD COLUMN folder_id TEXT")
            cursor.execute("ALTER TABLE ai_queries ADD COLUMN deleted_at TIMESTAMP")
            conn.commit()
        
        # Check if ai_folders table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_folders'")
        if not cursor.fetchone():
            print("Creating ai_folders table...")
            cursor.execute("""
                CREATE TABLE ai_folders (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    color TEXT DEFAULT 'blue',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX idx_ai_folders_user ON ai_folders(user_id, tenant_id)")
            conn.commit()
        
        # Clear existing AI queries to avoid duplicates
        print("Clearing existing AI history...")
        cursor.execute("DELETE FROM ai_queries WHERE tenant_id = ?", (DEMO_TENANT_ID,))
        cursor.execute("DELETE FROM ai_folders WHERE tenant_id = ?", (DEMO_TENANT_ID,))
        conn.commit()
        
        # Generate for each student
        total_items = 0
        for student_id in STUDENT_IDS:
            print(f"\nGenerating for student: {student_id[:16]}...")
            
            # Create folders
            folders = create_folders_for_student(conn, student_id)
            print(f"  📁 Created {len(folders)} folders")
            
            # Generate history
            generate_student_history(conn, student_id, folders)
            
            # Count items
            cursor.execute(
                "SELECT COUNT(*) FROM ai_queries WHERE user_id = ? AND tenant_id = ?",
                (student_id, DEMO_TENANT_ID)
            )
            count = cursor.fetchone()[0]
            total_items += count
            print(f"  ✅ Created {count} AI history items")
        
        conn.commit()
        print()
        print("=" * 70)
        print(f"✅ Successfully created {total_items} AI history items")
        print(f"   for {len(STUDENT_IDS)} demo students")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
