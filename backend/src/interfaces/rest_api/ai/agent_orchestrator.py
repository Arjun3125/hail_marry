"""Agent orchestrator — multi-step stateful AI workflows (LangGraph-style).

Enables chaining of AI modes (query -> quiz -> study_guide) into stateful
multi-step workflows with shared context and memory properly powered by a LangGraph StateGraph
and persisted via Redis.
"""
import json
from datetime import datetime, timezone
from typing import TypedDict, Annotated, Optional
import operator
from uuid import uuid4

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END

from src.infrastructure.llm.cache import _get_redis

WORKFLOW_TEMPLATES = {
    "deep_study": {
        "name": "Deep Study",
        "description": "Research a topic -> generate quiz -> create study guide",
    },
    "exam_prep": {
        "name": "Exam Preparation",
        "description": "Topic summary -> practice questions -> weak area analysis",
    },
    "lesson_plan": {
        "name": "Lesson Plan Generator",
        "description": "Topic research -> assessment creation -> teaching materials",
    },
    "admin_assistant": {
        "name": "School Administration Desk",
        "description": "Handle queries for library tracking, book availability, and financial fee status",
    },
}

_active_workflows: dict[str, dict] = {}

class AgentState(TypedDict):
    workflow_id: str
    workflow_type: str
    params: dict
    topic: str
    steps_completed: list[dict]
    current_step: int
    context: str
    status: str
    
    # LangGraph transient memory for the next action to pass back to the API
    pending_mode: Optional[str]
    pending_prompt: Optional[str]
    
    # Admin context gathered from tools
    tool_context: Optional[str]

from src.shared.ai_tools.erp_tools import check_library_catalog, get_school_library_stats, get_school_financial_report

def plan_node(state: AgentState) -> dict:
    """Agent node that decides the next step based on context."""
    step_val = state.get("current_step")
    current_step = int(step_val) if step_val is not None else 0
    if current_step >= 3:
        return {"status": "completed", "pending_mode": None, "pending_prompt": None}
        
    w_type = str(state.get("workflow_type", "deep_study"))
    topic = state.get('topic', 'General')
    
    # Fast path for Administrative workflow: Use tools natively
    if w_type == "admin_assistant":
        if current_step > 0:
            return {"status": "completed", "pending_mode": None, "pending_prompt": None}
            
        llm = ChatOllama(model="llama3.2", temperature=0.1)
        tools = [check_library_catalog, get_school_library_stats, get_school_financial_report]
        llm_with_tools = llm.bind_tools(tools)
        
        sys_prompt = f"You are a school admin assistant. Answer this query using your tools: {topic}"
        try:
            # Simplistic 1-step ReAct simulation for demo purposes
            res = llm_with_tools.invoke([SystemMessage(content=sys_prompt)])
            if hasattr(res, "tool_calls") and res.tool_calls:
                tool_call = res.tool_calls[0]
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Execute tool manually
                tool_result = ""
                if tool_name == "check_library_catalog":
                    tool_result = check_library_catalog.invoke(tool_args)
                elif tool_name == "get_school_library_stats":
                    tool_result = get_school_library_stats.invoke(tool_args)
                elif tool_name == "get_school_financial_report":
                    tool_result = get_school_financial_report.invoke(tool_args)
                    
                # Ask LLM to summarize tool out
                final_res = llm.invoke([
                    SystemMessage(content="Summarize the tool output for the user's query: " + topic),
                    SystemMessage(content="Tool output: " + str(tool_result))
                ])
                return {"pending_mode": "qa", "pending_prompt": "Provide this exact summary: " + final_res.content}
            else:
                return {"pending_mode": "qa", "pending_prompt": "Respond with: " + res.content}
        except Exception as e:
            return {
                "pending_mode": "qa",
                "pending_prompt": "Respond with: Sorry, the admin tools are temporarily unavailable. Please retry the request in a moment.",
            }

    # Standard JSON-based Learning Orchestrator Path
    from pydantic import BaseModel, Field
    from typing import Literal
    
    class OrchestratorDecision(BaseModel):
        action: Literal["continue", "finish"] = Field(description="continue or finish")
        mode: Literal["qa", "quiz", "study_guide", "concept_map"] = Field(description="the study mode")
        prompt_template: str = Field(description="the specific query")

    llm = ChatOllama(model="llama3.2", format="json", temperature=0.1)
    structured_llm = llm.with_structured_output(OrchestratorDecision)
    
    goal = WORKFLOW_TEMPLATES.get(w_type, {}).get("description", "Learn")
    
    sys_prompt = f"""You are an autonomous learning orchestrator.
Goal: {goal}
Topic: {topic}
Completed steps: {current_step}
Context from previous steps:
{state.get('context', '')}

Decide the NEXT atomic step to advance the user's comprehension.
"""
    try:
        data = structured_llm.invoke([SystemMessage(content=sys_prompt)])
        if data.action == "finish":
            return {"status": "completed", "pending_mode": None, "pending_prompt": None}
            
        return {
            "pending_mode": data.mode,
            "pending_prompt": data.prompt_template
        }
    except Exception:
        fallback_modes = ["qa", "quiz", "study_guide"]
        mode = fallback_modes[current_step % len(fallback_modes)]
        return {
            "pending_mode": mode,
            "pending_prompt": f"Provide a {mode} regarding {topic}"
        }

def should_continue(state: AgentState):
    if state.get("status") == "completed":
        return END
    return END  # Always suspend graph execution to return control to HTTP REST caller

# Build the LangGraph
workflow = StateGraph(AgentState)
workflow.add_node("plan", plan_node)
workflow.set_entry_point("plan")
workflow.add_conditional_edges("plan", should_continue)
orchestrator_app = workflow.compile()


# --- Legacy API Wrappers to keep routes/ai.py stable ---

class WorkflowState:
    """Facade for backward compatibility, heavily utilizing AgentState dict internally."""
    def __init__(self, state_dict: dict):
        self.state = state_dict

    @property
    def workflow_id(self): return self.state.get("workflow_id")
    @property
    def status(self): return self.state.get("status")
    @property
    def current_step(self): return self.state.get("current_step", 0)
    @property
    def params(self): return self.state.get("params", {})

    def to_dict(self):
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.state.get("workflow_type"),
            "params": self.params,
            "status": self.status,
            "current_step": self.current_step,
            "total_steps": 3,
            "steps_completed": self.state.get("steps_completed", []),
            "context": self.state.get("context", ""),
        }
        
    def save(self):
        redis = _get_redis()
        if redis:
            redis.setex(f"wf:{self.workflow_id}", 86400, json.dumps(self.state))
        else:
            _active_workflows[self.workflow_id] = self.state

    @classmethod
    def load(cls, workflow_id: str) -> Optional['WorkflowState']:
        redis = _get_redis()
        if redis:
            data = redis.get(f"wf:{workflow_id}")
            if data:
                return cls(json.loads(data))
        else:
            state_dict = _active_workflows.get(workflow_id)
            if state_dict:
                return cls(state_dict)
        return None


async def start_workflow(workflow_type: str, params: dict) -> WorkflowState:
    """Initialize state and bootstrap first step."""
    workflow_id = f"wf-{uuid4().hex[:12]}"
    
    state: AgentState = {
        "workflow_id": workflow_id,
        "workflow_type": workflow_type,
        "params": params,
        "topic": params.get("topic", "General"),
        "steps_completed": [],
        "current_step": 0,
        "context": "",
        "status": "running",
        "pending_mode": None,
        "pending_prompt": None,
        "tool_context": None,
    }
    
    # Run the graph once to plan the first step!
    new_state = orchestrator_app.invoke(state)
    
    ws = WorkflowState(new_state)
    ws.save()
    return ws


def get_next_step(workflow_id: str) -> Optional[dict]:
    """Retrieve LangGraph's planned pending step."""
    ws = WorkflowState.load(workflow_id)
    if ws is None or ws.status != "running":
        return None

    state = ws.state
    if not state.get("pending_mode"):
        # Invoke LangGraph to plan the step
        state = orchestrator_app.invoke(state)
        ws.state = state
        ws.save()

    if state.get("status") == "completed" or not state.get("pending_mode"):
        return None

    return {
        "step_index": state.get("current_step", 0),
        "mode": state.get("pending_mode"),
        "prompt": state.get("pending_prompt"),
        "workflow_id": workflow_id,
    }

def record_step_result(workflow_id: str, result: dict):
    """Advance the LangGraph state machine with the execution result."""
    ws = WorkflowState.load(workflow_id)
    if ws is None:
        raise ValueError("Workflow not found")

    state = ws.state
    step_val = state.get("current_step")
    idx = int(step_val) if step_val is not None else 0
    
    state["steps_completed"].append({
        "step_index": idx,
        "mode": str(result.get("mode", "")),
        "answer_preview": str(result.get("answer", ""))[:200],
        "completed_at": datetime.now(timezone.utc).isoformat(),
    })
    
    answer = str(result.get("answer", ""))
    state["context"] = str(state.get("context", "")) + f"\n\n[Step {idx + 1} Result]: {answer[:500]}"
    state["current_step"] = idx + 1
    
    # Wipe the pending action so LangGraph must re-plan on next call
    state["pending_mode"] = None
    state["pending_prompt"] = None
    
    # Auto-run graph to plan next step or mark completed
    new_state = orchestrator_app.invoke(state)
    ws.state = new_state
    
    if int(ws.state.get("current_step", 0)) >= 3:
        ws.state["status"] = "completed"
        
    ws.save()

def get_workflow(workflow_id: str) -> Optional[dict]:
    ws = WorkflowState.load(workflow_id)
    return ws.to_dict() if ws else None

def get_workflow_state(workflow_id: str) -> Optional[WorkflowState]:
    return WorkflowState.load(workflow_id)

def list_workflows() -> list[dict]:
    return [
        {"type": k, "name": v["name"], "description": v["description"], "step_count": 3}
        for k, v in WORKFLOW_TEMPLATES.items()
    ]
