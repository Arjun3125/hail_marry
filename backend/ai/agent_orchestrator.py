"""Agent orchestrator — multi-step stateful AI workflows (LangGraph-style).

Enables chaining of AI modes (query → quiz → study_guide) into stateful
multi-step workflows with shared context and memory.
"""
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


# ── Workflow definitions ──

WORKFLOW_TEMPLATES = {
    "deep_study": {
        "name": "Deep Study",
        "description": "Research a topic → generate quiz → create study guide",
        "steps": [
            {"mode": "qa", "prompt_template": "Research and explain: {topic}"},
            {"mode": "quiz", "prompt_template": "Generate a quiz on: {topic}"},
            {"mode": "study_guide", "prompt_template": "Create a study guide for: {topic}"},
        ],
    },
    "exam_prep": {
        "name": "Exam Preparation",
        "description": "Topic summary → practice questions → weak area analysis",
        "steps": [
            {"mode": "qa", "prompt_template": "Summarize key concepts for: {topic}"},
            {"mode": "quiz", "prompt_template": "Create 10 practice questions on: {topic}"},
            {"mode": "qa", "prompt_template": "Based on common mistakes, what areas need focus for: {topic}"},
        ],
    },
    "lesson_plan": {
        "name": "Lesson Plan Generator",
        "description": "Topic research → assessment creation → teaching materials",
        "steps": [
            {"mode": "qa", "prompt_template": "Research curriculum content for: {topic}"},
            {"mode": "quiz", "prompt_template": "Create assessment questions for: {topic}"},
            {"mode": "study_guide", "prompt_template": "Create student handout for: {topic}"},
        ],
    },
}


class WorkflowState:
    """Maintains state across multi-step workflow execution."""

    def __init__(self, workflow_id: str, workflow_type: str, params: dict):
        self.workflow_id = workflow_id
        self.workflow_type = workflow_type
        self.params = params
        self.steps_completed: list[dict] = []
        self.current_step = 0
        self.context: str = ""  # accumulated context from previous steps
        self.status = "running"  # running, completed, failed, paused
        self.started_at = datetime.now(timezone.utc)
        self.completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "status": self.status,
            "current_step": self.current_step,
            "total_steps": len(WORKFLOW_TEMPLATES.get(self.workflow_type, {}).get("steps", [])),
            "steps_completed": self.steps_completed,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# ── In-memory workflow store ──
_active_workflows: dict[str, WorkflowState] = {}


def start_workflow(workflow_type: str, params: dict) -> WorkflowState:
    """Start a new multi-step workflow."""
    if workflow_type not in WORKFLOW_TEMPLATES:
        raise ValueError(f"Unknown workflow: {workflow_type}. Available: {list(WORKFLOW_TEMPLATES.keys())}")

    workflow_id = f"wf-{uuid4().hex[:12]}"
    state = WorkflowState(workflow_id, workflow_type, params)
    _active_workflows[workflow_id] = state
    return state


def get_next_step(workflow_id: str) -> Optional[dict]:
    """Get the next step to execute in a workflow."""
    state = _active_workflows.get(workflow_id)
    if not state or state.status != "running":
        return None

    template = WORKFLOW_TEMPLATES.get(state.workflow_type)
    if not template:
        return None

    steps = template["steps"]
    if state.current_step >= len(steps):
        state.status = "completed"
        state.completed_at = datetime.now(timezone.utc)
        return None

    step = steps[state.current_step]
    prompt = step["prompt_template"].format(**state.params)

    # Prepend context from previous steps
    if state.context:
        prompt = f"Previous context:\n{state.context}\n\n{prompt}"

    return {
        "step_index": state.current_step,
        "mode": step["mode"],
        "prompt": prompt,
        "workflow_id": workflow_id,
    }


def record_step_result(workflow_id: str, result: dict):
    """Record the result of a completed step and advance."""
    state = _active_workflows.get(workflow_id)
    if not state:
        raise ValueError("Workflow not found")

    state.steps_completed.append({
        "step_index": state.current_step,
        "mode": result.get("mode", ""),
        "answer_preview": str(result.get("answer", ""))[:200],
        "completed_at": datetime.now(timezone.utc).isoformat(),
    })

    # Accumulate context
    answer = result.get("answer", "")
    state.context += f"\n\n[Step {state.current_step + 1}]: {answer[:500]}"
    state.current_step += 1

    # Check if workflow is complete
    template = WORKFLOW_TEMPLATES.get(state.workflow_type, {})
    if state.current_step >= len(template.get("steps", [])):
        state.status = "completed"
        state.completed_at = datetime.now(timezone.utc)


def get_workflow(workflow_id: str) -> Optional[dict]:
    """Get workflow state by ID."""
    state = _active_workflows.get(workflow_id)
    return state.to_dict() if state else None


def get_workflow_state(workflow_id: str) -> Optional[WorkflowState]:
    """Return the raw workflow state for internal orchestration."""
    return _active_workflows.get(workflow_id)


def list_workflows() -> list[dict]:
    """List all workflow templates."""
    return [
        {"type": k, "name": v["name"], "description": v["description"], "step_count": len(v["steps"])}
        for k, v in WORKFLOW_TEMPLATES.items()
    ]
