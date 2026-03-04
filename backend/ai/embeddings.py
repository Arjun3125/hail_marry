"""
Embedding Engine — generates embeddings via Ollama's nomic-embed-text model.
"""
import httpx
from typing import List
import numpy as np

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768


async def generate_embedding(text: str) -> List[float]:
    """Generate a single embedding vector using Ollama."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": text},
        )
        if response.status_code == 200:
            data = response.json()
            # Ollama returns embeddings in 'embeddings' key (list of lists)
            embeddings = data.get("embeddings", [])
            if embeddings:
                return embeddings[0]
        raise RuntimeError(f"Embedding failed: {response.status_code} {response.text}")


async def generate_embeddings_batch(texts: List[str], batch_size: int = 10) -> List[List[float]]:
    """Generate embeddings for multiple texts in batches."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/embed",
                json={"model": EMBED_MODEL, "input": batch},
            )
            if response.status_code == 200:
                data = response.json()
                embeddings = data.get("embeddings", [])
                all_embeddings.extend(embeddings)
            else:
                # Fallback: embed one by one
                for text in batch:
                    emb = await generate_embedding(text)
                    all_embeddings.append(emb)
    return all_embeddings


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_np = np.array(a)
    b_np = np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np) + 1e-8))
