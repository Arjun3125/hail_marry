"""LLM-Wiki Knowledge Infrastructure — Karpathy-pattern persistent wiki.

This package implements a persistent, compounding knowledge base that replaces
traditional RAG as the primary retrieval strategy. The wiki is maintained by
an LLM agent that incrementally updates interlinked Markdown pages on every
document ingest. At query time the wiki is searched first; traditional vector
RAG is kept as a fallback for edge cases.
"""
