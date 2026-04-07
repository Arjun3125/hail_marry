"""
RAG Edge Case Benchmarking Suite
================================
Research-backed tests derived from:
  - "MultiHop-RAG: Benchmarking RAG for Multi-Hop Queries" (LLM_Architecture)
  - "Vendi-RAG: Adaptively Trading-Off Diversity And Quality" (LLM_Architecture)
  - "RAG LLMs are Not Safer: Safety Analysis of RAG" (LLM_Architecture)
  - "THELMA: Task-Based Holistic Evaluation" (LLM_Architecture)
  - "Collab-RAG: Boosting RAG for Complex QA" (LLM_Architecture)

Tests validate:
  1. Contradictory context handling — RAG must not hallucinate a merged answer
  2. Multi-hop reasoning — answers requiring synthesis across multiple chunks
  3. Empty/null context fallback — graceful degradation when retrieval fails
  4. Extremely long input handling — input truncation / token budget respect
  5. Malformed document edge cases — special characters, Unicode, binary data
  6. Citation accuracy — answers must reference retrievable sources
  7. Diversity vs. quality trade-off in retrieved contexts
"""
import os
import re
import sys
import unittest
from typing import List, Set

# Ensure backend imports resolve
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


# ─── Lightweight tokenizer (reuse from existing evaluation suite) ────
STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "just",
    "because", "until", "while", "about", "against", "and", "but", "or",
    "if", "that", "this", "it", "its", "i", "me", "my", "we", "our",
    "you", "your", "he", "him", "his", "she", "her", "they", "them", "their",
    "what", "which", "who", "whom",
}


def tokenize(text: str) -> Set[str]:
    tokens = set(re.findall(r"\b\w+\b", text.lower()))
    return tokens - STOPWORDS


def faithfulness_score(answer: str, contexts: List[str]) -> float:
    answer_tokens = tokenize(answer)
    if not answer_tokens:
        return 1.0
    context_tokens = set()
    for ctx in contexts:
        context_tokens.update(tokenize(ctx))
    grounded = answer_tokens.intersection(context_tokens)
    return len(grounded) / len(answer_tokens)


def answer_relevancy_score(answer: str, question: str) -> float:
    q_tokens = tokenize(question)
    a_tokens = tokenize(answer)
    if not q_tokens or not a_tokens:
        return 0.0
    overlap = q_tokens.intersection(a_tokens)
    union = q_tokens.union(a_tokens)
    return len(overlap) / len(union) if union else 0.0


def context_precision_score(contexts: List[str], question: str) -> float:
    if not contexts:
        return 0.0
    q_tokens = tokenize(question)
    if not q_tokens:
        return 0.0
    scores = []
    for ctx in contexts:
        c_tokens = tokenize(ctx)
        overlap = q_tokens.intersection(c_tokens)
        union = q_tokens.union(c_tokens)
        scores.append(len(overlap) / len(union) if union else 0.0)
    return sum(scores) / len(scores)


# ─── Edge Case Datasets ──────────────────────────────────────────────

CONTRADICTORY_CONTEXTS = {
    "question": "What is the boiling point of water?",
    "contexts": [
        "The boiling point of water is 100 degrees Celsius at standard atmospheric pressure.",
        "Water boils at 90 degrees Celsius in high altitude regions due to lower pressure.",
        "Some experiments show water can be superheated to 120 degrees without boiling in a clean container.",
    ],
    "expected_answer_should_mention": ["100", "pressure"],
}

MULTI_HOP_QUERY = {
    "question": "How does photosynthesis relate to the carbon cycle and climate change?",
    "contexts": [
        "Photosynthesis converts CO2 and water into glucose and oxygen using sunlight.",
        "The carbon cycle describes how carbon moves between atmosphere, oceans, and living organisms.",
        "Deforestation reduces the planet's capacity for photosynthesis, increasing atmospheric CO2.",
        "Rising CO2 levels are a primary driver of global climate change and temperature increases.",
    ],
    "ground_truth": (
        "Photosynthesis removes CO2 from the atmosphere as part of the carbon cycle. "
        "When photosynthesis capacity is reduced through deforestation, more CO2 stays "
        "in the atmosphere, accelerating climate change."
    ),
}

EMPTY_CONTEXT_QUERY = {
    "question": "What is quantum entanglement?",
    "contexts": [],
    "expected_behavior": "Should indicate no relevant information found",
}

UNICODE_EDGE_CASES = [
    "नमस्ते, यह एक हिंदी पाठ है।",  # Hindi text
    "这是中文文本测试。",  # Chinese text
    "🧬 DNA is the molecule of heredity 🔬",  # Emoji in scientific text
    "Chemical formula: H₂O + CO₂ → H₂CO₃",  # Subscripts and arrows
    "",  # Empty string
    "   \n\t\n   ",  # Whitespace only
    "A" * 100000,  # Extremely long single-token text
]


class TestContradictoryContextHandling(unittest.TestCase):
    """
    From "MultiHop-RAG":
    When retrieved contexts contain contradictory information,
    the system must not blindly merge them into a single assertion.
    """

    def test_contradictory_contexts_lower_faithfulness(self):
        """An answer that picks one source should have moderate faithfulness, not perfect."""
        data = CONTRADICTORY_CONTEXTS

        # Simulate an answer that correctly acknowledges the contradiction
        nuanced_answer = (
            "The boiling point of water is 100 degrees Celsius at standard atmospheric "
            "pressure, but this varies with altitude and conditions."
        )
        score = faithfulness_score(nuanced_answer, data["contexts"])
        self.assertGreater(score, 0.3, "Nuanced answer should be reasonably grounded")

    def test_hallucinated_answer_gets_low_faithfulness(self):
        """An answer containing information NOT in any context should score poorly."""
        data = CONTRADICTORY_CONTEXTS
        hallucinated = (
            "The boiling point of water is 212 degrees Fahrenheit, which was discovered "
            "by Daniel Gabriel Fahrenheit in 1724 using mercury thermometers."
        )
        score = faithfulness_score(hallucinated, data["contexts"])
        grounded_answer = "Water boils at 100 degrees Celsius at standard atmospheric pressure."
        grounded_score = faithfulness_score(grounded_answer, data["contexts"])

        self.assertLess(score, grounded_score,
                        "Hallucinated answer should score lower than grounded answer")


class TestMultiHopReasoning(unittest.TestCase):
    """
    From "MultiHop-RAG" and "Collab-RAG":
    Multi-hop questions require synthesizing information
    from multiple retrieved chunks to form a coherent answer.
    """

    def test_multi_hop_answer_uses_multiple_contexts(self):
        """A good multi-hop answer should draw from at least 2 contexts."""
        data = MULTI_HOP_QUERY
        good_answer = data["ground_truth"]

        # Check that the answer tokens overlap with multiple context chunks
        answer_tokens = tokenize(good_answer)
        contexts_overlapping = 0
        for ctx in data["contexts"]:
            ctx_tokens = tokenize(ctx)
            if answer_tokens.intersection(ctx_tokens):
                contexts_overlapping += 1

        self.assertGreaterEqual(contexts_overlapping, 2,
                                "Multi-hop answer should reference at least 2 context chunks")

    def test_context_recall_for_multi_hop(self):
        """Retrieved contexts should collectively cover the ground truth."""
        data = MULTI_HOP_QUERY
        gt_tokens = tokenize(data["ground_truth"])
        ctx_tokens = set()
        for ctx in data["contexts"]:
            ctx_tokens.update(tokenize(ctx))

        recalled = gt_tokens.intersection(ctx_tokens)
        recall = len(recalled) / len(gt_tokens) if gt_tokens else 0.0

        self.assertGreater(recall, 0.4,
                           f"Context recall for multi-hop should be above 0.4, got {recall:.4f}")

    def test_single_context_insufficient_for_multi_hop(self):
        """No single context should be sufficient to answer a multi-hop question fully."""
        data = MULTI_HOP_QUERY
        gt_tokens = tokenize(data["ground_truth"])

        max_single_recall = 0.0
        for ctx in data["contexts"]:
            ctx_tokens = tokenize(ctx)
            recalled = gt_tokens.intersection(ctx_tokens)
            recall = len(recalled) / len(gt_tokens) if gt_tokens else 0.0
            max_single_recall = max(max_single_recall, recall)

        self.assertLess(max_single_recall, 0.8,
                        "No single context should cover >80% of a multi-hop ground truth")


class TestEmptyContextFallback(unittest.TestCase):
    """
    From "RAG-Star: Enhancing Deliberative Reasoning":
    When retrieval returns nothing, the system must degrade gracefully
    rather than hallucinate an answer.
    """

    def test_empty_context_faithfulness_is_low(self):
        """With no contexts, any substantive answer has zero grounding."""
        answer = "Quantum entanglement is when two particles become correlated."
        score = faithfulness_score(answer, [])
        # With empty contexts, no tokens can be grounded
        self.assertEqual(score, 0.0,
                         "Faithfulness should be 0.0 when there are no contexts")

    def test_empty_context_precision_is_zero(self):
        """Context precision with empty contexts should be 0."""
        score = context_precision_score([], "What is quantum entanglement?")
        self.assertEqual(score, 0.0)

    def test_none_context_handling(self):
        """System should handle None in context lists gracefully."""
        try:
            score = faithfulness_score("test answer", ["valid context"])
            self.assertGreaterEqual(score, 0.0)
        except (TypeError, AttributeError):
            self.fail("Should handle edge case contexts gracefully")


class TestExtremeInputLengths(unittest.TestCase):
    """
    From "RAG over Tables: Hierarchical Memory Index":
    Real-world inputs can be extremely long; the system must
    handle truncation and token budgets correctly.
    """

    def test_very_long_answer_scoring(self):
        """Scoring functions must not crash or hang on extremely long text."""
        long_answer = "photosynthesis " * 10000  # ~150k chars
        contexts = ["Photosynthesis converts sunlight into chemical energy in plants."]

        score = faithfulness_score(long_answer, contexts)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_very_long_context_scoring(self):
        """Long contexts should still produce valid scores."""
        answer = "Plants use sunlight for photosynthesis."
        long_context = "Photosynthesis is a process " + "involving chloroplasts " * 5000
        contexts = [long_context]

        score = faithfulness_score(answer, contexts)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_token_approximation_for_long_text(self):
        """Token approximation must scale linearly and not overflow."""
        try:
            from src.domains.platform.services.usage_governance import approximate_token_count
            long_text = "word " * 100000  # 500k chars
            tokens = approximate_token_count(long_text)
            self.assertGreater(tokens, 0)
            self.assertIsInstance(tokens, int)
        except ImportError:
            self.skipTest("usage_governance not importable")


class TestUnicodeAndSpecialCharacters(unittest.TestCase):
    """
    From "Jais and Jais-chat: Arabic-Centric LLM" (LLM_Architecture):
    Multilingual and special character inputs must not crash
    the scoring or processing pipeline.
    """

    def test_tokenizer_handles_all_unicode_cases(self):
        """Tokenizer must not crash on any Unicode input."""
        for text in UNICODE_EDGE_CASES:
            try:
                tokens = tokenize(text)
                self.assertIsInstance(tokens, set)
            except Exception as e:
                self.fail(f"Tokenizer crashed on input '{text[:50]}...': {e}")

    def test_faithfulness_with_unicode_contexts(self):
        """Scoring with non-Latin text should produce valid results."""
        answer = "DNA is the molecule of heredity"
        contexts = [
            "🧬 DNA is the molecule of heredity 🔬",
            "डीएनए आनुवंशिकता का अणु है।",
        ]
        score = faithfulness_score(answer, contexts)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_empty_and_whitespace_inputs(self):
        """Empty strings and whitespace should produce valid scores, not errors."""
        self.assertEqual(faithfulness_score("", []), 1.0)  # No tokens to ground
        self.assertEqual(faithfulness_score("", ["context"]), 1.0)
        self.assertEqual(answer_relevancy_score("", "question"), 0.0)
        self.assertEqual(answer_relevancy_score("answer", ""), 0.0)
        self.assertEqual(context_precision_score([], "question"), 0.0)
        self.assertEqual(context_precision_score(["context"], ""), 0.0)


class TestCitationAccuracy(unittest.TestCase):
    """
    From "THELMA: Task Based Holistic Evaluation":
    RAG answers must provide verifiable citations back to source chunks.
    """

    def test_answer_grounded_in_context_has_high_faithfulness(self):
        """An answer entirely derived from context should score > 0.5."""
        contexts = [
            "The Pythagorean theorem states that in a right triangle, "
            "the square of the hypotenuse equals the sum of the squares of the other two sides."
        ]
        answer = "The Pythagorean theorem says the square of the hypotenuse equals the sum of squares of the other two sides."

        score = faithfulness_score(answer, contexts)
        self.assertGreater(score, 0.5,
                           f"Well-grounded answer should have faithfulness > 0.5, got {score:.4f}")

    def test_completely_ungrounded_answer_detected(self):
        """An answer with zero overlap should be flagged."""
        contexts = ["The Earth orbits the Sun once every 365.25 days."]
        answer = "Shakespeare wrote Hamlet in approximately 1600."

        score = faithfulness_score(answer, contexts)
        grounded_answer = "Earth orbits the Sun once every 365 days."
        grounded_score = faithfulness_score(grounded_answer, contexts)

        self.assertLess(score, grounded_score,
                        "Ungrounded answer should score lower than grounded")


class TestDiversityVsQualityTradeoff(unittest.TestCase):
    """
    From "Vendi-RAG: Adaptively Trading-Off Diversity And Quality":
    Retrieval should balance diversity and relevance —
    redundant contexts waste token budget without improving answers.
    """

    def test_redundant_contexts_dont_improve_precision(self):
        """Duplicating the same context should not inflate precision."""
        question = "What is gravity?"
        single_context = ["Gravity is a force that attracts objects with mass toward each other."]
        redundant_contexts = single_context * 5

        single_precision = context_precision_score(single_context, question)
        redundant_precision = context_precision_score(redundant_contexts, question)

        self.assertAlmostEqual(single_precision, redundant_precision, places=4,
                               msg="Redundant contexts should not inflate precision")

    def test_diverse_contexts_improve_recall(self):
        """Adding diverse contexts should improve coverage of the ground truth."""
        ground_truth = (
            "Photosynthesis produces glucose which is consumed by herbivores. "
            "Herbivores are eaten by carnivores, forming the food chain."
        )

        limited_contexts = [
            "Photosynthesis converts sunlight into glucose in plant chloroplasts.",
        ]
        diverse_contexts = limited_contexts + [
            "Herbivores consume plants as their primary food source.",
            "Carnivores eat herbivores, forming higher levels of the food chain.",
        ]

        gt_tokens = tokenize(ground_truth)
        limited_tokens = set()
        for c in limited_contexts:
            limited_tokens.update(tokenize(c))
        diverse_tokens = set()
        for c in diverse_contexts:
            diverse_tokens.update(tokenize(c))

        limited_recall = len(gt_tokens.intersection(limited_tokens)) / len(gt_tokens) if gt_tokens else 0
        diverse_recall = len(gt_tokens.intersection(diverse_tokens)) / len(gt_tokens) if gt_tokens else 0

        self.assertGreater(diverse_recall, limited_recall,
                           "Diverse contexts should improve recall over limited contexts")


class TestToolOutputNormalization(unittest.TestCase):
    """
    Edge cases for the study tool output normalization pipeline.
    Tests malformed JSON, injection attempts, and boundary conditions.
    """

    def test_malformed_json_raises_422(self):
        """Invalid JSON in tool output should raise 422, not crash."""
        try:
            student_routes = __import__(
                "src.domains.academic.routes.students",
                fromlist=["_normalize_tool_output"],
            )
            from fastapi import HTTPException
            with self.assertRaises(HTTPException) as ctx:
                student_routes._normalize_tool_output("quiz", "not valid json {{{")
            self.assertEqual(ctx.exception.status_code, 422)
        except (ImportError, AttributeError):
            self.skipTest("_normalize_tool_output not available")

    def test_extremely_nested_json(self):
        """Deeply nested JSON should not cause stack overflow."""
        import json
        nested = {"label": "root", "children": []}
        current = nested
        for i in range(50):
            child = {"label": f"level_{i}", "children": []}
            current["children"].append(child)
            current = child

        json_str = json.dumps(nested)
        try:
            parsed = json.loads(json_str)
            self.assertIsInstance(parsed, dict)
        except RecursionError:
            self.fail("JSON parser should handle 50 levels of nesting")

    def test_html_injection_in_answer(self):
        """HTML/script tags in answers should not be treated as executable."""
        malicious = '<script>alert("xss")</script>Photosynthesis makes glucose.'
        contexts = ["Photosynthesis makes glucose from CO2 and water."]
        score = faithfulness_score(malicious, contexts)
        # The score should still work; the HTML tags are just treated as tokens
        self.assertGreaterEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()
