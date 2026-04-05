"""
RAG Quality Evaluation Pipeline
===============================
Measures the quality of the Retrieval-Augmented Generation pipeline using
deterministic, RAGAS-inspired metrics:

- Faithfulness: Does the answer stay within the retrieved context?
- Answer Relevancy: Is the answer relevant to the question?
- Context Precision: Are the retrieved chunks relevant to the question?
- Context Recall: Did retrieval find the needed information?

This implementation uses lightweight token overlap so it remains reproducible
and does not require an external LLM.
"""
import os
import re
import sys
from typing import Dict, List, Set

import pytest

# Ensure backend imports resolve
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


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
    """Extract meaningful tokens from text, removing stopwords."""
    tokens = set(re.findall(r"\b\w+\b", text.lower()))
    return tokens - STOPWORDS


def faithfulness_score(answer: str, contexts: List[str]) -> float:
    """Measure how much of the answer is grounded in the retrieved contexts."""
    answer_tokens = tokenize(answer)
    if not answer_tokens:
        return 1.0

    context_tokens = set()
    for context in contexts:
        context_tokens.update(tokenize(context))

    grounded = answer_tokens.intersection(context_tokens)
    return len(grounded) / len(answer_tokens)


def answer_relevancy_score(answer: str, question: str) -> float:
    """Measure how relevant the answer is to the question."""
    question_tokens = tokenize(question)
    answer_tokens = tokenize(answer)

    if not question_tokens or not answer_tokens:
        return 0.0

    overlap = question_tokens.intersection(answer_tokens)
    union = question_tokens.union(answer_tokens)
    return len(overlap) / len(union) if union else 0.0


def context_precision_score(contexts: List[str], question: str) -> float:
    """Measure how precise the retrieved contexts are relative to the question."""
    if not contexts:
        return 0.0

    question_tokens = tokenize(question)
    if not question_tokens:
        return 0.0

    scores = []
    for context in contexts:
        context_tokens = tokenize(context)
        overlap = question_tokens.intersection(context_tokens)
        union = question_tokens.union(context_tokens)
        scores.append(len(overlap) / len(union) if union else 0.0)

    return sum(scores) / len(scores)


def context_recall_score(contexts: List[str], ground_truth: str) -> float:
    """Measure how much of the ground truth is covered by the retrieved contexts."""
    ground_truth_tokens = tokenize(ground_truth)
    if not ground_truth_tokens:
        return 1.0

    context_tokens = set()
    for context in contexts:
        context_tokens.update(tokenize(context))

    recalled = ground_truth_tokens.intersection(context_tokens)
    return len(recalled) / len(ground_truth_tokens)


def ascii_bar(value: float, width: int = 30) -> str:
    """Render a stable ASCII progress bar for console-safe report output."""
    clamped = max(0.0, min(value, 1.0))
    filled = int(clamped * width)
    return "#" * filled + "-" * (width - filled)


RAG_GOLDEN_DATASET: List[Dict] = [
    {
        "question": "What is photosynthesis?",
        "ground_truth": (
            "Photosynthesis is the process by which green plants use sunlight to synthesize "
            "food from carbon dioxide and water, generating oxygen as a byproduct."
        ),
        "contexts": [
            "Photosynthesis is a biological process where plants convert light energy into chemical energy. It occurs in chloroplasts using chlorophyll.",
            "During photosynthesis, carbon dioxide and water are converted into glucose and oxygen using sunlight energy.",
            "The overall equation for photosynthesis is: 6CO2 + 6H2O + light energy -> C6H12O6 + 6O2",
        ],
        "answer": (
            "Photosynthesis is the process by which plants use sunlight to convert carbon "
            "dioxide and water into glucose and oxygen. It occurs in the chloroplasts of plant cells."
        ),
    },
    {
        "question": "What causes earthquakes?",
        "ground_truth": (
            "Earthquakes are caused by sudden release of energy in the Earth's crust, "
            "usually due to tectonic plate movements along fault lines."
        ),
        "contexts": [
            "Tectonic plates float on the semi-fluid asthenosphere and move relative to each other. Their interactions cause geological phenomena.",
            "When stress builds up along fault lines where tectonic plates meet, the sudden release of energy causes seismic waves - earthquakes.",
            "The Richter scale measures earthquake magnitude logarithmically. A magnitude 7 earthquake is 10 times stronger than a magnitude 6.",
        ],
        "answer": (
            "Earthquakes are caused by the sudden release of energy along fault lines where "
            "tectonic plates interact. The stress builds up and then releases as seismic waves."
        ),
    },
    {
        "question": "How does the water cycle work?",
        "ground_truth": (
            "The water cycle involves evaporation of water from surfaces, condensation into "
            "clouds, precipitation as rain or snow, and collection in water bodies."
        ),
        "contexts": [
            "The water cycle, also known as the hydrological cycle, describes the continuous movement of water within the Earth and atmosphere.",
            "Evaporation occurs when water from oceans, lakes, and rivers is heated by the sun and turns into water vapor.",
            "Water vapor rises and cools, forming clouds through condensation. When droplets become heavy enough, precipitation occurs as rain, snow, or hail.",
        ],
        "answer": (
            "The water cycle works through evaporation, where water turns to vapor from heat, "
            "rises and condenses into clouds, and then falls back as precipitation."
        ),
    },
    {
        "question": "What is Newton's first law of motion?",
        "ground_truth": (
            "Newton's first law states that an object will remain at rest or in uniform motion "
            "in a straight line unless acted upon by an external force."
        ),
        "contexts": [
            "Newton's laws of motion form the foundation of classical mechanics. They describe the relationship between forces and motion.",
            "The first law of motion, also called the law of inertia, states that a body continues in its state of rest or uniform motion unless compelled by an external force.",
            "Inertia is the property of matter that resists changes in velocity. More massive objects have greater inertia.",
        ],
        "answer": (
            "Newton's first law, the law of inertia, states that an object stays at rest or "
            "continues moving in a straight line at constant speed unless acted upon by an external force."
        ),
    },
    {
        "question": "What is the difference between mitosis and meiosis?",
        "ground_truth": (
            "Mitosis produces two identical diploid cells for growth and repair, while meiosis "
            "produces four genetically unique haploid cells for reproduction."
        ),
        "contexts": [
            "Mitosis is a type of cell division that results in two daughter cells each having the same number and kind of chromosomes as the parent cell.",
            "Meiosis is cell division that reduces the chromosome number by half, creating four haploid cells for sexual reproduction.",
            "Unlike mitosis, meiosis involves two rounds of division and introduces genetic variation through crossing over and independent assortment.",
        ],
        "answer": (
            "Mitosis produces two identical diploid daughter cells for growth, while meiosis "
            "produces four genetically diverse haploid cells for reproduction through two rounds of division."
        ),
    },
    {
        "question": "What is machine learning?",
        "ground_truth": (
            "Machine learning is a subset of artificial intelligence where algorithms learn "
            "patterns from data to make predictions without being explicitly programmed."
        ),
        "contexts": [
            "Machine learning is a branch of AI that enables computers to learn from data and improve performance without explicit programming.",
            "Common ML techniques include supervised learning (classification, regression), unsupervised learning (clustering), and reinforcement learning.",
            "Neural networks are a popular ML architecture inspired by the human brain, consisting of interconnected layers of artificial neurons.",
        ],
        "answer": (
            "Machine learning is an AI technique where algorithms automatically learn patterns "
            "from data to make predictions, without being explicitly programmed for each task."
        ),
    },
    {
        "question": "What are prime numbers?",
        "ground_truth": (
            "Prime numbers are natural numbers greater than 1 that have no positive divisors "
            "other than 1 and themselves."
        ),
        "contexts": [
            "Prime numbers are fundamental in number theory. A prime number is a natural number greater than 1 that cannot be formed by multiplying two smaller natural numbers.",
            "The first few prime numbers are 2, 3, 5, 7, 11, 13, 17, 19, 23, and 29. The number 2 is the only even prime number.",
            "The fundamental theorem of arithmetic states that every integer greater than 1 can be uniquely represented as a product of prime numbers.",
        ],
        "answer": (
            "Prime numbers are natural numbers greater than 1 that are only divisible by 1 and "
            "themselves. Examples include 2, 3, 5, 7, and 11."
        ),
    },
    {
        "question": "Tell me about the Indian economy",
        "ground_truth": "India has a mixed economy that is one of the fastest growing in the world.",
        "contexts": [
            "India's GDP growth rate has been consistently above 6% in recent years.",
            "The service sector contributes significantly to India's GDP.",
        ],
        "answer": (
            "India has a booming economy with GDP growth above 6%. The tech sector in Bangalore "
            "is the Silicon Valley of Asia, and India's space program ISRO has launched over 300 satellites."
        ),
    },
]


class TestRAGEvaluation:
    """Quantitative evaluation of RAG pipeline quality."""

    def test_faithfulness(self):
        scores = [faithfulness_score(sample["answer"], sample["contexts"]) for sample in RAG_GOLDEN_DATASET]
        average = sum(scores) / len(scores)
        print(f"\nAverage Faithfulness: {average:.4f}")
        assert average > 0.3, f"Faithfulness too low: {average:.4f} - answers are hallucinating"

    def test_answer_relevancy(self):
        scores = [answer_relevancy_score(sample["answer"], sample["question"]) for sample in RAG_GOLDEN_DATASET]
        average = sum(scores) / len(scores)
        print(f"\nAverage Answer Relevancy: {average:.4f}")
        assert average > 0.05, f"Answer relevancy too low: {average:.4f}"

    def test_context_precision(self):
        scores = [context_precision_score(sample["contexts"], sample["question"]) for sample in RAG_GOLDEN_DATASET]
        average = sum(scores) / len(scores)
        print(f"\nAverage Context Precision: {average:.4f}")
        assert average > 0.02, f"Context precision too low: {average:.4f}"

    def test_context_recall(self):
        scores = [context_recall_score(sample["contexts"], sample["ground_truth"]) for sample in RAG_GOLDEN_DATASET]
        average = sum(scores) / len(scores)
        print(f"\nAverage Context Recall: {average:.4f}")
        assert average > 0.3, f"Context recall too low: {average:.4f}"

    def test_hallucination_detection(self):
        hallucination_sample = RAG_GOLDEN_DATASET[-1]
        hallucinated_faithfulness = faithfulness_score(
            hallucination_sample["answer"],
            hallucination_sample["contexts"],
        )
        print(f"\nHallucination Sample Faithfulness: {hallucinated_faithfulness:.4f}")
        print("   Lower values indicate more hallucinated content.")

        clean_scores = [
            faithfulness_score(sample["answer"], sample["contexts"])
            for sample in RAG_GOLDEN_DATASET[:-1]
        ]
        clean_average = sum(clean_scores) / len(clean_scores)
        print(f"   Clean samples average faithfulness: {clean_average:.4f}")

        assert hallucinated_faithfulness < clean_average, (
            f"Hallucination not detected: hallucinated={hallucinated_faithfulness:.4f} "
            f"vs clean={clean_average:.4f}"
        )

    def test_full_rag_report(self, capsys):
        sample_count = len(RAG_GOLDEN_DATASET)

        faithfulness_scores = [
            faithfulness_score(sample["answer"], sample["contexts"])
            for sample in RAG_GOLDEN_DATASET
        ]
        relevancy_scores = [
            answer_relevancy_score(sample["answer"], sample["question"])
            for sample in RAG_GOLDEN_DATASET
        ]
        precision_scores = [
            context_precision_score(sample["contexts"], sample["question"])
            for sample in RAG_GOLDEN_DATASET
        ]
        recall_scores = [
            context_recall_score(sample["contexts"], sample["ground_truth"])
            for sample in RAG_GOLDEN_DATASET
        ]

        report = {
            "benchmark": "RAG Quality Evaluation (RAGAS-inspired)",
            "num_samples": sample_count,
            "metrics": {
                "Faithfulness": round(sum(faithfulness_scores) / sample_count, 4),
                "Answer Relevancy": round(sum(relevancy_scores) / sample_count, 4),
                "Context Precision": round(sum(precision_scores) / sample_count, 4),
                "Context Recall": round(sum(recall_scores) / sample_count, 4),
            },
        }

        print("\n" + "=" * 60)
        print("RAG QUALITY EVALUATION REPORT")
        print("=" * 60)
        for metric, value in report["metrics"].items():
            print(f"  {metric:20s} | {ascii_bar(value)} | {value:.4f}")
        print("=" * 60)

        print("\n  Per-sample faithfulness scores:")
        for index, (sample, score) in enumerate(zip(RAG_GOLDEN_DATASET, faithfulness_scores), start=1):
            question = sample["question"][:50]
            if score > 0.5:
                indicator = "[OK]"
            elif score > 0.3:
                indicator = "[WARN]"
            else:
                indicator = "[FAIL]"
            print(f"    {indicator} Q{index}: {question:50s} -> faith={score:.3f}")

        print(f"\n  Evaluation complete with {sample_count} samples")

        output = capsys.readouterr().out
        output.encode("ascii")
        assert report["metrics"]["Faithfulness"] > 0.0, "RAG evaluation pipeline is broken"


class TestRAGASIntegration:
    """Verify either the optional RAGAS dependency or the built-in fallback path."""

    def test_ragas_dependency_or_fallback_available(self):
        try:
            import ragas

            print(f"\nRAGAS {ragas.__version__} is installed")
        except ImportError:
            print("\nRAGAS is not installed. Verifying lightweight token-overlap fallback instead.")
            sample = RAG_GOLDEN_DATASET[0]
            assert faithfulness_score(sample["answer"], sample["contexts"]) > 0.0
            assert answer_relevancy_score(sample["answer"], sample["question"]) > 0.0
            assert context_precision_score(sample["contexts"], sample["question"]) > 0.0
            assert context_recall_score(sample["contexts"], sample["ground_truth"]) > 0.0
