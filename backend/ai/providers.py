"""
Provider Abstraction Layer — Abstract base classes for LLM, Embedding, and VectorStore.
Enables swapping providers (Ollama → OpenAI → vLLM) without code changes.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseLLM(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> dict:
        """
        Generate text from prompt.
        Returns: {"response": str, "token_usage": int}
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass


class BaseEmbedding(ABC):
    """Abstract embedding provider interface."""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embedding vector for a single text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return embedding dimension (e.g., 768)."""
        pass


class BaseVectorStore(ABC):
    """Abstract vector store interface."""

    @abstractmethod
    def add_chunks(self, chunks: List[Dict], embeddings: List[List[float]]) -> None:
        """Add chunks with their embeddings to the store."""
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 8,
        subject_id: Optional[str] = None,
    ) -> List[tuple]:
        """Search for similar chunks. Returns list of (metadata, score) tuples."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> int:
        """Delete all chunks for a document. Returns count deleted."""
        pass

    @property
    @abstractmethod
    def chunk_count(self) -> int:
        """Total number of chunks in the store."""
        pass


class BaseParser(ABC):
    """Abstract document parser interface."""

    @abstractmethod
    def parse(self, file_path: str, **kwargs) -> List[Dict]:
        """
        Parse document into chunks.
        Returns list of dicts with: text, page_number, section_title, metadata
        """
        pass

    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        pass
