"""Script to index VidyaOS documentation into FAISS for the RAG chatbot."""
import os
import sys
import asyncio
from pathlib import Path

# Add backend root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.infrastructure.vector_store.ingestion import ingest_document
from src.infrastructure.llm.providers import get_embedding_provider, get_vector_store_provider

async def index_docs():
    # Documentation and root files are one level up from 'backend/'
    root_path = Path("..")
    docs_path = root_path / "documentation"
    if not docs_path.exists():
        print(f"Documentation folder not found at {docs_path.resolve()}.")
        return

    print("Indexing documentation for RAG chatbot...")
    
    # Collection name used by chatbot
    COLLECTION = "vidyaos_docs"
    
    files_to_index = list(docs_path.glob("**/*.md"))
    if (root_path / "README.md").exists():
        files_to_index.append(root_path / "README.md")
    if (root_path / "feature_guide.md").exists():
        files_to_index.append(root_path / "feature_guide.md")
    if (root_path / "VidyaOs_feature_guide.md").exists():
        files_to_index.append(root_path / "VidyaOs_feature_guide.md")

    embedder = get_embedding_provider()
    store = get_vector_store_provider(COLLECTION)
    
    total_count = 0
    for doc_file in files_to_index:
        try:
            print(f"Propcessing {doc_file}...")
            # Use real ingestion pipeline
            chunks = ingest_document(
                file_path=str(doc_file),
                document_id=doc_file.stem,
                tenant_id=COLLECTION
            )
            
            if not chunks:
                continue
                
            # Batch embeddings
            texts = [c.text for c in chunks]
            embeddings = await embedder.embed_batch(texts)
            
            # Map Chunk objects to dicts for store
            chunk_dicts = [
                {
                    "text": c.text,
                    "document_id": c.document_id,
                    "page_number": c.page_number,
                    "section_title": c.section_title,
                    "source_file": c.source_file,
                    "metadata": c.metadata
                }
                for c in chunks
            ]
            
            store.add_chunks(chunk_dicts, embeddings)
            total_count += len(chunks)
            print(f"  Indexed {len(chunks)} chunks from {doc_file.name}")
        except Exception as e:
            print(f"  Failed to index {doc_file}: {e}")

    print(f"\nSuccessfully indexed {total_count} chunks into '{COLLECTION}' collection.")

if __name__ == "__main__":
    asyncio.run(index_docs())
