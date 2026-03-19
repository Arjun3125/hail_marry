"""Tests for agent orchestrator."""
import pytest
from src.interfaces.rest_api.ai.agent_orchestrator import (
    WORKFLOW_TEMPLATES, WorkflowState, start_workflow,
    get_next_step, record_step_result, get_workflow, list_workflows,
)

def test_workflow_templates():
    assert "deep_study" in WORKFLOW_TEMPLATES
    assert "exam_prep" in WORKFLOW_TEMPLATES
    assert "lesson_plan" in WORKFLOW_TEMPLATES

@pytest.mark.asyncio
async def test_start_workflow():
    state = await start_workflow("deep_study", {"topic": "Photosynthesis"})
    assert state.status == "running"
    assert state.current_step == 0
    # There is no longer a static `steps` array since planning is fully autonomous via LangGraph

@pytest.mark.asyncio
async def test_get_next_step():
    state = await start_workflow("exam_prep", {"topic": "Algebra"})
    step = get_next_step(state.workflow_id)
    assert step is not None
    assert step["mode"] in ("qa", "quiz", "study_guide", "concept_map")

@pytest.mark.asyncio
async def test_record_step_advances():
    state = await start_workflow("deep_study", {"topic": "Physics"})
    step = get_next_step(state.workflow_id)
    record_step_result(state.workflow_id, {"answer": "Physics is cool", "mode": step["mode"] if step else "qa"})
    
    # Reload from cache check
    updated_state = get_workflow(state.workflow_id)
    assert updated_state["current_step"] == 1

@pytest.mark.asyncio
async def test_workflow_completes():
    state = await start_workflow("deep_study", {"topic": "Math"})
    for i in range(3):
        step = get_next_step(state.workflow_id)
        if step:
            record_step_result(state.workflow_id, {"answer": f"Step {i}", "mode": step["mode"]})
        else:
            break
    
    final_state = get_workflow(state.workflow_id)
    assert final_state["status"] == "completed"

def test_list_workflows():
    templates = list_workflows()
    assert len(templates) >= 3
    names = [t["type"] for t in templates]
    assert "deep_study" in names

def test_workflow_state_to_dict():
    state = WorkflowState({
        "workflow_id": "wf-test",
        "workflow_type": "deep_study",
        "params": {"topic": "Test"},
        "status": "running",
        "current_step": 0
    })
    d = state.to_dict()
    assert d["workflow_id"] == "wf-test"
    assert d["status"] == "running"

@pytest.mark.asyncio
async def test_admin_assistant_workflow():
    # Start an administrative workflow (e.g., asking about the library fees or books)
    # We will pass a simple query to see if the LLM binds to the tool
    state = await start_workflow("admin_assistant", {"topic": "Do we have any books on biology?"})
    
    assert state.status == "running"
    
    # LangGraph should have triggered the tool and formulated an answer 
    # instead of plotting a 3-step course.
    step = get_next_step(state.workflow_id)
    assert step is not None
    assert step["mode"] == "qa"
    # The prompt should contain the summarized tool output.
    assert "Respond with" in step["prompt"] or "Provide this exact summary" in step["prompt"]
    
    # Record the final answer and it should complete immediately Since admin_assistant is a 1-shot tool loop
    record_step_result(state.workflow_id, {"answer": "Yes, we have biology books.", "mode": "qa"})
    final_state = get_workflow(state.workflow_id)
    assert final_state["status"] == "completed"
