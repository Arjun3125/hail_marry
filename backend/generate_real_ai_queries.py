#!/usr/bin/env python3
"""
Generate real AI query logs using the actual knowledge base and Ollama.
This creates actual AIQuery records with real LLM-generated responses.
"""
import os
import json
import sqlite3
import pickle
import requests
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

# Paths
DB_PATH = Path(__file__).parent / "demo.db"
VECTOR_STORE_PATH = Path(__file__).parent / "vector_store"

# Demo IDs (hex format)
DEMO_TENANT_ID = "00000000000000000000000000000001"
STUDENT_IDS = [
    "00000000000000000000000000000041",  # Arjun
    "00000000000000000000000000000042",  # Priya
    "00000000000000000000000000000043",  # Rahul
    "00000000000000000000000000000044",  # Sneha
    "00000000000000000000000000000045",  # Aditya
]


def get_ollama_response(prompt: str, model: str = "llama3.1:8b-instruct-q4_0", temperature: float = 0.7) -> str:
    """Get response from Ollama API."""
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature}
            },
            timeout=120
        )
        if resp.status_code == 200:
            return resp.json().get("response", "")
        else:
            return f"Error: {resp.status_code}"
    except Exception as e:
        return f"Error: {e}"


def get_ollama_json_response(prompt: str, model: str = "llama3.1:8b-instruct-q4_0", temperature: float = 0.7) -> dict:
    """Get JSON response from Ollama API."""
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": temperature}
            },
            timeout=120
        )
        if resp.status_code == 200:
            response_text = resp.json().get("response", "{}")
            try:
                return json.loads(response_text)
            except:
                return {"response": response_text}
        else:
            return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def retrieve_context(query: str, top_k: int = 5) -> list:
    """Retrieve context chunks from vector store."""
    store_file = VECTOR_STORE_PATH / f"tenant_{DEMO_TENANT_ID}.pkl"

    if not store_file.exists():
        return []

    with open(store_file, "rb") as f:
        store = pickle.load(f)

    # Simple keyword matching for retrieval (FAISS would be better)
    query_words = set(query.lower().split())
    chunks = store.get("chunks", [])
    metadata = store.get("metadata", [])

    scored_chunks = []
    for i, (chunk, meta) in enumerate(zip(chunks, metadata)):
        chunk_words = set(chunk.lower().split())
        score = len(query_words & chunk_words)
        if score > 0:
            scored_chunks.append((score, chunk, meta))

    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    return scored_chunks[:top_k]


def save_ai_query(student_id: str, query_text: str, mode: str, response_text: str,
                  token_usage: int = 0, citations: int = 0):
    """Save AI query to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    trace_id = f"demo-trace-{uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO ai_queries (id, tenant_id, user_id, query_text, mode, response_text,
                               token_usage, response_time_ms, citation_count, trace_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        uuid4().hex,
        DEMO_TENANT_ID,
        student_id,
        query_text,
        mode,
        response_text,
        token_usage,
        len(response_text) * 4,  # Rough estimate: ~4 chars per token
        citations,
        trace_id,
        now
    ))

    conn.commit()
    conn.close()
    return trace_id


def generate_qa_queries():
    """Generate QA mode queries."""
    queries = [
        ("What is the quadratic formula?", "Mathematics"),
        ("Explain photosynthesis in simple terms", "Science"),
        ("Who is Shylock in Merchant of Venice?", "English"),
        ("What caused the Revolt of 1857?", "History"),
        ("How do I solve quadratic equations by factorization?", "Mathematics"),
        ("What are the products of light reaction in photosynthesis?", "Science"),
    ]

    results = []
    for query, subject in queries:
        print(f"\n📝 QA Query: {query[:50]}...")

        context_chunks = retrieve_context(query, top_k=3)
        context_text = "\n\n".join([f"[Doc {i+1}] {chunk}" for i, (_, chunk, _) in enumerate(context_chunks)])

        prompt = f"""You are an academic assistant for students.
Answer the following question using ONLY the provided context.
Cite sources using [Document_X] format.
If the answer is not in the context, say: "Not found in provided materials."

Question: {query}

Context from study materials:
{context_text}

Answer with citations:"""

        response = get_ollama_response(prompt, temperature=0.5)
        citations = response.count("[")

        student_id = STUDENT_IDS[len(results) % len(STUDENT_IDS)]
        trace_id = save_ai_query(student_id, query, "qa", response, citations=citations)

        print(f"   ✅ Saved (trace: {trace_id[:16]}...)")
        results.append({"mode": "qa", "query": query, "response_length": len(response)})

    return results


def generate_mindmap_queries():
    """Generate mindmap mode queries."""
    queries = [
        "Create a mind map for World War II",
        "Mind map for Photosynthesis process",
    ]

    results = []
    for query in queries:
        print(f"\n🧠 Mindmap Query: {query}")

        context_chunks = retrieve_context(query, top_k=3)
        context_text = "\n\n".join([f"[Doc {i+1}] {chunk}" for i, (_, chunk, _) in enumerate(context_chunks)])

        prompt = f"""Create a hierarchical mind map as JSON for the topic using the provided context.
The root node is the main topic. Each node has a "label" and optional "children" array.
Keep labels concise (max 5 words).

Topic: {query}

Context:
{context_text}

Output JSON:
{{"label": "Topic", "children": [{{"label": "Subtopic", "children": [{{"label": "Detail"}}]}}]}}"""

        response_data = get_ollama_json_response(prompt, temperature=0.7)
        response_json = json.dumps(response_data, indent=2)

        student_id = STUDENT_IDS[len(results) % len(STUDENT_IDS)]
        trace_id = save_ai_query(student_id, query, "mindmap", response_json)

        print(f"   ✅ Saved (trace: {trace_id[:16]}...)")
        results.append({"mode": "mindmap", "query": query})

    return results


def generate_flowchart_queries():
    """Generate flowchart mode queries."""
    queries = [
        "How does photosynthesis work?",
        "Process of solving quadratic equations",
    ]

    results = []
    for query in queries:
        print(f"\n📊 Flowchart Query: {query}")

        context_chunks = retrieve_context(query, top_k=3)
        context_text = "\n\n".join([f"[Doc {i+1}] {chunk}" for i, (_, chunk, _) in enumerate(context_chunks)])

        prompt = f"""Create a flowchart in Mermaid.js syntax for the topic using the context.
Use flowchart TD (top-down) format. Keep node labels short.
Use proper Mermaid syntax with --> for connections.
Do NOT wrap in code fences. Output ONLY raw Mermaid code.

Topic: {query}

Context:
{context_text}

Mermaid flowchart:"""

        response = get_ollama_response(prompt, temperature=0.5)

        student_id = STUDENT_IDS[len(results) % len(STUDENT_IDS)]
        trace_id = save_ai_query(student_id, query, "flowchart", response)

        print(f"   ✅ Saved (trace: {trace_id[:16]}...)")
        results.append({"mode": "flowchart", "query": query})

    return results


def generate_quiz_queries():
    """Generate quiz mode queries."""
    queries = [
        "Generate a quiz on Indian Independence Movement",
        "Quiz on Photosynthesis",
    ]

    results = []
    for query in queries:
        print(f"\n❓ Quiz Query: {query}")

        context_chunks = retrieve_context(query, top_k=4)
        context_text = "\n\n".join([f"[Doc {i+1}] {chunk}" for i, (_, chunk, _) in enumerate(context_chunks)])

        prompt = f"""Generate exactly 5 multiple-choice questions using ONLY the context.
Each question has 4 options (A, B, C, D) with one correct answer.
Format as JSON array.

Topic: {query}

Context:
{context_text}

Generate quiz as JSON:
[{{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "correct": "B"}}]"""

        response_data = get_ollama_json_response(prompt, temperature=0.7)
        response_json = json.dumps(response_data, indent=2)

        student_id = STUDENT_IDS[len(results) % len(STUDENT_IDS)]
        trace_id = save_ai_query(student_id, query, "quiz", response_json)

        print(f"   ✅ Saved (trace: {trace_id[:16]}...)")
        results.append({"mode": "quiz", "query": query})

    return results


def generate_flashcard_queries():
    """Generate flashcards mode queries."""
    queries = [
        "Create flashcards for chemical bonding",
        "Flashcards for quadratic equations",
    ]

    results = []
    for query in queries:
        print(f"\n🎴 Flashcard Query: {query}")

        context_chunks = retrieve_context(query, top_k=3)
        context_text = "\n\n".join([f"[Doc {i+1}] {chunk}" for i, (_, chunk, _) in enumerate(context_chunks)])

        prompt = f"""Create exactly 8 flashcards as JSON for the topic using the context.
Each flashcard has "front" (question/term) and "back" (answer/definition).

Topic: {query}

Context:
{context_text}

Generate flashcards as JSON:
[{{"front": "...", "back": "..."}}]"""

        response_data = get_ollama_json_response(prompt, temperature=0.7)
        response_json = json.dumps(response_data, indent=2)

        student_id = STUDENT_IDS[len(results) % len(STUDENT_IDS)]
        trace_id = save_ai_query(student_id, query, "flashcards", response_json)

        print(f"   ✅ Saved (trace: {trace_id[:16]}...)")
        results.append({"mode": "flashcards", "query": query})

    return results


def generate_socratic_queries():
    """Generate Socratic mode queries."""
    queries = [
        ("I think gravity pulls things down.", "gravity"),
        ("I know that x squared equals 4 means x is 2.", "math"),
    ]

    results = []
    for query, topic in queries:
        print(f"\n🗣️ Socratic Query: {query[:50]}...")

        context_chunks = retrieve_context(topic, top_k=3)
        context_text = "\n\n".join([f"[Doc {i+1}] {chunk}" for i, (_, chunk, _) in enumerate(context_chunks)])

        prompt = f"""You are a Socratic tutor. Guide the student toward the answer.
NEVER give the answer directly. Use clarifying counter-questions.
Be warm, patient, and encouraging.

Student's Question: {query}

Context:
{context_text}

Your Socratic Response (hints and questions only):"""

        response = get_ollama_response(prompt, temperature=0.8)

        student_id = STUDENT_IDS[len(results) % len(STUDENT_IDS)]
        trace_id = save_ai_query(student_id, query, "socratic", response)

        print(f"   ✅ Saved (trace: {trace_id[:16]}...)")
        results.append({"mode": "socratic", "query": query})

    return results


def generate_study_guide_queries():
    """Generate study guide mode queries."""
    queries = [
        "Help me understand trigonometric identities",
        "Study guide for Indian Independence Movement",
    ]

    results = []
    for query in queries:
        print(f"\n📚 Study Guide Query: {query}")

        context_chunks = retrieve_context(query, top_k=4)
        context_text = "\n\n".join([f"[Doc {i+1}] {chunk}" for i, (_, chunk, _) in enumerate(context_chunks)])

        prompt = f"""Create a structured study guide using ONLY the context.
Use clear headings, bullet points, and key takeaways.

Topic: {query}

Context:
{context_text}

Study Guide:"""

        response = get_ollama_response(prompt, temperature=0.6)

        student_id = STUDENT_IDS[len(results) % len(STUDENT_IDS)]
        trace_id = save_ai_query(student_id, query, "study_guide", response)

        print(f"   ✅ Saved (trace: {trace_id[:16]}...)")
        results.append({"mode": "study_guide", "query": query})

    return results


def generate_weak_topic_queries():
    """Generate weak topic analysis queries."""
    queries = [
        ("I am struggling with Thermodynamics", "thermodynamics"),
        ("Cell division is confusing me", "cell division"),
    ]

    results = []
    for query, topic in queries:
        print(f"\n📉 Weak Topic Query: {query}")

        context_chunks = retrieve_context(topic, top_k=3)
        context_text = "\n\n".join([f"[Doc {i+1}] {chunk}" for i, (_, chunk, _) in enumerate(context_chunks)])

        prompt = f"""The student is weak in: {query}
Using the study materials, create a TARGETED remediation plan:
1. Key concepts they likely missed
2. Brief explanation of each
3. Practice exercises

Context:
{context_text}

Remediation Plan:"""

        response = get_ollama_response(prompt, temperature=0.6)

        student_id = STUDENT_IDS[0]  # Arjun is weak
        trace_id = save_ai_query(student_id, query, "weak_topic", response)

        print(f"   ✅ Saved (trace: {trace_id[:16]}...)")
        results.append({"mode": "weak_topic", "query": query})

    return results


def generate_concept_map_queries():
    """Generate concept map mode queries."""
    queries = [
        "Explain the water cycle with a concept map",
    ]

    results = []
    for query in queries:
        print(f"\n🕸️ Concept Map Query: {query}")

        context_chunks = retrieve_context(query, top_k=3)
        context_text = "\n\n".join([f"[Doc {i+1}] {chunk}" for i, (_, chunk, _) in enumerate(context_chunks)])

        prompt = f"""Create a concept map from the context about the topic.
Output as JSON with nodes and edges.

Topic: {query}

Context:
{context_text}

Output JSON:
{{"nodes": [{{"id": "1", "label": "..."}}], "edges": [{{"from": "1", "to": "2", "label": "..."}}]}}"""

        response_data = get_ollama_json_response(prompt, temperature=0.7)
        response_json = json.dumps(response_data, indent=2)

        student_id = STUDENT_IDS[len(results) % len(STUDENT_IDS)]
        trace_id = save_ai_query(student_id, query, "concept_map", response_json)

        print(f"   ✅ Saved (trace: {trace_id[:16]}...)")
        results.append({"mode": "concept_map", "query": query})

    return results


def main():
    print("=" * 70)
    print("Generating Real AI Query Logs with Ollama + Knowledge Base")
    print("=" * 70)
    print()

    # Check Ollama
    print("🔍 Checking Ollama...")
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            print("✅ Ollama connected")
        else:
            print(f"❌ Ollama status: {resp.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return

    # Check database
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return
    print(f"✅ Database: {DB_PATH}")

    # Check vector store
    store_file = VECTOR_STORE_PATH / f"tenant_{DEMO_TENANT_ID}.pkl"
    if not store_file.exists():
        print(f"❌ Vector store not found. Run ingest_standalone.py first!")
        return
    print(f"✅ Vector store: {store_file}")
    print()

    # Generate queries for each mode
    all_results = []

    print("Generating QA queries...")
    all_results.extend(generate_qa_queries())

    print("\nGenerating mindmap queries...")
    all_results.extend(generate_mindmap_queries())

    print("\nGenerating flowchart queries...")
    all_results.extend(generate_flowchart_queries())

    print("\nGenerating quiz queries...")
    all_results.extend(generate_quiz_queries())

    print("\nGenerating flashcard queries...")
    all_results.extend(generate_flashcard_queries())

    print("\nGenerating Socratic queries...")
    all_results.extend(generate_socratic_queries())

    print("\nGenerating study guide queries...")
    all_results.extend(generate_study_guide_queries())

    print("\nGenerating weak topic queries...")
    all_results.extend(generate_weak_topic_queries())

    print("\nGenerating concept map queries...")
    all_results.extend(generate_concept_map_queries())

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ Generated {len(all_results)} AI query logs")

    # Count by mode
    mode_counts = {}
    for r in all_results:
        mode = r["mode"]
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

    print("\nBy mode:")
    for mode, count in sorted(mode_counts.items()):
        print(f"  - {mode}: {count} queries")

    print()
    print("=" * 70)
    print("Real AI query data is now in the demo database!")
    print("The demo will show actual LLM-generated responses.")
    print("=" * 70)


if __name__ == "__main__":
    main()
