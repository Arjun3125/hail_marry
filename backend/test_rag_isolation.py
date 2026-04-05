"""Isolate exactly where the RAG pipeline breaks."""
import asyncio
import os

# Set env vars before importing config
os.environ.setdefault("DATABASE_URL", "sqlite:///./vidyaos_demo.db")
os.environ.setdefault("EMBEDDING_API_KEY", "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")
os.environ.setdefault("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")

from config import settings

async def main():
    print("=== RAG Pipeline Isolation Test ===\n")

    # 1. Check config
    print("1. Config Check:")
    print(f"   embedding.provider: {settings.embedding.provider}")
    print(f"   embedding.model: {settings.embedding.model}")
    print(f"   embedding.embed_dim: {settings.embedding.embed_dim}")
    print(f"   storage.vector_store_dir: {settings.storage.vector_store_dir}")
    print(f"   EMBEDDING_API_KEY set: {bool(os.getenv('EMBEDDING_API_KEY'))}")
    print(f"   OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")

    # 2. Check FAISS store directly
    print("\n2. FAISS Store Check:")
    from src.infrastructure.vector_store.vector_store import get_vector_store
    tenant_id = "cc2e868d-7dab-41a4-b474-a65fc23e843c"
    store = get_vector_store(tenant_id)
    print(f"   tenant_id: {tenant_id}")
    print(f"   chunk_count: {store.chunk_count}")
    if store.chunk_count > 0 and store.metadata:
        print(f"   first chunk text: {store.metadata[0].get('text', '')[:80]}...")
    else:
        print("   ❌ NO CHUNKS FOUND!")
        # Check if files exist at the right path
        from pathlib import Path
        vs_dir = Path(settings.storage.vector_store_dir).resolve()
        print(f"   Looking in: {vs_dir}")
        meta_path = vs_dir / f"tenant_{tenant_id}.meta.json"
        index_path = vs_dir / f"tenant_{tenant_id}.index"
        print(f"   meta exists: {meta_path.exists()}")
        print(f"   index exists: {index_path.exists()}")
        if vs_dir.exists():
            print(f"   dir contents: {list(vs_dir.iterdir())}")

    # 3. Test embedding generation
    print("\n3. Embedding Test:")
    try:
        from src.infrastructure.llm.embeddings import generate_embedding
        query = "What is the difference between displacement and distance?"
        emb = await generate_embedding(query)
        print(f"   ✅ Got embedding: dim={len(emb)}")
    except Exception as e:
        print(f"   ❌ Embedding FAILED: {type(e).__name__}: {e}")

    # 4. Test full retrieval
    if store.chunk_count > 0:
        print("\n4. Vector Search Test:")
        try:
            results = store.search(query_embedding=emb, top_k=5)
            print(f"   ✅ Found {len(results)} results")
            for meta, score in results:
                print(f"   score={score:.4f}: {meta.get('text', '')[:60]}...")
        except Exception as e:
            print(f"   ❌ Search FAILED: {e}")

        print("\n5. Full retrieve_context Test:")
        try:
            from src.infrastructure.vector_store.retrieval import retrieve_context
            chunks = await retrieve_context(query="What is the difference between displacement and distance?", tenant_id=tenant_id, top_k=5)
            print(f"   ✅ Got {len(chunks)} context chunks")
            for c in chunks:
                print(f"   [{c.get('citation')}] score={c.get('score')}: {c.get('text', '')[:60]}...")
        except Exception as e:
            print(f"   ❌ retrieve_context FAILED: {e}")

asyncio.run(main())
