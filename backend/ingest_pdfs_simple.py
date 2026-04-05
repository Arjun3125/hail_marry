#!/usr/bin/env python3
"""
Simple script to ingest demo PDFs using HTTP API calls.
This avoids complex import issues and uses the actual running backend.
"""
import requests
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000"
DB_PATH = Path(__file__).parent / "demo.db"


def get_demo_token():
    """Get a demo teacher token by calling the demo-login endpoint."""
    try:
        resp = requests.post(
            f"{API_BASE}/api/auth/demo-login",
            json={"role": "teacher"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("access_token")
        else:
            print(f"Demo login failed: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"Cannot connect to backend: {e}")
        return None


def get_subject_id(token):
    """Get the first subject ID for the demo tenant."""
    try:
        resp = requests.get(
            f"{API_BASE}/api/teacher/classes",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if resp.status_code == 200:
            classes = resp.json()
            if classes and classes[0].get("subjects"):
                return classes[0]["subjects"][0]["id"]
        return None
    except Exception as e:
        print(f"Error getting subjects: {e}")
        return None


def upload_pdf_api(file_path: Path, token, subject_id=None):
    """Upload a PDF through the teacher upload API."""
    try:
        files = {"file": (file_path.name, open(file_path, "rb"), "application/pdf")}
        data = {"subject_id": subject_id} if subject_id else {}

        resp = requests.post(
            f"{API_BASE}/api/teacher/upload",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            data=data,
            timeout=60
        )

        if resp.status_code == 200:
            return resp.json()
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_ollama():
    """Check if Ollama is running."""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            embed_models = [m for m in models if "embed" in m.get("name", "").lower()]
            return len(embed_models) > 0, embed_models
        return False, []
    except Exception:
        return False, []


def main():
    print("=" * 70)
    print("VidyaOS Demo Knowledge Base - Simple HTTP Ingestion")
    print("=" * 70)
    print()

    # Check Ollama
    print("🔍 Checking Ollama...")
    has_embed, embed_models = check_ollama()
    if has_embed:
        print(f"✅ Ollama ready with embedding models: {[m['name'] for m in embed_models]}")
    else:
        print("⚠️  No embedding models found in Ollama. Ingestion may fail.")
        print("   Recommended: ollama pull nomic-embed-text")
    print()

    # Check backend
    print("🔍 Checking backend...")
    token = get_demo_token()
    if not token:
        print("❌ Cannot get demo token. Make sure backend is running:")
        print("   Run: demo.bat")
        return
    print("✅ Backend connected (got demo teacher token)")
    print()

    # Get subject
    print("🔍 Getting subject...")
    subject_id = get_subject_id(token)
    if subject_id:
        print(f"✅ Found subject: {subject_id}")
    else:
        print("⚠️  No subject found, uploading without subject association")
    print()

    # Find PDFs
    pdf_dir = Path(__file__).parent / "demo_pdfs"
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        return

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_dir}")
        return

    print(f"📚 Found {len(pdf_files)} PDF files")
    print()

    # Upload each PDF
    results = []
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Uploading: {pdf_file.name}")
        result = upload_pdf_api(pdf_file, token, subject_id)
        results.append((pdf_file.name, result))

        if result.get("success"):
            print(f"   ✅ Success - {result.get('chunks', 0)} chunks ingested")
        else:
            print(f"   ❌ Failed - {result.get('error', 'Unknown')}")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    successful = [(name, r) for name, r in results if r.get("success")]
    failed = [(name, r) for name, r in results if not r.get("success")]

    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")

    if successful:
        total = sum(r.get("chunks", 0) for _, r in successful)
        print(f"📊 Total chunks: {total}")

    if failed:
        print("\nFailed uploads:")
        for name, r in failed:
            print(f"  - {name}: {r.get('error', 'Unknown')}")

    print()
    print("=" * 70)
    print("Done! Start the demo to query your knowledge base:")
    print("  http://localhost:3000/demo")
    print("=" * 70)


if __name__ == "__main__":
    main()
