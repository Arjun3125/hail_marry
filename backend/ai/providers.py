"""
Provider abstraction layer for LLM, embeddings, and vector store access.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from hashlib import sha1
from typing import Dict, List, Optional

import httpx

from config import settings
from ai.embeddings import generate_embedding, generate_embeddings_batch
from ai.vector_store import get_vector_store


class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_model_name(self) -> str:
        raise NotImplementedError


class BaseEmbedding(ABC):
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        raise NotImplementedError

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    @abstractmethod
    def get_dimension(self) -> int:
        raise NotImplementedError


class BaseVectorStore(ABC):
    @abstractmethod
    def add_chunks(self, chunks: List[Dict], embeddings: List[List[float]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 8,
        subject_id: Optional[str] = None,
    ) -> List[tuple]:
        raise NotImplementedError

    @abstractmethod
    def delete_document(self, document_id: str) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def chunk_count(self) -> int:
        raise NotImplementedError


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str, **kwargs) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def supported_extensions(self) -> List[str]:
        raise NotImplementedError


class OllamaLLM(BaseLLM):
    async def generate(self, prompt: str, **kwargs) -> dict:
        model = kwargs.get("model", settings.llm.model)
        num_predict = kwargs.get("num_predict", settings.llm.max_new_tokens)
        temperature = kwargs.get("temperature", settings.llm.temperature)

        async with httpx.AsyncClient(timeout=settings.llm.timeout_seconds) as client:
            response = await client.post(
                f"{settings.llm.url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": num_predict,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            return {
                "response": data.get("response", ""),
                "token_usage": data.get("eval_count", 0),
            }

    def get_model_name(self) -> str:
        return settings.llm.model


class OllamaEmbedding(BaseEmbedding):
    async def embed(self, text: str) -> List[float]:
        return await generate_embedding(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return await generate_embeddings_batch(texts)

    def get_dimension(self) -> int:
        return settings.embedding.embed_dim


class TenantVectorStoreAdapter(BaseVectorStore):
    def __init__(self, tenant_id: str):
        self.store = get_vector_store(tenant_id)

    def add_chunks(self, chunks: List[Dict], embeddings: List[List[float]]) -> None:
        self.store.add_chunks(chunks, embeddings)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 8,
        subject_id: Optional[str] = None,
    ) -> List[tuple]:
        return self.store.search(query_embedding=query_embedding, top_k=top_k, subject_id=subject_id)

    def delete_document(self, document_id: str) -> int:
        before = self.store.chunk_count
        self.store.delete_document(document_id)
        return max(before - self.store.chunk_count, 0)

    @property
    def chunk_count(self) -> int:
        return self.store.chunk_count


class QdrantVectorStoreAdapter(BaseVectorStore):
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.collection_name = f"{settings.vector_backend.collection_prefix}{tenant_id}".replace("-", "_")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if settings.vector_backend.qdrant_api_key:
            headers["api-key"] = settings.vector_backend.qdrant_api_key
        return headers

    def _base_url(self) -> str:
        return settings.vector_backend.qdrant_url.rstrip("/")

    def _ensure_collection(self) -> None:
        with httpx.Client(timeout=settings.vector_backend.timeout_seconds) as client:
            response = client.put(
                f"{self._base_url()}/collections/{self.collection_name}",
                headers=self._headers(),
                json={
                    "vectors": {
                        "size": settings.embedding.embed_dim,
                        "distance": "Cosine",
                    }
                },
            )
            if response.status_code not in (200, 201):
                response.raise_for_status()

    def add_chunks(self, chunks: List[Dict], embeddings: List[List[float]]) -> None:
        if not chunks or not embeddings:
            return
        self._ensure_collection()
        points = []
        for chunk, embedding in zip(chunks, embeddings, strict=False):
            point_id = sha1(f"{self.collection_name}:{chunk.get('document_id')}:{chunk.get('text')}".encode("utf-8")).hexdigest()
            points.append({
                "id": point_id,
                "vector": embedding,
                "payload": chunk,
            })
        with httpx.Client(timeout=settings.vector_backend.timeout_seconds) as client:
            response = client.put(
                f"{self._base_url()}/collections/{self.collection_name}/points?wait=true",
                headers=self._headers(),
                json={"points": points},
            )
            response.raise_for_status()

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 8,
        subject_id: Optional[str] = None,
    ) -> List[tuple]:
        self._ensure_collection()
        payload: dict = {
            "vector": query_embedding,
            "limit": top_k,
            "with_payload": True,
        }
        if subject_id:
            payload["filter"] = {
                "must": [
                    {
                        "key": "subject_id",
                        "match": {"value": subject_id},
                    }
                ]
            }
        with httpx.Client(timeout=settings.vector_backend.timeout_seconds) as client:
            response = client.post(
                f"{self._base_url()}/collections/{self.collection_name}/points/search",
                headers=self._headers(),
                json=payload,
            )
            if response.status_code == 404:
                return []
            response.raise_for_status()
            items = response.json().get("result", [])
        return [(item.get("payload", {}), float(item.get("score", 0.0))) for item in items]

    def delete_document(self, document_id: str) -> int:
        before = self.chunk_count
        self._ensure_collection()
        with httpx.Client(timeout=settings.vector_backend.timeout_seconds) as client:
            response = client.post(
                f"{self._base_url()}/collections/{self.collection_name}/points/delete?wait=true",
                headers=self._headers(),
                json={
                    "filter": {
                        "must": [
                            {
                                "key": "document_id",
                                "match": {"value": document_id},
                            }
                        ]
                    }
                },
            )
            if response.status_code not in (200, 202, 404):
                response.raise_for_status()
        return max(before - self.chunk_count, 0)

    @property
    def chunk_count(self) -> int:
        with httpx.Client(timeout=settings.vector_backend.timeout_seconds) as client:
            response = client.post(
                f"{self._base_url()}/collections/{self.collection_name}/points/count",
                headers=self._headers(),
                json={"exact": True},
            )
            if response.status_code == 404:
                return 0
            response.raise_for_status()
            return int(response.json().get("result", {}).get("count", 0))


def get_llm_provider() -> BaseLLM:
    return OllamaLLM()


def get_embedding_provider() -> BaseEmbedding:
    return OllamaEmbedding()


def get_vector_store_provider(tenant_id: str) -> BaseVectorStore:
    if settings.vector_backend.provider.lower() == "qdrant":
        return QdrantVectorStoreAdapter(tenant_id)
    return TenantVectorStoreAdapter(tenant_id)
