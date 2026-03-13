"""Tests for agent orchestrator."""
import pytest
from ai.agent_orchestrator import (
    WORKFLOW_TEMPLATES, WorkflowState, start_workflow,
    get_next_step, record_step_result, get_workflow, list_workflows,
)


def test_workflow_templates():
    assert "deep_study" in WORKFLOW_TEMPLATES
    assert "exam_prep" in WORKFLOW_TEMPLATES
    assert "lesson_plan" in WORKFLOW_TEMPLATES


def test_deep_study_has_3_steps():
    assert len(WORKFLOW_TEMPLATES["deep_study"]["steps"]) == 3


def test_start_workflow():
    state = start_workflow("deep_study", {"topic": "Photosynthesis"})
    assert state.status == "running"
    assert state.current_step == 0


def test_start_unknown_workflow():
    with pytest.raises(ValueError, match="Unknown workflow"):
        start_workflow("nonexistent", {})


def test_get_next_step():
    state = start_workflow("exam_prep", {"topic": "Algebra"})
    step = get_next_step(state.workflow_id)
    assert step is not None
    assert step["mode"] == "qa"
    assert "Algebra" in step["prompt"]


def test_record_step_advances():
    state = start_workflow("deep_study", {"topic": "Physics"})
    step = get_next_step(state.workflow_id)
    record_step_result(state.workflow_id, {"answer": "Physics is cool", "mode": "qa"})
    assert state.current_step == 1


def test_workflow_completes():
    state = start_workflow("deep_study", {"topic": "Math"})
    for i in range(3):
        step = get_next_step(state.workflow_id)
        record_step_result(state.workflow_id, {"answer": f"Step {i}", "mode": step["mode"]})
    assert state.status == "completed"


def test_list_workflows():
    templates = list_workflows()
    assert len(templates) >= 3
    names = [t["type"] for t in templates]
    assert "deep_study" in names


def test_workflow_state_to_dict():
    state = WorkflowState("wf-test", "deep_study", {"topic": "Test"})
    d = state.to_dict()
    assert d["workflow_id"] == "wf-test"
    assert d["status"] == "running"
