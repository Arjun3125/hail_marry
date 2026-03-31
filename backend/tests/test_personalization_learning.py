import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from src.domains.academic.models.core import Class, Subject
from src.domains.academic.models.performance import SubjectPerformance
from src.domains.identity.models.user import User
from src.domains.identity.routes.auth import pwd_context
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.generated_content import GeneratedContent
from src.domains.platform.models.learner_profile import LearnerProfile
from src.domains.platform.models.study_path_plan import StudyPathPlan
from src.domains.platform.models.study_session import StudySession
from src.domains.platform.models.topic_mastery import TopicMastery
from src.domains.platform.services.learner_profile_service import recompute_learner_profile
from src.domains.platform.services.mastery_tracking_service import (
    build_adaptive_quiz_profile,
    count_recent_confusion_queries,
    ensure_topic_mastery_seed,
    extract_concepts,
    infer_topic_from_query,
    record_ai_confusion_pattern,
    record_quiz_completion,
    record_review_completion,
)
from src.interfaces.rest_api.ai.workflows import _apply_personalization_context
from src.domains.platform.services.metrics_registry import reset_metrics_registry
from src.shared.ai_tools.study_tools import _build_adaptive_tool_topic, execute_study_tool
from src.domains.platform.schemas.ai_runtime import InternalStudyToolGenerateRequest


def _create_user_and_login(client, db_session, tenant_id, email: str, *, role: str = "student"):
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name="Personalization Tester",
        role=role,
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "pass123!"},
    )
    token = response.json().get("access_token")
    assert token
    return user, token


def _create_student_and_login(client, db_session, tenant_id, email: str):
    return _create_user_and_login(client, db_session, tenant_id, email, role="student")


def test_extract_concepts_returns_compact_learning_units():
    concepts = extract_concepts("Photosynthesis in green plants and chloroplast energy transfer")
    assert "photosynthesis" in concepts
    assert "chloroplast" in concepts or "energy" in concepts


def test_record_review_completion_updates_topic_mastery(db_session, active_tenant):
    user = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="mastery-review@testschool.edu",
        role="student",
    )
    db_session.add(user)
    db_session.commit()

    seed_rows = ensure_topic_mastery_seed(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        topic="Cell division basics",
    )
    before_score = seed_rows[0].mastery_score
    before_confidence = seed_rows[0].confidence_score

    record_review_completion(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        topic="Cell division basics",
        rating=5,
        next_review_at=datetime.now(timezone.utc) + timedelta(days=6),
    )
    db_session.commit()

    row = (
        db_session.query(TopicMastery)
        .filter(
            TopicMastery.tenant_id == active_tenant.id,
            TopicMastery.user_id == user.id,
            TopicMastery.topic == "Cell division basics",
            TopicMastery.concept == "core",
        )
        .first()
    )
    assert row is not None
    assert row.mastery_score > before_score
    assert row.confidence_score > before_confidence
    assert row.last_evidence_type == "review_completed"


def test_record_quiz_completion_updates_mastery_from_accuracy(db_session, active_tenant):
    user = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="mastery-quiz@testschool.edu",
        role="student",
    )
    db_session.add(user)
    db_session.commit()

    seed_rows = ensure_topic_mastery_seed(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        topic="Chemical bonding",
    )
    before_score = seed_rows[0].mastery_score

    record_quiz_completion(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        topic="Chemical bonding",
        total_questions=5,
        correct_answers=4,
        difficulty_breakdown={"easy": 2, "medium": 2, "hard": 1},
    )
    db_session.commit()

    row = (
        db_session.query(TopicMastery)
        .filter(
            TopicMastery.tenant_id == active_tenant.id,
            TopicMastery.user_id == user.id,
            TopicMastery.topic == "Chemical bonding",
            TopicMastery.concept == "core",
        )
        .first()
    )
    assert row is not None
    assert row.mastery_score > before_score
    assert row.last_evidence_type == "quiz_completed"


def test_build_adaptive_quiz_profile_supports_struggling_learner(db_session, active_tenant):
    user = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="adaptive-quiz@testschool.edu",
        role="student",
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 10", grade_level="10")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, name="Biology")
    db_session.add_all([user, school_class, subject])
    db_session.commit()

    db_session.add(
        SubjectPerformance(
            tenant_id=active_tenant.id,
            student_id=user.id,
            subject_id=subject.id,
            average_score=34.0,
            attendance_rate=85.0,
        )
    )
    db_session.commit()

    profile = build_adaptive_quiz_profile(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        topic="Photosynthesis",
        subject_id=subject.id,
    )

    assert profile["label"] == "support"
    assert profile["difficulty_mix"] == {"easy": 3, "medium": 2, "hard": 0}
    assert "required difficulty mix" in profile["prompt_suffix"]


def test_apply_personalization_context_adds_learner_and_topic_guidance():
    prompt = _apply_personalization_context(
        "Answer with citations:",
        learner_profile={
            "inferred_expertise_level": "simple",
            "preferred_response_length": "brief",
            "preferred_language": "hindi",
            "primary_subjects": ["Biology"],
        },
        learner_topic_context={
            "topic": "Photosynthesis",
            "mastery_score": 38.0,
            "confidence_score": 0.31,
            "focus_concepts": ["chlorophyll", "sunlight"],
            "repeated_confusion_count": 3,
        },
        mode="qa",
    )

    assert prompt.startswith("Personalization context:")
    assert "learner expertise: simple" in prompt
    assert "preferred response length: brief" in prompt
    assert "preferred language: hindi" in prompt
    assert "primary subjects: Biology" in prompt
    assert "current topic: Photosynthesis" in prompt
    assert "current mastery score: 38.0" in prompt
    assert "focus concepts: chlorophyll, sunlight" in prompt
    assert "repeated confusion count on topic: 3" in prompt
    assert "do not override explicit user instructions" in prompt


def test_apply_personalization_context_reorders_study_guides_for_struggling_learners():
    prompt = _apply_personalization_context(
        "Study Guide:",
        learner_profile={
            "inferred_expertise_level": "simple",
            "preferred_response_length": "brief",
        },
        learner_topic_context={
            "topic": "Photosynthesis",
            "mastery_score": 41.0,
            "confidence_score": 0.35,
            "repeated_confusion_count": 2,
        },
        mode="study_guide",
    )

    assert "Adaptive guidance:" in prompt
    assert "organize the study guide as basics first" in prompt
    assert "define key terms before deeper explanation" in prompt
    assert "scaffold the explanation step by step" in prompt


def test_apply_personalization_context_deepens_study_guides_for_advanced_learners():
    prompt = _apply_personalization_context(
        "Study Guide:",
        learner_profile={
            "inferred_expertise_level": "advanced",
            "preferred_response_length": "detailed",
        },
        learner_topic_context={
            "topic": "Photosynthesis",
            "mastery_score": 88.0,
            "confidence_score": 0.8,
            "repeated_confusion_count": 0,
        },
        mode="study_guide",
    )

    assert "Adaptive guidance:" in prompt
    assert "start with a concise summary" in prompt
    assert "higher-order connections" in prompt


def test_build_adaptive_tool_topic_prioritizes_flashcard_focus_concepts():
    topic = _build_adaptive_tool_topic(
        InternalStudyToolGenerateRequest(
            tool="flashcards",
            topic="Photosynthesis",
            tenant_id="tenant-1",
            user_id="user-1",
            learner_profile={
                "inferred_expertise_level": "simple",
                "preferred_response_length": "brief",
            },
            learner_topic_context={
                "mastery_score": 42.0,
                "focus_concepts": ["chlorophyll", "light reactions"],
                "repeated_confusion_count": 2,
            },
        )
    )

    assert "Adaptive generation guidance" in topic
    assert "Prioritize the weakest or most confusing concepts first" in topic
    assert "chlorophyll, light reactions" in topic
    assert "misconception-correction" in topic
    assert "especially concise" in topic


def test_build_adaptive_tool_topic_simplifies_visual_tools_for_struggling_learners():
    topic = _build_adaptive_tool_topic(
        InternalStudyToolGenerateRequest(
            tool="mindmap",
            topic="Cell division",
            tenant_id="tenant-1",
            learner_profile={"inferred_expertise_level": "simple"},
            learner_topic_context={"mastery_score": 35.0, "repeated_confusion_count": 1},
        )
    )

    assert "Adaptive generation guidance" in topic
    assert "Prefer a simpler structure" in topic


def test_execute_study_tool_passes_personalization_context_to_ai_query(monkeypatch):
    import src.shared.ai_tools.study_tools as study_tools_module

    captured = {}

    async def fake_execute_text_query(request):
        captured["query"] = request.query
        captured["learner_profile"] = request.learner_profile
        captured["learner_topic_context"] = request.learner_topic_context
        return {
            "answer": '[{"front":"Chlorophyll","back":"Captures light energy.","citation":"[bio_p1]"}]',
            "citations": [],
            "token_usage": 7,
            "citation_valid": True,
        }

    monkeypatch.setattr(study_tools_module, "execute_text_query", fake_execute_text_query)

    result = asyncio.run(
        execute_study_tool(
            InternalStudyToolGenerateRequest(
                tool="flashcards",
                topic="Photosynthesis",
                tenant_id="tenant-1",
                user_id="user-1",
                learner_profile={"inferred_expertise_level": "simple"},
                learner_topic_context={
                    "topic": "Photosynthesis",
                    "mastery_score": 41.0,
                    "focus_concepts": ["chlorophyll"],
                    "repeated_confusion_count": 2,
                },
            )
        )
    )

    assert "Adaptive generation guidance" in captured["query"]
    assert captured["learner_profile"]["inferred_expertise_level"] == "simple"
    assert captured["learner_topic_context"]["focus_concepts"] == ["chlorophyll"]
    assert result["data"][0]["front"] == "Chlorophyll"


def test_recompute_learner_profile_infers_preferences_and_metrics(db_session, active_tenant):
    user = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="profile-inference@testschool.edu",
        role="student",
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 11", grade_level="11")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, name="Biology")
    db_session.add_all([user, school_class, subject])
    db_session.commit()

    db_session.add_all(
        [
            AIQuery(
                tenant_id=active_tenant.id,
                user_id=user.id,
                query_text="Explain photosynthesis briefly in simple terms",
                mode="qa",
                response_text="answer",
            ),
            AIQuery(
                tenant_id=active_tenant.id,
                user_id=user.id,
                query_text="Give me a short summary of chlorophyll",
                mode="study_guide",
                response_text="answer",
            ),
            StudySession(
                tenant_id=active_tenant.id,
                user_id=user.id,
                topic="Photosynthesis",
                duration_seconds=1800,
                questions_answered=6,
            ),
            GeneratedContent(
                tenant_id=active_tenant.id,
                user_id=user.id,
                notebook_id=uuid.uuid4(),
                type="flashcards",
                title="Bio Cards",
                content={"cards": []},
            ),
            SubjectPerformance(
                tenant_id=active_tenant.id,
                student_id=user.id,
                subject_id=subject.id,
                average_score=44.0,
                attendance_rate=90.0,
            ),
        ]
    )
    db_session.commit()

    profile = recompute_learner_profile(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
    )
    db_session.commit()

    assert profile.preferred_response_length == "brief"
    assert profile.inferred_expertise_level == "simple"
    assert "Biology" in (profile.primary_subjects or [])
    assert profile.engagement_score > 0
    assert profile.signal_summary["recent_query_count"] == 2


def test_personalization_recommendations_prioritize_weak_topics(client, db_session, active_tenant):
    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "recommendations@testschool.edu",
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 9", grade_level="9")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, name="Physics")
    db_session.add_all([school_class, subject])
    db_session.commit()

    db_session.add(
        SubjectPerformance(
            tenant_id=active_tenant.id,
            student_id=user.id,
            subject_id=subject.id,
            average_score=41.0,
            attendance_rate=90.0,
        )
    )
    db_session.commit()

    response = client.get(
        "/api/personalization/recommendations?active_tool=qa&current_surface=ai_studio",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"]
    assert any(item["reason"] in {"weak_topic", "mastery_gap"} for item in payload["items"])
    assert any("Physics" in item["label"] or "Physics" in item["prompt"] for item in payload["items"])
    assert payload["learner_profile"]["inferred_expertise_level"] in {"simple", "standard", "advanced"}


def test_personalization_profile_endpoint_returns_persisted_profile(client, db_session, active_tenant):
    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "profile-endpoint@testschool.edu",
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 7", grade_level="7")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, name="Maths")
    db_session.add_all([school_class, subject])
    db_session.commit()
    db_session.add(
        SubjectPerformance(
            tenant_id=active_tenant.id,
            student_id=user.id,
            subject_id=subject.id,
            average_score=81.0,
            attendance_rate=96.0,
        )
    )
    db_session.commit()

    response = client.post(
        "/api/personalization/profile/recompute",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()["profile"]
    assert payload["inferred_expertise_level"] in {"standard", "advanced"}

    row = (
        db_session.query(LearnerProfile)
        .filter(
            LearnerProfile.tenant_id == active_tenant.id,
            LearnerProfile.user_id == user.id,
        )
        .first()
    )
    assert row is not None
    assert row.last_recomputed_at is not None


def test_student_quiz_result_submission_updates_mastery(client, db_session, active_tenant):
    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "quiz-results@testschool.edu",
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 6", grade_level="6")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, name="Science")
    db_session.add_all([school_class, subject])
    db_session.commit()

    response = client.post(
        "/api/student/tools/quiz-results",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "topic": "Respiration",
            "subject_id": str(subject.id),
            "total_questions": 5,
            "correct_answers": 4,
            "difficulty_breakdown": {"easy": 2, "medium": 2, "hard": 1},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["mastery"]["mastery_score"] > 55


def test_guided_quiz_completion_emits_improvement_metrics(client, db_session, active_tenant):
    reset_metrics_registry()
    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "guided-improvement@testschool.edu",
    )
    admin_user = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="guided-improvement-admin@testschool.edu",
        full_name="Guided Improvement Admin",
        role="admin",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    db_session.add(admin_user)
    db_session.add(
        TopicMastery(
            tenant_id=active_tenant.id,
            user_id=user.id,
            topic="Photosynthesis",
            concept="core",
            mastery_score=48.0,
            confidence_score=0.38,
            last_evidence_type="quiz_completed",
        )
    )
    db_session.commit()

    plan_response = client.get(
        "/api/personalization/study-path?topic=Photosynthesis&current_surface=overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert plan_response.status_code == 200
    plan = plan_response.json()["plan"]

    step_response = client.post(
        f"/api/personalization/study-path/{plan['id']}/steps/guide/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert step_response.status_code == 200

    quiz_response = client.post(
        "/api/student/tools/quiz-results",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "topic": "Photosynthesis",
            "total_questions": 5,
            "correct_answers": 5,
            "difficulty_breakdown": {"easy": 2, "medium": 2, "hard": 1},
        },
    )
    assert quiz_response.status_code == 200
    assert quiz_response.json()["mastery"]["mastery_score"] >= 60

    admin_login = client.post(
        "/api/auth/login",
        json={"email": "guided-improvement-admin@testschool.edu", "password": "pass123!"},
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]

    metrics_response = client.get(
        "/api/personalization/metrics",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert metrics_response.status_code == 200
    summary = metrics_response.json()["summary"]
    assert summary["mastery_improved_total"] >= 1
    assert summary["mastery_recovered_total"] >= 1
    assert summary["guided_mastery_improved_total"] >= 1
    assert summary["guided_mastery_recovered_total"] >= 1
    assert summary["guided_improvement_rate_pct"] > 0

    reset_metrics_registry()


def test_student_weak_topics_includes_mastery_topics(client, db_session, active_tenant):
    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "weak-mastery@testschool.edu",
    )
    ensure_topic_mastery_seed(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        topic="Photosynthesis",
    )
    record_ai_confusion_pattern(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        query="Explain photosynthesis",
        repeated_count=3,
    )
    db_session.commit()

    response = client.get(
        "/api/student/weak-topics",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mastery_topics"]
    assert payload["mastery_topics"][0]["topic"] == "Photosynthesis"


def test_ai_query_repetition_updates_confusion_mastery(client, db_session, active_tenant, monkeypatch):
    import src.interfaces.rest_api.ai.routes.ai as ai_routes

    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "confusion-ai@testschool.edu",
    )

    async def fake_prepare_ai_query(**kwargs):
        return kwargs["query"], [], kwargs["query"], ""

    async def fake_run_text_query(request, trace_id=None):
        return {
            "answer": "Photosynthesis converts light into chemical energy.",
            "citations": [],
            "token_usage": 5,
            "mode": "qa",
            "has_context": True,
            "citation_valid": True,
            "citation_count": 0,
        }

    monkeypatch.setattr(ai_routes, "_prepare_ai_query", fake_prepare_ai_query)
    monkeypatch.setattr(ai_routes, "run_text_query", fake_run_text_query)

    for _ in range(2):
        response = client.post(
            "/api/ai/query",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": "Explain photosynthesis", "mode": "qa"},
        )
        assert response.status_code == 200

    repeat_count = count_recent_confusion_queries(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        topic="Explain photosynthesis",
    )
    assert repeat_count >= 2

    row = (
        db_session.query(TopicMastery)
        .filter(
            TopicMastery.tenant_id == active_tenant.id,
            TopicMastery.user_id == user.id,
            TopicMastery.topic == infer_topic_from_query("Explain photosynthesis"),
            TopicMastery.concept == "core",
        )
        .first()
    )
    assert row is not None
    assert row.last_evidence_type == "ai_confusion_pattern"


def test_student_quiz_generation_receives_adaptive_quiz_profile(
    client,
    db_session,
    active_tenant,
    monkeypatch,
):
    import src.domains.academic.routes.students as student_routes

    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "adaptive-route@testschool.edu",
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 8", grade_level="8")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, name="Chemistry")
    db_session.add_all([school_class, subject])
    db_session.commit()
    db_session.add(
        SubjectPerformance(
            tenant_id=active_tenant.id,
            student_id=user.id,
            subject_id=subject.id,
            average_score=33.0,
            attendance_rate=88.0,
        )
    )
    db_session.commit()

    async def fake_run_study_tool(request, trace_id=None):
        assert request.adaptive_quiz_profile is not None
        assert request.adaptive_quiz_profile["label"] == "support"
        return {
            "tool": "quiz",
            "topic": request.topic,
            "data": [
                {
                    "question": "Q1",
                    "options": ["A. One", "B. Two"],
                    "correct": "A",
                    "citation": "[chem_p1]",
                    "difficulty": "easy",
                }
            ],
            "citations": [],
            "adaptive_quiz_profile": request.adaptive_quiz_profile,
        }

    monkeypatch.setattr(student_routes, "run_study_tool", fake_run_study_tool)

    response = client.post(
        "/api/student/tools/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"tool": "quiz", "topic": "Acids and bases", "subject_id": str(subject.id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["adaptive_quiz_profile"]["label"] == "support"
    assert payload["data"][0]["difficulty"] == "easy"


def test_student_flashcards_generation_receives_personalization_context(
    client,
    db_session,
    active_tenant,
    monkeypatch,
):
    import src.domains.academic.routes.students as student_routes

    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "adaptive-flashcards@testschool.edu",
    )
    db_session.add(
        TopicMastery(
            tenant_id=active_tenant.id,
            user_id=user.id,
            topic="Photosynthesis",
            concept="chlorophyll",
            mastery_score=38.0,
            confidence_score=0.4,
            last_evidence_type="quiz_completed",
        )
    )
    db_session.commit()

    async def fake_run_study_tool(request, trace_id=None):
        assert request.learner_profile is not None
        assert request.learner_topic_context is not None
        assert "chlorophyll" in request.learner_topic_context["focus_concepts"]
        return {
            "tool": "flashcards",
            "topic": request.topic,
            "data": [{"front": "Chlorophyll", "back": "Captures light.", "citation": "[bio_p1]"}],
            "citations": [],
            "citation_valid": True,
        }

    monkeypatch.setattr(student_routes, "run_study_tool", fake_run_study_tool)

    response = client.post(
        "/api/student/tools/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"tool": "flashcards", "topic": "Photosynthesis"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"][0]["front"] == "Chlorophyll"


def test_personalization_remediation_endpoint_returns_low_mastery_topics(client, db_session, active_tenant):
    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "remediation@testschool.edu",
    )
    db_session.add_all(
        [
            TopicMastery(
                tenant_id=active_tenant.id,
                user_id=user.id,
                topic="Photosynthesis",
                concept="core",
                mastery_score=32.0,
                confidence_score=0.28,
                last_evidence_type="quiz_completed",
            ),
            TopicMastery(
                tenant_id=active_tenant.id,
                user_id=user.id,
                topic="Respiration",
                concept="core",
                mastery_score=48.0,
                confidence_score=0.35,
                last_evidence_type="ai_confusion_pattern",
            ),
        ]
    )
    db_session.commit()

    response = client.get(
        "/api/personalization/remediation",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"]
    assert payload["items"][0]["topic"] == "Photosynthesis"
    assert payload["items"][0]["suggested_tool"] in {"study_guide", "flashcards", "quiz"}


def test_personalization_study_path_endpoint_persists_plan(client, db_session, active_tenant):
    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "study-path@testschool.edu",
    )
    db_session.add(
        TopicMastery(
            tenant_id=active_tenant.id,
            user_id=user.id,
            topic="Photosynthesis",
            concept="core",
            mastery_score=36.0,
            confidence_score=0.31,
            last_evidence_type="quiz_completed",
        )
    )
    db_session.commit()

    response = client.get(
        "/api/personalization/study-path?topic=Photosynthesis&current_surface=overview",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    plan = response.json()["plan"]
    assert plan["focus_topic"] == "Photosynthesis"
    assert len(plan["items"]) == 4
    assert plan["next_action"]["id"] == "guide"

    row = (
        db_session.query(StudyPathPlan)
        .filter(
            StudyPathPlan.tenant_id == active_tenant.id,
            StudyPathPlan.user_id == user.id,
            StudyPathPlan.focus_topic == "Photosynthesis",
        )
        .first()
    )
    assert row is not None
    assert row.plan_type == "remediation"


def test_personalization_study_path_complete_step_advances_next_action(client, db_session, active_tenant):
    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "study-path-progress@testschool.edu",
    )
    db_session.add(
        TopicMastery(
            tenant_id=active_tenant.id,
            user_id=user.id,
            topic="Cell division",
            concept="core",
            mastery_score=34.0,
            confidence_score=0.29,
            last_evidence_type="quiz_completed",
        )
    )
    db_session.commit()

    create_response = client.get(
        "/api/personalization/study-path?topic=Cell division",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 200
    plan = create_response.json()["plan"]

    complete_response = client.post(
        f"/api/personalization/study-path/{plan['id']}/steps/guide/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert complete_response.status_code == 200
    updated_plan = complete_response.json()["plan"]
    assert updated_plan["current_step_index"] == 1
    assert updated_plan["items"][0]["status"] == "completed"
    assert updated_plan["next_action"]["id"] == "flashcards"


def test_personalization_metrics_endpoint_summarizes_served_clicks_and_completion(client, db_session, active_tenant, monkeypatch):
    import src.domains.platform.routes.personalization as personalization_routes

    reset_metrics_registry()
    student, student_token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "personalization-metrics@testschool.edu",
    )
    monkeypatch.setattr(
        personalization_routes,
        "build_profile_aware_recommendations",
        lambda *args, **kwargs: [
            {
                "id": "rec-1",
                "label": "Review Photosynthesis",
                "description": "Revisit the weak topic with a guided study guide.",
                "prompt": "Create a study guide for Photosynthesis",
                "target_tool": "study_guide",
            }
        ],
    )
    admin_user = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="personalization-admin@testschool.edu",
        full_name="Personalization Admin",
        role="admin",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    db_session.add(admin_user)
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 10", grade_level="10")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, name="Biology")
    db_session.add_all([school_class, subject])
    db_session.commit()

    db_session.add_all(
        [
            SubjectPerformance(
                tenant_id=active_tenant.id,
                student_id=student.id,
                subject_id=subject.id,
                average_score=39.0,
                attendance_rate=87.0,
            ),
            TopicMastery(
                tenant_id=active_tenant.id,
                user_id=student.id,
                topic="Photosynthesis",
                concept="core",
                mastery_score=35.0,
                confidence_score=0.3,
                last_evidence_type="quiz_completed",
            ),
            TopicMastery(
                tenant_id=active_tenant.id,
                user_id=student.id,
                topic="Respiration",
                concept="core",
                mastery_score=42.0,
                confidence_score=0.36,
                last_evidence_type="ai_confusion_pattern",
            ),
        ]
    )
    db_session.commit()

    recommendation_response = client.get(
        "/api/personalization/recommendations?current_surface=overview",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert recommendation_response.status_code == 200

    click_response = client.post(
        "/api/personalization/events",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "event_type": "recommendation_click",
            "surface": "overview",
            "target": "study_guide",
        },
    )
    assert click_response.status_code == 200

    study_path_response = client.get(
        "/api/personalization/study-path?topic=Photosynthesis&current_surface=overview",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert study_path_response.status_code == 200
    plan = study_path_response.json()["plan"]

    complete_response = client.post(
        f"/api/personalization/study-path/{plan['id']}/steps/guide/complete",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert complete_response.status_code == 200

    admin_login = client.post(
        "/api/auth/login",
        json={"email": "personalization-admin@testschool.edu", "password": "pass123!"},
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]

    metrics_response = client.get(
        "/api/personalization/metrics",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert metrics_response.status_code == 200
    payload = metrics_response.json()
    assert payload["summary"]["recommendation_served_total"] >= 1
    assert payload["summary"]["recommendation_click_total"] == 1.0
    assert payload["summary"]["study_path_view_total"] == 1.0
    assert payload["summary"]["study_path_step_complete_total"] == 1.0
    assert payload["summary"]["recommendation_ctr_pct"] > 0
    assert any(
        row["surface"] == "overview" and row["recommendation_click_total"] == 1.0
        for row in payload["by_surface"]
    )

    reset_metrics_registry()


def test_personalization_events_endpoint_rejects_unsupported_event(client, db_session, active_tenant):
    reset_metrics_registry()
    _student, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "personalization-bad-event@testschool.edu",
    )

    response = client.post(
        "/api/personalization/events",
        headers={"Authorization": f"Bearer {token}"},
        json={"event_type": "unknown_event", "surface": "overview"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported event_type"
    reset_metrics_registry()
