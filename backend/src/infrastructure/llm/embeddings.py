"""
Embedding Engine — generates embeddings via Ollama's nomic-embed-text model.
"""
import httpx
from typing import List
import numpy as np
from config import settings

OLLAMA_URL = settings.embedding.url
EMBED_MODEL = settings.embedding.model
EMBED_DIM = settings.embedding.embed_dim


async def generate_embedding(text: str) -> List[float]:
    """Generate a single embedding vector."""
    if settings.embedding.provider == "openai":
        import os
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=os.getenv("EMBEDDING_API_KEY", settings.llm.openai_api_key),
            base_url=os.getenv("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1"),
        )
        response = await client.embeddings.create(
            input=text,
            model=settings.embedding.model,
            encoding_format="float",
            extra_body={"input_type": "query", "truncate": "END"}
        )
        return response.data[0].embedding

    # Ollama Default logic
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": text},
        )
        if response.status_code == 200:
            data = response.json()
            embeddings = data.get("embeddings", [])
            if embeddings:
                return embeddings[0]
        raise RuntimeError(f"Embedding failed: {response.status_code} {response.text}")


async def generate_embeddings_batch(texts: List[str], batch_size: int = 10) -> List[List[float]]:
    """Generate embeddings for multiple texts in batches."""
    if settings.embedding.provider == "openai":
        import os
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=os.getenv("EMBEDDING_API_KEY", settings.llm.openai_api_key),
            base_url=os.getenv("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1"),
        )
        response = await client.embeddings.create(
            input=texts,
            model=settings.embedding.model,
            encoding_format="float",
            extra_body={"input_type": "passage", "truncate": "END"}
        )
        return [item.embedding for item in response.data]

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
                for text in batch:
                    emb = await generate_embedding(text)
                    all_embeddings.append(emb)
    return all_embeddings


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_np = np.array(a)
    b_np = np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np) + 1e-8))
