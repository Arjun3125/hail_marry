#!/usr/bin/env python3
"""
Upload demo PDFs to the VidyaOS knowledge base using the real ingestion pipeline.
This script uses the teacher upload endpoint which triggers the actual RAG pipeline:
1. File upload
2. Document chunking
3. Embedding generation via Ollama
4. Vector store storage (FAISS)
"""
import os

# CRITICAL: Set these BEFORE any other imports to ensure SQLite is used
os.environ["DEMO_MODE"] = "true"
os.environ["APP_ENV"] = "local"
os.environ["DATABASE_URL"] = "sqlite:///./demo.db"
os.environ["VECTOR_STORE_PATH"] = "./vector_store"

import uuid
from pathlib import Path


def setup_demo_environment():
    """Set up the demo environment with SQLite database."""
    from database import SessionLocal
    from src.domains.identity.models.tenant import Tenant
    from src.domains.identity.models.user import User
    from src.domains.academic.models.core import Class, Subject

    db = SessionLocal()

    # Demo tenant ID from demo_seed.py
    tenant_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    teacher_id = uuid.UUID("00000000-0000-0000-0000-000000000020")

    # Check if demo data exists
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        print("❌ Demo tenant not found. Please run demo_seed.py first!")
        print("   Run: python demo_seed.py or start the demo with demo.bat")
        db.close()
        return None, None, None

    # Get teacher user
    teacher = db.query(User).filter(User.id == teacher_id).first()
    if not teacher:
        print("❌ Demo teacher not found!")
        db.close()
        return None, None, None

    # Get first class and subject for association
    db.query(Class).filter(Class.tenant_id == tenant_id).first()
    subject = db.query(Subject).filter(Subject.tenant_id == tenant_id).first()

    db.close()

    return tenant, teacher, subject


def upload_and_ingest_pdf(file_path: Path, teacher, subject):
    """Upload and ingest a single PDF through the real pipeline."""
    import asyncio
    from database import SessionLocal
    from src.domains.platform.models.document import Document
    from utils.upload_security import ensure_storage_dir
    from uuid import uuid4

    db = SessionLocal()
    UPLOAD_DIR = ensure_storage_dir("uploads")

    try:
        # Copy file to uploads directory with proper naming
        safe_filename = file_path.name
        dest_path = UPLOAD_DIR / f"{teacher.tenant_id}_{teacher.id}_{uuid4().hex}_{safe_filename}"

        with open(file_path, "rb") as src:
            content = src.read()

        with open(dest_path, "wb") as dst:
            dst.write(content)

        print(f"  📁 Saved to: {dest_path}")

        # Create document record
        doc = Document(
            tenant_id=teacher.tenant_id,
            subject_id=subject.id if subject else None,
            uploaded_by=teacher.id,
            file_name=safe_filename,
            file_type="pdf",
            storage_path=str(dest_path),
            ingestion_status="processing",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        print(f"  📝 Created document record: {doc.id}")

        # Now trigger the actual ingestion pipeline
        print("  🔄 Starting ingestion (chunking + embedding)...")

        try:
            from src.infrastructure.vector_store.ingestion import ingest_document
            from src.infrastructure.llm.embeddings import generate_embeddings_batch
            from src.infrastructure.vector_store.vector_store import get_vector_store

            chunks = ingest_document(
                file_path=str(dest_path),
                document_id=str(doc.id),
                tenant_id=str(teacher.tenant_id),
            )

            if chunks:
                print(f"  ✂️  Created {len(chunks)} chunks")

                # Generate embeddings using Ollama
                texts = [c.text for c in chunks]
                embeddings = asyncio.run(generate_embeddings_batch(texts))
                print(f"  🧠 Generated {len(embeddings)} embeddings via Ollama")

                # Store in vector store (FAISS)
                store = get_vector_store(str(teacher.tenant_id))
                chunk_dicts = [{
                    "text": c.text,
                    "document_id": c.document_id,
                    "page_number": c.page_number,
                    "section_title": c.section_title or "",
                    "subject_id": c.subject_id or "",
                    "source_file": c.source_file or "",
                } for c in chunks]
                store.add_chunks(chunk_dicts, embeddings)
                print("  💾 Stored in vector store")

                doc.ingestion_status = "completed"
                doc.chunk_count = len(chunks)
                db.commit()

                return {
                    "success": True,
                    "document_id": str(doc.id),
                    "chunks": len(chunks),
                    "file_name": safe_filename,
                }
            else:
                print("  ⚠️  No chunks created")
                doc.ingestion_status = "failed"
                db.commit()
                return {"success": False, "error": "No chunks created"}

        except Exception as e:
            print(f"  ❌ Ingestion failed: {e}")
            import traceback
            traceback.print_exc()
            doc.ingestion_status = "failed"
            db.commit()
            return {"success": False, "error": str(e)}

    finally:
        db.close()


def main():
    """Main function to upload all demo PDFs."""
    print("=" * 70)
    print("VidyaOS Demo Knowledge Base - Real Ingestion Pipeline")
    print("=" * 70)
    print()

    # Check Ollama is running
    print("🔍 Checking Ollama connection...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama connected ({len(models)} models available)")
        else:
            print(f"⚠️  Ollama returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("   Make sure Ollama is running on localhost:11434")
        return

    print()

    # Setup environment
    print("🔧 Setting up demo environment...")
    tenant, teacher, subject = setup_demo_environment()
    if not tenant or not teacher:
        return

    print("✅ Demo environment ready:")
    print(f"   Tenant: {tenant.name}")
    print(f"   Teacher: {teacher.full_name} ({teacher.email})")
    if subject:
        print(f"   Subject: {subject.name}")
    print()

    # Find PDF files
    pdf_dir = Path(__file__).parent / "demo_pdfs"
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        print("   Run create_demo_pdfs.py first!")
        return

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_dir}")
        return

    print(f"📚 Found {len(pdf_files)} PDF files to ingest")
    print()

    # Upload and ingest each PDF
    results = []
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        result = upload_and_ingest_pdf(pdf_file, teacher, subject)
        results.append(result)

        if result["success"]:
            print(f"   ✅ Success - {result['chunks']} chunks ingested")
        else:
            print(f"   ❌ Failed - {result.get('error', 'Unknown error')}")
        print()

    # Summary
    print("=" * 70)
    print("INGESTION SUMMARY")
    print("=" * 70)

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    print()

    if successful:
        total_chunks = sum(r["chunks"] for r in successful)
        print(f"📊 Total chunks ingested: {total_chunks}")
        print()
        print("Ingested documents:")
        for r in successful:
            print(f"  - {r['file_name']} ({r['chunks']} chunks)")

    if failed:
        print()
        print("Failed documents:")
        for r in failed:
            print(f"  - {r.get('file_name', 'Unknown')}: {r.get('error', 'Unknown error')}")

    print()
    print("=" * 70)
    print("Your demo knowledge base is now ready!")
    print("You can query it through the AI Assistant in the demo.")
    print("=" * 70)


if __name__ == "__main__":
    main()
