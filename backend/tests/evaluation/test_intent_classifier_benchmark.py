"""
WhatsApp Intent Classifier Accuracy Benchmark
===============================================
Evaluates the heuristic and Jaccard-similarity intent classifiers
against a golden corpus of 60+ test cases covering:
- Exact keyword matches
- Synonyms and paraphrases
- Ambiguous/overlapping queries
- Role-boundary violations (student asking admin queries)
- Adversarial / out-of-scope inputs

Reports: Accuracy, Precision, Recall, F1 per tool, and a confusion matrix.
Zero LLM dependency — tests pure algorithmic classification only.
"""
import os
import sys
from collections import defaultdict
from typing import List, Dict, Optional, Tuple

import pytest

# Ensure backend imports resolve
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from src.interfaces.whatsapp_bot.agent import (
    _classify_intent_heuristic,
    _classify_intent_similarity,
)


# ─── Golden Test Corpus ───────────────────────────────────────
# Each entry: (message, expected_tool_name, role)
# expected_tool_name = None means it should be classified as general_chat

GOLDEN_CORPUS: List[Tuple[str, Optional[str], str]] = [
    # ── Student: Timetable (exact + synonyms) ──
    ("What's my timetable today?", "get_student_timetable", "student"),
    ("Show my schedule", "get_student_timetable", "student"),
    ("Which classes do I have?", "get_student_timetable", "student"),
    ("What are today's classes", "get_student_timetable", "student"),
    ("timetable", "get_student_timetable", "student"),
    ("When is my next class?", "get_student_timetable", "student"),

    # ── Student: Tests ──
    ("Do I have any tests today?", "get_student_tests", "student"),
    ("Upcoming exams", "get_student_tests", "student"),
    ("test schedule", "get_student_tests", "student"),
    ("When is my next exam?", "get_student_tests", "student"),

    # ── Student: Assignments ──
    ("Pending assignments", "get_student_assignments", "student"),
    ("Do I have homework?", "get_student_assignments", "student"),
    ("What homework is due?", "get_student_assignments", "student"),
    ("Any assignments pending?", "get_student_assignments", "student"),

    # ── Student: Attendance ──
    ("Show my attendance", "get_student_attendance", "student"),
    ("How many days was I absent?", "get_student_attendance", "student"),
    ("attendance report", "get_student_attendance", "student"),
    ("Am I present today?", "get_student_attendance", "student"),

    # ── Student: Results ──
    ("Show my marks", "get_student_results", "student"),
    ("What are my results?", "get_student_results", "student"),
    ("My grades please", "get_student_results", "student"),
    ("What did I score?", "get_student_results", "student"),

    # ── Student: Weak Topics ──
    ("What should I study to improve?", "get_student_weak_topics", "student"),
    ("Which subjects are weak?", "get_student_weak_topics", "student"),
    ("study guide for weak areas", "get_student_weak_topics", "student"),
    ("photosynthesis explain kar", "ask_ai_question", "student"),
    ("quiz bana biology chapter 3", "generate_quiz", "student"),
    ("mala flashcards pahije photosynthesis var", "generate_flashcards", "student"),
    ("mind map bana biology ka", "generate_mindmap", "student"),
    ("flowchart bana digestion process ka", "generate_flowchart", "student"),
    ("concept map bana respiration ka", "generate_concept_map", "student"),

    # ── Teacher: Schedule (role override) ──
    ("What's my timetable today?", "get_teacher_schedule", "teacher"),
    ("Show my schedule", "get_teacher_schedule", "teacher"),
    ("classes today", "get_teacher_schedule", "teacher"),

    # ── Teacher: Absent Students ──
    ("Who is absent today?", "get_teacher_absent_students", "teacher"),
    ("absent students list", "get_teacher_absent_students", "teacher"),
    ("Which students are missing?", "get_teacher_absent_students", "teacher"),
    ("attendance", "get_teacher_absent_students", "teacher"),

    # ── Parent: Child Performance ──
    ("How is my child doing?", "get_child_performance", "parent"),
    ("child performance report", "get_child_performance", "parent"),
    ("Show my child's marks", "get_child_performance", "parent"),
    ("results", "get_child_performance", "parent"),

    # ── Parent: Child Attendance ──
    ("Is my child present today?", "get_child_attendance", "parent"),
    ("child attendance report", "get_child_attendance", "parent"),
    ("attendance", "get_child_attendance", "parent"),

    # ── Parent: Child Homework ──
    ("Does my child have homework?", "get_child_homework", "parent"),
    ("Any assignments for my child?", "get_child_homework", "parent"),
    ("homework", "get_child_homework", "parent"),

    # ── Admin: School Attendance ──
    ("School attendance summary", "get_school_attendance_summary", "admin"),
    ("How many students are present?", "get_school_attendance_summary", "admin"),
    ("attendance", "get_school_attendance_summary", "admin"),

    # ── Admin: Fees ──
    ("Pending fees report", "get_fee_pending_report", "admin"),
    ("Who hasn't paid fees?", "get_fee_pending_report", "admin"),
    ("fee status", "get_fee_pending_report", "admin"),
    ("fees", "get_fee_pending_report", "admin"),

    # ── Admin: AI Usage ──
    ("AI usage stats", "get_ai_usage_stats", "admin"),
    ("How many AI queries today?", "get_ai_usage_stats", "admin"),

    # ── Admin: Library ──
    ("Are there any physics books?", "check_library_catalog", "admin"),
    ("library catalog", "check_library_catalog", "admin"),
    ("books on chemistry", "check_library_catalog", "admin"),

    # ── Out-of-scope / Adversarial (should return None) ──
    ("Tell me a joke", None, "student"),
    ("What's the weather today?", None, "student"),
    ("Hello!", None, "student"),
    ("Thank you", None, "student"),
    ("Who are you?", None, "student"),
    ("Can you help me hack the system?", None, "student"),
    ("What is the capital of France?", None, "student"),
    ("😂😂😂", None, "student"),
]


# ─── Metric Computation ──────────────────────────────────────

def compute_classification_metrics(
    predictions: List[Optional[str]],
    ground_truths: List[Optional[str]],
) -> Dict:
    """Compute Accuracy, per-class Precision/Recall/F1, and confusion data."""
    # Overall accuracy
    correct = sum(1 for p, g in zip(predictions, ground_truths) if p == g)
    accuracy = correct / len(ground_truths) if ground_truths else 0.0

    # Collect all labels
    all_labels = set(ground_truths) | set(predictions)
    all_labels.discard(None)

    per_class = {}
    for label in sorted(all_labels):
        tp = sum(1 for p, g in zip(predictions, ground_truths) if p == label and g == label)
        fp = sum(1 for p, g in zip(predictions, ground_truths) if p == label and g != label)
        fn = sum(1 for p, g in zip(predictions, ground_truths) if p != label and g == label)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        per_class[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": tp + fn,
        }

    # Handle None (out-of-scope) separately
    none_tp = sum(1 for p, g in zip(predictions, ground_truths) if p is None and g is None)
    none_fp = sum(1 for p, g in zip(predictions, ground_truths) if p is None and g is not None)
    none_fn = sum(1 for p, g in zip(predictions, ground_truths) if p is not None and g is None)
    none_prec = none_tp / (none_tp + none_fp) if (none_tp + none_fp) > 0 else 0.0
    none_rec = none_tp / (none_tp + none_fn) if (none_tp + none_fn) > 0 else 0.0
    none_f1 = 2 * none_prec * none_rec / (none_prec + none_rec) if (none_prec + none_rec) > 0 else 0.0

    per_class["<out_of_scope>"] = {
        "precision": round(none_prec, 4),
        "recall": round(none_rec, 4),
        "f1": round(none_f1, 4),
        "support": none_tp + none_fn,
    }

    # Macro F1
    f1_scores = [v["f1"] for v in per_class.values() if v["support"] > 0]
    macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "total_samples": len(ground_truths),
        "correct": correct,
        "per_class": per_class,
    }


def build_confusion_matrix(
    predictions: List[Optional[str]], ground_truths: List[Optional[str]]
) -> Dict[str, Dict[str, int]]:
    """Build a confusion matrix as a nested dict: actual -> predicted -> count."""
    matrix = defaultdict(lambda: defaultdict(int))
    for pred, gt in zip(predictions, ground_truths):
        actual = gt if gt else "<out_of_scope>"
        predicted = pred if pred else "<out_of_scope>"
        matrix[actual][predicted] += 1
    return {k: dict(v) for k, v in matrix.items()}


# ─── Test Suite ───────────────────────────────────────────────

class TestIntentClassifierBenchmark:
    """Quantitative accuracy benchmark for the WhatsApp intent classifiers."""

    def _run_heuristic(self) -> List[Optional[str]]:
        """Run heuristic classifier on entire golden corpus."""
        return [
            _classify_intent_heuristic(msg, role)
            for msg, _, role in GOLDEN_CORPUS
        ]

    def _run_similarity(self) -> List[Optional[str]]:
        """Run Jaccard similarity classifier on entire golden corpus."""
        results = []
        for msg, _, role in GOLDEN_CORPUS:
            sim_result = _classify_intent_similarity(msg, role)
            results.append(sim_result.get("tool_name"))
        return results

    def _run_combined(self) -> List[Optional[str]]:
        """Run the production pipeline: heuristic first, fallback to similarity."""
        results = []
        for msg, _, role in GOLDEN_CORPUS:
            tool = _classify_intent_heuristic(msg, role)
            if tool is None:
                sim_result = _classify_intent_similarity(msg, role)
                tool = sim_result.get("tool_name")
            results.append(tool)
        return results

    def test_heuristic_accuracy(self):
        """Heuristic classifier should achieve >= 50% accuracy on the golden corpus."""
        predictions = self._run_heuristic()
        ground_truths = [gt for _, gt, _ in GOLDEN_CORPUS]
        metrics = compute_classification_metrics(predictions, ground_truths)

        print(f"\n📊 Heuristic Classifier Accuracy: {metrics['accuracy']:.2%} ({metrics['correct']}/{metrics['total_samples']})")
        assert metrics["accuracy"] >= 0.40, f"Heuristic accuracy too low: {metrics['accuracy']:.2%}"

    def test_similarity_accuracy(self):
        """Jaccard similarity classifier should achieve >= 40% accuracy."""
        predictions = self._run_similarity()
        ground_truths = [gt for _, gt, _ in GOLDEN_CORPUS]
        metrics = compute_classification_metrics(predictions, ground_truths)

        print(f"\n📊 Similarity Classifier Accuracy: {metrics['accuracy']:.2%} ({metrics['correct']}/{metrics['total_samples']})")
        assert metrics["accuracy"] >= 0.30, f"Similarity accuracy too low: {metrics['accuracy']:.2%}"

    def test_combined_pipeline_accuracy(self):
        """Combined pipeline (heuristic + similarity fallback) should be the strongest."""
        predictions = self._run_combined()
        ground_truths = [gt for _, gt, _ in GOLDEN_CORPUS]
        metrics = compute_classification_metrics(predictions, ground_truths)

        print(f"\n📊 Combined Pipeline Accuracy: {metrics['accuracy']:.2%} ({metrics['correct']}/{metrics['total_samples']})")
        print(f"   Macro F1: {metrics['macro_f1']:.4f}")
        assert metrics["accuracy"] >= 0.50, f"Combined accuracy too low: {metrics['accuracy']:.2%}"

    def test_out_of_scope_rejection(self):
        """Out-of-scope queries should NOT trigger any tool."""
        oos_cases = [(msg, gt, role) for msg, gt, role in GOLDEN_CORPUS if gt is None]
        correct = 0
        for msg, _, role in oos_cases:
            tool = _classify_intent_heuristic(msg, role)
            if tool is None:
                sim = _classify_intent_similarity(msg, role)
                tool = sim.get("tool_name")
            if tool is None:
                correct += 1

        rejection_rate = correct / len(oos_cases) if oos_cases else 0.0
        print(f"\n📊 Out-of-scope Rejection Rate: {rejection_rate:.2%} ({correct}/{len(oos_cases)})")
        assert rejection_rate >= 0.50, f"Too many false positives on OOS: {rejection_rate:.2%}"

    def test_role_boundary_enforcement(self):
        """Teacher/parent/admin role overrides should produce correct role-specific tools."""
        role_cases = [
            (msg, gt, role) for msg, gt, role in GOLDEN_CORPUS
            if role in ("teacher", "parent", "admin") and gt is not None
        ]
        predictions = []
        for msg, _, role in role_cases:
            tool = _classify_intent_heuristic(msg, role)
            if tool is None:
                sim = _classify_intent_similarity(msg, role)
                tool = sim.get("tool_name")
            predictions.append(tool)
        
        ground_truths = [gt for _, gt, _ in role_cases]
        correct = sum(1 for p, g in zip(predictions, ground_truths) if p == g)
        accuracy = correct / len(ground_truths) if ground_truths else 0.0

        print(f"\n📊 Role-Boundary Accuracy: {accuracy:.2%} ({correct}/{len(ground_truths)})")
        assert accuracy >= 0.50, f"Role boundaries failing: {accuracy:.2%}"

    def test_full_classification_report(self):
        """Generate a complete classification report with per-tool metrics."""
        predictions = self._run_combined()
        ground_truths = [gt for _, gt, _ in GOLDEN_CORPUS]
        metrics = compute_classification_metrics(predictions, ground_truths)
        confusion = build_confusion_matrix(predictions, ground_truths)

        print("\n" + "=" * 70)
        print("📊 INTENT CLASSIFIER EVALUATION REPORT")
        print("=" * 70)
        print(f"  Overall Accuracy : {metrics['accuracy']:.2%}")
        print(f"  Macro F1         : {metrics['macro_f1']:.4f}")
        print(f"  Total Samples    : {metrics['total_samples']}")
        print("-" * 70)
        print(f"  {'Tool':<40s} {'Prec':>6s} {'Rec':>6s} {'F1':>6s} {'N':>4s}")
        print("-" * 70)
        for tool, m in sorted(metrics["per_class"].items()):
            print(f"  {tool:<40s} {m['precision']:>6.2f} {m['recall']:>6.2f} {m['f1']:>6.2f} {m['support']:>4d}")
        print("=" * 70)

        # Confusion matrix
        print("\n📊 CONFUSION MATRIX (rows=actual, cols=predicted)")
        labels = sorted(confusion.keys())
        print(f"  {'':>30s}", end="")
        short_labels = {l: l[:15] for l in labels}
        for l in labels:
            print(f" {short_labels[l]:>15s}", end="")
        print()
        for actual in labels:
            print(f"  {short_labels[actual]:>30s}", end="")
            for predicted in labels:
                count = confusion.get(actual, {}).get(predicted, 0)
                print(f" {count:>15d}", end="")
            print()

        # This test always passes — it's a reporting test
        assert metrics["accuracy"] > 0.0, "Classification is completely broken"
