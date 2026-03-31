"""
Deterministic personalization quality benchmark.

This gate verifies that the personalization layer adapts across three learner
states: support, balanced, and advanced. It exercises recommendation ranking,
adaptive quiz difficulty, prompt shaping, and study-path generation without
calling external model providers.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import pytest

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from src.domains.academic.models.core import Class, Subject
from src.domains.academic.models.performance import SubjectPerformance
from src.domains.identity.models.user import User
from src.domains.platform.models.topic_mastery import TopicMastery
from src.domains.platform.services.mastery_tracking_service import (
    build_adaptive_quiz_profile,
    build_profile_aware_recommendations,
)
from src.domains.platform.services.study_path_service import get_or_create_study_path
from src.interfaces.rest_api.ai.workflows import _apply_personalization_context


SCENARIOS = [
    {
        "label": "support",
        "average_score": 38.0,
        "mastery_score": 41.0,
        "confidence_score": 0.32,
        "learner_profile": {
            "preferred_language": "english",
            "preferred_response_length": "brief",
            "inferred_expertise_level": "simple",
            "primary_subjects": ["Biology"],
        },
    },
    {
        "label": "balanced",
        "average_score": 66.0,
        "mastery_score": 63.0,
        "confidence_score": 0.52,
        "learner_profile": {
            "preferred_language": "english",
            "preferred_response_length": "default",
            "inferred_expertise_level": "standard",
            "primary_subjects": ["Biology"],
        },
    },
    {
        "label": "advanced",
        "average_score": 88.0,
        "mastery_score": 84.0,
        "confidence_score": 0.78,
        "learner_profile": {
            "preferred_language": "english",
            "preferred_response_length": "detailed",
            "inferred_expertise_level": "advanced",
            "primary_subjects": ["Biology"],
        },
    },
]

PASS_RATE_THRESHOLD = 1.0


def _create_student_fixture(db_session, tenant_id, *, label: str) -> tuple[User, Subject]:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=f"personalization-{label}-{suffix}@testschool.edu",
        full_name=f"Personalization {label.title()} Learner",
        role="student",
        is_active=True,
    )
    school_class = Class(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name=f"Benchmark Class {label.title()} {suffix}",
        grade_level="10",
    )
    subject = Subject(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        class_id=school_class.id,
        name="Biology",
    )
    db_session.add_all([user, school_class, subject])
    db_session.flush()
    return user, subject


def _run_personalization_scenario(db_session, active_tenant, scenario: dict[str, Any]) -> dict[str, Any]:
    user, subject = _create_student_fixture(
        db_session,
        active_tenant.id,
        label=str(scenario["label"]),
    )
    db_session.add_all(
        [
            SubjectPerformance(
                tenant_id=active_tenant.id,
                student_id=user.id,
                subject_id=subject.id,
                average_score=float(scenario["average_score"]),
                attendance_rate=91.0,
            ),
            TopicMastery(
                tenant_id=active_tenant.id,
                user_id=user.id,
                subject_id=subject.id,
                topic="Photosynthesis",
                concept="core",
                mastery_score=float(scenario["mastery_score"]),
                confidence_score=float(scenario["confidence_score"]),
                last_evidence_type="quiz_completed",
            ),
        ]
    )
    db_session.commit()

    learner_profile = dict(scenario["learner_profile"])
    recommendations = build_profile_aware_recommendations(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        active_tool="qa",
        current_surface="ai_studio",
        current_topic="Photosynthesis",
        learner_profile=learner_profile,
        limit=4,
    )
    quiz_profile = build_adaptive_quiz_profile(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        topic="Photosynthesis",
        subject_id=subject.id,
    )
    topic_context = {
        "topic": "Photosynthesis",
        "mastery_score": scenario["mastery_score"],
        "confidence_score": scenario["confidence_score"],
        "focus_concepts": ["chlorophyll", "light reaction"],
        "repeated_confusion_count": 2 if scenario["label"] == "support" else 0,
    }
    qa_prompt = _apply_personalization_context(
        "Answer with citations:",
        learner_profile=learner_profile,
        learner_topic_context=topic_context,
        mode="qa",
    )
    study_guide_prompt = _apply_personalization_context(
        "Study Guide:",
        learner_profile=learner_profile,
        learner_topic_context=topic_context,
        mode="study_guide",
    )
    plan = get_or_create_study_path(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        topic="Photosynthesis",
        subject_id=subject.id,
        current_surface="ai_studio",
        force_refresh=True,
    )

    recommendation_targets = {item.get("target_tool") for item in recommendations}
    checks = {
        "recommendation_alignment": False,
        "quiz_alignment": False,
        "qa_prompt_alignment": False,
        "study_guide_alignment": False,
        "study_path_alignment": False,
    }

    if scenario["label"] == "support":
        checks["recommendation_alignment"] = bool(recommendation_targets.intersection({"study_guide", "quiz", "flashcards"}))
        checks["quiz_alignment"] = quiz_profile["label"] == "support"
        checks["qa_prompt_alignment"] = "learner expertise: simple" in qa_prompt and "preferred response length: brief" in qa_prompt
        checks["study_guide_alignment"] = (
            "organize the study guide as basics first" in study_guide_prompt
            and "scaffold the explanation step by step" in study_guide_prompt
        )
    elif scenario["label"] == "balanced":
        checks["recommendation_alignment"] = bool(recommendation_targets.intersection({"quiz", "flashcards", "study_guide"}))
        checks["quiz_alignment"] = quiz_profile["label"] == "balanced"
        checks["qa_prompt_alignment"] = "learner expertise: standard" in qa_prompt
        checks["study_guide_alignment"] = "Adaptive guidance:" not in study_guide_prompt
    else:
        checks["recommendation_alignment"] = bool(recommendation_targets.intersection({"debate", "concept_map"}))
        checks["quiz_alignment"] = quiz_profile["label"] == "challenge"
        checks["qa_prompt_alignment"] = "learner expertise: advanced" in qa_prompt and "preferred response length: detailed" in qa_prompt
        checks["study_guide_alignment"] = (
            "start with a concise summary" in study_guide_prompt
            and "higher-order connections" in study_guide_prompt
        )

    checks["study_path_alignment"] = (
        plan["next_action"]["id"] == "guide"
        and [item["id"] for item in plan["items"]] == ["guide", "flashcards", "quiz", "recheck"]
    )

    pass_rate = round(sum(1 for passed in checks.values() if passed) / len(checks), 2)
    return {
        "label": scenario["label"],
        "recommendation_targets": sorted(target for target in recommendation_targets if target),
        "quiz_label": quiz_profile["label"],
        "checks": checks,
        "pass_rate": pass_rate,
    }


def _run_personalization_benchmark(db_session, active_tenant) -> dict[str, Any]:
    scenarios = [_run_personalization_scenario(db_session, active_tenant, scenario) for scenario in SCENARIOS]
    overall_pass_rate = round(sum(item["pass_rate"] for item in scenarios) / len(scenarios), 2)
    return {
        "benchmark": "personalization_adaptation",
        "scenarios": scenarios,
        "overall_pass_rate": overall_pass_rate,
        "thresholds": {
            "scenario_pass_rate": PASS_RATE_THRESHOLD,
            "overall_pass_rate": PASS_RATE_THRESHOLD,
        },
    }


def test_personalization_benchmark_gate(db_session, active_tenant):
    report = _run_personalization_benchmark(db_session, active_tenant)

    assert report["overall_pass_rate"] >= PASS_RATE_THRESHOLD
    for scenario in report["scenarios"]:
        assert scenario["pass_rate"] >= PASS_RATE_THRESHOLD, (
            f"{scenario['label']} personalization scenario failed: {scenario['checks']}"
        )


def test_personalization_benchmark_report(db_session, active_tenant, tmp_path, capsys):
    report = _run_personalization_benchmark(db_session, active_tenant)
    report_path = Path(tmp_path) / "personalization_benchmark_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\nPERSONALIZATION BENCHMARK REPORT")
    for scenario in report["scenarios"]:
        print(
            f"- {scenario['label']}: pass_rate={scenario['pass_rate']:.2f}, "
            f"quiz={scenario['quiz_label']}, targets={','.join(scenario['recommendation_targets'])}"
        )
    print(f"overall_pass_rate={report['overall_pass_rate']:.2f}")
    print(f"report_path={report_path}")

    output = capsys.readouterr().out
    output.encode("ascii")

    assert report_path.exists()
    assert report["overall_pass_rate"] >= PASS_RATE_THRESHOLD
