"""
Action Handler Strategy Pattern for Mascot Orchestrator.

Breaks down 20+ action type branches into separate, testable handler classes.
Each handler is responsible for a specific action intent type.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domains.platform.services.mascot_schemas import MascotAction, MascotMessageRequest as MascotRequest
from src.domains.academic.models import Enrollment, Assignment, Attendance, ParentLink
from src.domains.platform.models.notebook import Notebook
from src.domains.identity.models.user import User


class ActionExecutionContext:
    """Context shared across all action handlers during execution."""

    def __init__(
        self,
        session: Session,
        request: MascotRequest,
        active_notebook: Optional[Notebook],
        normalized_message: str,
        translated_message: str,
        trace_id: str,
        allow_high_risk: bool = False,
    ):
        self.session = session
        self.request = request
        self.active_notebook = active_notebook
        self.normalized_message = normalized_message
        self.translated_message = translated_message
        self.trace_id = trace_id
        self.allow_high_risk = allow_high_risk

        # Mutable state during execution
        self.results: list[MascotAction] = []
        self.artifacts: list[dict[str, Any]] = []
        self.reply_parts: list[str] = []
        self.navigation: Optional[dict[str, Any]] = None
        self.requires_confirmation = False
        self.confirmation_id: Optional[str] = None


class ActionHandler(ABC):
    """Base class for all action handlers following Strategy Pattern."""

    @property
    @abstractmethod
    def intent(self) -> str:
        """The action intent this handler processes (e.g., 'notebook_create')."""
        pass

    @abstractmethod
    async def execute(
        self,
        action: dict[str, Any],
        context: ActionExecutionContext,
    ) -> bool:
        """
        Execute the action.

        Args:
            action: The action dict with intent, parameters, etc.
            context: Shared execution context with session, request, etc.

        Returns:
            True if action was handled, False to continue to next action.
            Side effects: appends to context.results, context.artifacts, context.reply_parts.
        """
        pass


# ============================================================================
# GROUP 1: NOTEBOOK OPERATIONS (2 handlers)
# ============================================================================

class NotebookCreateHandler(ActionHandler):
    """Handler for creating new notebooks."""

    @property
    def intent(self) -> str:
        return "notebook_create"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _create_notebook,
            _web_nav,
        )
        
        notebook_name = (action.get("name") or "New Notebook").strip()
        active_notebook = await _create_notebook(context.session, context.request, notebook_name)
        
        context.navigation = _web_nav(
            context.request.role or "student", 
            "ai_studio", 
            str(active_notebook.id)
        )
        context.results.append(
            MascotAction(
                kind="notebook_create",
                status="completed",
                payload={"name": notebook_name, "notebook_id": str(active_notebook.id)},
                result_summary=f"Created notebook '{active_notebook.name}'.",
            )
        )
        context.reply_parts.append(f"Created notebook '{active_notebook.name}'.")
        context.active_notebook = active_notebook
        return False  # Continue to next action


class NotebookUpdateHandler(ActionHandler):
    """Handler for updating notebooks (rename, archive)."""

    @property
    def intent(self) -> str:
        return "notebook_update"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _notebook_by_name,
        )
        
        target = context.active_notebook or await _notebook_by_name(
            context.session, context.request, action.get("notebook_name")
        )
        if target is None:
            context.results.append(
                MascotAction(
                    kind="notebook_update",
                    status="failed",
                    payload=action,
                    result_summary="Notebook not found.",
                )
            )
            context.reply_parts.append("I could not find that notebook.")
            return True  # Handled
        
        if action.get("operation") == "rename":
            new_name = (action.get("name") or "").strip()
            if not new_name:
                context.results.append(
                    MascotAction(
                        kind="clarify",
                        status="needs_input",
                        payload=action,
                        result_summary="Missing new notebook name.",
                    )
                )
                context.reply_parts.append("Tell me the new notebook name too.")
                return True
            
            target.name = new_name
            await context.session.commit()
            await context.session.refresh(target)
            context.active_notebook = target
            context.results.append(
                MascotAction(
                    kind="notebook_update",
                    status="completed",
                    payload={"operation": "rename", "notebook_id": str(target.id)},
                    result_summary=f"Renamed notebook to '{new_name}'.",
                )
            )
            context.reply_parts.append(f"Renamed the notebook to '{new_name}'.")
        
        elif action.get("operation") == "archive":
            target.is_active = False
            await context.session.commit()
            context.results.append(
                MascotAction(
                    kind="notebook_update",
                    status="completed",
                    payload={"operation": "archive", "notebook_id": str(target.id)},
                    result_summary=f"Archived notebook '{target.name}'.",
                )
            )
            context.reply_parts.append(f"Archived notebook '{target.name}'.")
        
        return True  # Handled


# ============================================================================
# GROUP 2: NAVIGATION (1 handler)
# ============================================================================

class NavigateHandler(ActionHandler):
    """Handler for navigation intents."""

    @property
    def intent(self) -> str:
        return "navigate"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import _web_nav
        
        navigation = _web_nav(
            context.request.role or "student",
            action["target"],
            str(context.active_notebook.id) if context.active_notebook else None,
        )
        if navigation:
            context.navigation = navigation
            context.results.append(
                MascotAction(
                    kind="navigate",
                    status="completed",
                    payload=navigation,
                    result_summary=f"Prepared navigation to {navigation['href']}.",
                )
            )
            context.reply_parts.append(
                f"Opening {str(action['target']).replace('_', ' ')}."
            )
        else:
            context.results.append(
                MascotAction(
                    kind="navigate",
                    status="failed",
                    payload=action,
                    result_summary="No route available for that target.",
                )
            )
            context.reply_parts.append("I could not find that page for your account.")
        
        return True  # Handled


# ============================================================================
# GROUP 3: TEACHER REPORTS (2 handlers)
# ============================================================================

class TeacherInsightsReportHandler(ActionHandler):
    """Handler for teacher insights reports."""

    @property
    def intent(self) -> str:
        return "teacher_insights_report"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _teacher_class_ids,
            _build_teacher_insights,
        )
        
        class_ids = await _teacher_class_ids(context.session, context.request)
        insights = await _build_teacher_insights(context.session, context.request, class_ids)
        context.artifacts.append({"tool": "teacher_insights_report", **insights})
        context.results.append(
            MascotAction(
                kind="query",
                status="completed",
                payload={"report": "teacher_insights_report"},
                result_summary=insights["summary"],
            )
        )
        context.reply_parts.append(insights["summary"])
        return True  # Handled


class TeacherDoubtHeatmapHandler(ActionHandler):
    """Handler for teacher doubt heatmap reports."""

    @property
    def intent(self) -> str:
        return "teacher_doubt_heatmap_report"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _teacher_class_ids,
            _build_teacher_doubt_heatmap,
        )
        
        class_ids = await _teacher_class_ids(context.session, context.request)
        heatmap = await _build_teacher_doubt_heatmap(context.session, context.request, class_ids)
        context.artifacts.append({"tool": "teacher_doubt_heatmap_report", **heatmap})
        context.results.append(
            MascotAction(
                kind="query",
                status="completed",
                payload={"report": "teacher_doubt_heatmap_report"},
                result_summary=heatmap["summary"],
            )
        )
        context.reply_parts.append(heatmap["summary"])
        return True  # Handled


# ============================================================================
# GROUP 4: TEACHER WORKFLOWS (3 handlers)
# ============================================================================

class TeacherAssessmentGenerateHandler(ActionHandler):
    """Handler for generating teacher assessments."""

    @property
    def intent(self) -> str:
        return "teacher_assessment_generate"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _resolve_subject,
            run_text_query,
        )
        from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest
        
        topic = (action.get("topic") or context.translated_message).strip()
        subject = await _resolve_subject(context.session, context.request, context.translated_message)
        if subject is None:
            context.results.append(
                MascotAction(
                    kind="clarify",
                    status="needs_input",
                    payload=action,
                    result_summary="I need the subject name to generate a teacher assessment.",
                )
            )
            context.reply_parts.append(
                "Tell me the subject name too, for example: generate a Biology assessment on photosynthesis."
            )
            return True
        
        prompt_query = (
            f"Generate exactly {int(action.get('num_questions') or 5)} multiple-choice questions about: {topic}. "
            f"Subject: {subject.name}. Format as JSON array."
        )
        assessment = await run_text_query(
            InternalAIQueryRequest(
                tenant_id=context.request.tenant_id or "",
                query=prompt_query,
                mode="quiz",
                subject_id=str(subject.id),
            ),
            trace_id=context.trace_id,
        )
        summary = f"Generated an assessment for {subject.name} on {topic}."
        context.artifacts.append(
            {
                "tool": "teacher_assessment_generate",
                "subject": subject.name,
                "topic": topic,
                "assessment": assessment.get("answer", ""),
                "citations": assessment.get("citations", []),
            }
        )
        context.results.append(
            MascotAction(
                kind="query",
                status="completed",
                payload={
                    "report": "teacher_assessment_generate",
                    "subject_id": str(subject.id),
                    "topic": topic,
                },
                result_summary=summary,
            )
        )
        context.reply_parts.append(summary)
        return True  # Handled


class TeacherAttendanceMarkHandler(ActionHandler):
    """Handler for marking teacher attendance."""

    @property
    def intent(self) -> str:
        return "teacher_attendance_mark"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _safe_uuid,
            _parse_date_hint,
            _teacher_can_access_class,
        )
        
        class_uuid = _safe_uuid(action.get("class_id"))
        if not await _teacher_can_access_class(context.session, context.request, class_uuid):
            context.results.append(
                MascotAction(
                    kind="teacher_workflow",
                    status="failed",
                    payload=action,
                    result_summary="That class is outside your allowed teaching scope.",
                )
            )
            context.reply_parts.append("That class is outside your allowed teaching scope.")
            return True
        
        attendance_date = _parse_date_hint(action.get("attendance_date")) or datetime.now(timezone.utc).date()
        absent_ids = {
            _safe_uuid(item.get("student_id")) for item in (action.get("absent_students") or [])
        }
        absent_ids.discard(None)
        
        enrollment_result = await context.session.execute(
            select(Enrollment).where(
                Enrollment.tenant_id == _safe_uuid(context.request.tenant_id),
                Enrollment.class_id == class_uuid,
            )
        )
        enrollments = list(enrollment_result.scalars().all())
        
        for enrollment in enrollments:
            existing_result = await context.session.execute(
                select(Attendance).where(
                    Attendance.tenant_id == _safe_uuid(context.request.tenant_id),
                    Attendance.class_id == class_uuid,
                    Attendance.student_id == enrollment.student_id,
                    Attendance.date == attendance_date,
                )
            )
            existing = existing_result.scalar_one_or_none()
            status = "absent" if enrollment.student_id in absent_ids else "present"
            
            if existing is None:
                context.session.add(
                    Attendance(
                        tenant_id=_safe_uuid(context.request.tenant_id),
                        class_id=class_uuid,
                        student_id=enrollment.student_id,
                        date=attendance_date,
                        status=status,
                    )
                )
            else:
                existing.status = status
        
        await context.session.commit()
        summary = f"Marked attendance for {action.get('class_name')} on {attendance_date.isoformat()}."
        context.results.append(
            MascotAction(
                kind="teacher_workflow",
                status="completed",
                payload={
                    "intent": "teacher_attendance_mark",
                    "class_id": action.get("class_id"),
                    "attendance_date": attendance_date.isoformat(),
                    "absent_count": len(absent_ids),
                },
                result_summary=summary,
            )
        )
        context.artifacts.append(
            {
                "tool": "teacher_attendance_mark",
                "class_name": action.get("class_name"),
                "date": attendance_date.isoformat(),
                "absent_students": action.get("absent_students", []),
            }
        )
        context.reply_parts.append(summary)
        return True  # Handled


class TeacherHomeworkCreateHandler(ActionHandler):
    """Handler for creating teacher homework."""

    @property
    def intent(self) -> str:
        return "teacher_homework_create"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _safe_uuid,
            _parse_date_hint,
            _teacher_can_access_subject,
            submit_async_job,
            _notify_homework_recipients,
        )
        
        subject_uuid = _safe_uuid(action.get("subject_id"))
        class_uuid = _safe_uuid(action.get("class_id"))
        
        if not await _teacher_can_access_subject(
            context.session, context.request, subject_uuid
        ):
            context.results.append(
                MascotAction(
                    kind="teacher_workflow",
                    status="failed",
                    payload=action,
                    result_summary="That subject is outside your allowed teaching scope.",
                )
            )
            context.reply_parts.append("That subject is outside your allowed teaching scope.")
            return True
        
        due_date = _parse_date_hint(action.get("due_date"))
        assignment = Assignment(
            tenant_id=_safe_uuid(context.request.tenant_id),
            subject_id=subject_uuid,
            title=str(action.get("title") or "Homework")[:255],
            description=str(action.get("description") or "").strip(),
            due_date=(
                datetime.combine(due_date, datetime.min.time(), tzinfo=timezone.utc)
                if due_date
                else None
            ),
            created_by=_safe_uuid(context.request.user_id),
        )
        context.session.add(assignment)
        await context.session.commit()
        await context.session.refresh(assignment)
        
        # Fetch student and parent recipients
        enrollment_result = await context.session.execute(
            select(Enrollment, User)
            .join(User, User.id == Enrollment.student_id)
            .where(
                Enrollment.tenant_id == _safe_uuid(context.request.tenant_id),
                Enrollment.class_id == class_uuid,
                User.tenant_id == _safe_uuid(context.request.tenant_id),
            )
        )
        roster = list(enrollment_result.all())
        student_recipients = [
            {
                "user_id": str(user.id),
                "student_id": str(user.id),
                "student_name": user.full_name or "Student",
            }
            for enrollment, user in roster
        ]
        student_ids = [enrollment.student_id for enrollment, _user in roster]
        
        parent_recipients: list[dict[str, str]] = []
        if student_ids:
            parent_link_result = await context.session.execute(
                select(ParentLink, User)
                .join(User, User.id == ParentLink.parent_id)
                .where(
                    ParentLink.tenant_id == _safe_uuid(context.request.tenant_id),
                    ParentLink.child_id.in_(student_ids),
                    User.tenant_id == _safe_uuid(context.request.tenant_id),
                )
            )
            student_name_map = {
                str(user.id): user.full_name or "Student" for _enrollment, user in roster
            }
            for parent_link, parent_user in parent_link_result.all():
                parent_recipients.append(
                    {
                        "user_id": str(parent_user.id),
                        "student_id": str(parent_link.child_id),
                        "student_name": student_name_map.get(
                            str(parent_link.child_id), "Student"
                        ),
                    }
                )
        
        submit_async_job(
            "teacher-homework-notifications",
            _notify_homework_recipients,
            tenant_id=context.request.tenant_id or "",
            teacher_id=context.request.user_id or "",
            assignment_id=str(assignment.id),
            class_name=str(action.get("class_name") or ""),
            subject_name=str(action.get("subject_name") or ""),
            title=str(action.get("title") or "Homework"),
            description=str(action.get("description") or ""),
            due_date=due_date.isoformat() if due_date else None,
            student_recipients=student_recipients,
            parent_recipients=parent_recipients,
        )
        
        summary = f"Created homework '{assignment.title}' for {action.get('class_name')}."
        if due_date:
            summary = f"{summary} Due {due_date.isoformat()}."
        
        context.results.append(
            MascotAction(
                kind="teacher_workflow",
                status="completed",
                payload={
                    "intent": "teacher_homework_create",
                    "assignment_id": str(assignment.id),
                    "subject_id": action.get("subject_id"),
                    "class_id": action.get("class_id"),
                },
                result_summary=summary,
            )
        )
        context.artifacts.append(
            {
                "tool": "teacher_homework_create",
                "assignment_id": str(assignment.id),
                "title": assignment.title,
                "class_name": action.get("class_name"),
                "subject_name": action.get("subject_name"),
                "due_date": due_date.isoformat() if due_date else None,
            }
        )
        context.reply_parts.append(summary)
        return True  # Handled


# ============================================================================
# GROUP 5: PARENT REPORTS (1 handler)
# ============================================================================

class ParentProgressReportHandler(ActionHandler):
    """Handler for parent progress reports."""

    @property
    def intent(self) -> str:
        return "parent_progress_report"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _build_parent_progress_report,
        )
        
        progress = await _build_parent_progress_report(context.session, context.request)
        context.artifacts.append({"tool": "parent_progress_report", **progress})
        context.results.append(
            MascotAction(
                kind="query",
                status="completed",
                payload={"report": "parent_progress_report"},
                result_summary=progress["summary"],
            )
        )
        context.reply_parts.append(progress["summary"])
        return True  # Handled


# ============================================================================
# GROUP 6: STUDY PATH (2 handlers)
# ============================================================================

class StudyPathReportHandler(ActionHandler):
    """Handler for study path reports."""

    @property
    def intent(self) -> str:
        return "study_path_report"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _build_study_path_plan,
            _ui_metadata,
        )
        
        topic = action.get("topic") or context.translated_message
        plan = await _build_study_path_plan(
            context.session,
            context.request,
            topic=topic,
            current_surface=(
                _ui_metadata(context.request).get("current_surface")
                or (
                    context.request.ui_context.current_route
                    if context.request.ui_context
                    else None
                )
            ),
        )
        next_action = plan.get("next_action") if isinstance(plan, dict) else None
        summary = (
            f"Your current study path for {plan.get('focus_topic') or 'this topic'} "
            f"has {len(plan.get('items') or [])} steps."
        )
        if isinstance(next_action, dict):
            summary += f" Next: {next_action.get('title') or 'continue the next step'}."
        
        context.artifacts.append({"tool": "study_path", "plan": plan})
        context.results.append(
            MascotAction(
                kind="query",
                status="completed",
                payload={"report": "study_path_report", "plan_id": plan.get("id")},
                result_summary=summary,
            )
        )
        context.reply_parts.append(summary)
        return True  # Handled


class StudyPathExecuteHandler(ActionHandler):
    """Handler for executing study paths."""

    @property
    def intent(self) -> str:
        return "study_path_execute"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _build_study_path_plan,
            _ui_metadata,
            _TOOLS,
            _QUERY_MODES,
            run_study_tool,
            run_text_query,
            _build_adaptive_quiz_profile_for_request,
            _safe_uuid,
        )
        from src.domains.platform.schemas.ai_runtime import (
            InternalStudyToolGenerateRequest,
            InternalAIQueryRequest,
        )
        
        topic = action.get("topic") or context.translated_message
        plan = await _build_study_path_plan(
            context.session,
            context.request,
            topic=topic,
            current_surface=(
                _ui_metadata(context.request).get("current_surface")
                or (
                    context.request.ui_context.current_route
                    if context.request.ui_context
                    else None
                )
            ),
        )
        context.artifacts.append({"tool": "study_path", "plan": plan})
        next_action = plan.get("next_action") if isinstance(plan, dict) else None
        
        if not isinstance(next_action, dict):
            summary = "I could not find a pending study-path step for you right now."
            context.results.append(
                MascotAction(
                    kind="query",
                    status="completed",
                    payload={"report": "study_path_execute", "plan_id": plan.get("id")},
                    result_summary=summary,
                )
            )
            context.reply_parts.append(summary)
            return True
        
        next_tool = str(next_action.get("target_tool") or "study_guide").strip()
        next_prompt = str(
            next_action.get("prompt") or plan.get("focus_topic") or context.translated_message
        ).strip()
        
        tool_result = None
        if next_tool in _TOOLS:
            # Get mastery aware prompt padding
            profile = _build_adaptive_quiz_profile_for_request(context.request, topic=next_prompt)
            if profile and profile.get("prompt_suffix"):
                next_prompt = f"{next_prompt}\n\n[Pedagogy Instruction: {profile['prompt_suffix']}]"
            
            tool_result = await run_study_tool(
                InternalStudyToolGenerateRequest(
                    tenant_id=context.request.tenant_id or "",
                    user_id=context.request.user_id,
                    tool=next_tool,
                    topic=next_prompt,
                    notebook_id=(
                        context.active_notebook.id
                        if context.active_notebook
                        else _safe_uuid(context.request.notebook_id)
                    ),
                ),
                trace_id=context.trace_id,
            )
            context.artifacts.append(
                {
                    "tool": next_tool,
                    "data": tool_result.get("data"),
                    "citations": tool_result.get("citations", []),
                }
            )
        else:
            mode = (
                next_tool if next_tool in _QUERY_MODES or next_tool == "qa" else "study_guide"
            )
            query_result = await run_text_query(
                InternalAIQueryRequest(
                    tenant_id=context.request.tenant_id or "",
                    user_id=context.request.user_id,
                    query=next_prompt,
                    mode=mode,
                    notebook_id=(
                        context.active_notebook.id
                        if context.active_notebook
                        else _safe_uuid(context.request.notebook_id)
                    ),
                ),
                trace_id=context.trace_id,
            )
            context.artifacts.append(
                {
                    "tool": mode,
                    "answer": query_result.get("answer"),
                    "citations": query_result.get("citations", []),
                    "mode": query_result.get("mode"),
                }
            )
            tool_result = query_result
        
        summary = (
            f"Started your study path with: "
            f"{next_action.get('title') or next_tool.replace('_', ' ')}."
        )
        context.results.append(
            MascotAction(
                kind="query",
                status="completed",
                payload={
                    "report": "study_path_execute",
                    "plan_id": plan.get("id"),
                    "target_tool": next_tool,
                },
                result_summary=summary,
            )
        )
        context.reply_parts.append(summary)
        
        if tool_result and tool_result.get("answer"):
            context.reply_parts.append(str(tool_result["answer"]).strip())
        
        return True  # Handled


# ============================================================================
# GROUP 7: ADMIN REPORTS (3 handlers)
# ============================================================================

class AdminReleaseGateReportHandler(ActionHandler):
    """Handler for admin release gate reports."""

    @property
    def intent(self) -> str:
        return "admin_release_gate_report"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _build_admin_release_gate_report,
        )
        
        snapshot = _build_admin_release_gate_report(context.request)
        context.artifacts.append({"tool": "admin_release_gate_report", **snapshot})
        context.results.append(
            MascotAction(
                kind="query",
                status="completed",
                payload={"report": "admin_release_gate_report"},
                result_summary=snapshot["summary"],
            )
        )
        context.reply_parts.append(snapshot["summary"])
        return True  # Handled


class AdminOnboardingReportHandler(ActionHandler):
    """Handler for admin onboarding reports."""

    @property
    def intent(self) -> str:
        return "admin_onboarding_report"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _build_admin_onboarding_report,
        )
        
        onboarding = await _build_admin_onboarding_report(context.session, context.request)
        context.artifacts.append({"tool": "admin_onboarding_report", **onboarding})
        context.results.append(
            MascotAction(
                kind="query",
                status="completed",
                payload={"report": "admin_onboarding_report"},
                result_summary=onboarding["summary"],
            )
        )
        context.reply_parts.append(onboarding["summary"])
        return True  # Handled


class AdminAIReviewReportHandler(ActionHandler):
    """Handler for admin AI review reports."""

    @property
    def intent(self) -> str:
        return "admin_ai_review_report"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _build_admin_ai_review_report,
        )
        
        review = await _build_admin_ai_review_report(context.session, context.request)
        context.artifacts.append({"tool": "admin_ai_review_report", **review})
        context.results.append(
            MascotAction(
                kind="query",
                status="completed",
                payload={"report": "admin_ai_review_report"},
                result_summary=review["summary"],
            )
        )
        context.reply_parts.append(review["summary"])
        return True  # Handled


# ============================================================================
# GROUP 8: STRUCTURED IMPORTS (5 handlers)
# ============================================================================

class TeacherRosterImportHandler(ActionHandler):
    """Handler for teacher roster imports."""

    @property
    def intent(self) -> str:
        return "teacher_roster_import"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _apply_teacher_roster_import,
        )
        
        roster_result = await _apply_teacher_roster_import(
            context.session, context.request, action
        )
        context.artifacts.append(roster_result)
        context.results.append(
            MascotAction(
                kind="structured_import",
                status="completed",
                payload={
                    "intent": "teacher_roster_import",
                    "created_count": roster_result.get("created_count", 0),
                },
                result_summary=roster_result["summary"],
            )
        )
        context.reply_parts.append(roster_result["summary"])
        return True  # Handled


class AdminTeacherImportHandler(ActionHandler):
    """Handler for admin teacher imports."""

    @property
    def intent(self) -> str:
        return "admin_teacher_import"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _apply_admin_teacher_import,
        )
        
        teacher_import = await _apply_admin_teacher_import(
            context.session, context.request, action
        )
        context.artifacts.append(teacher_import)
        context.results.append(
            MascotAction(
                kind="structured_import",
                status="completed",
                payload={
                    "intent": "admin_teacher_import",
                    "created_count": teacher_import.get("created_count", 0),
                },
                result_summary=teacher_import["summary"],
            )
        )
        context.reply_parts.append(teacher_import["summary"])
        return True  # Handled


class AdminStudentImportHandler(ActionHandler):
    """Handler for admin student imports."""

    @property
    def intent(self) -> str:
        return "admin_student_import"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _apply_admin_student_import,
        )
        
        student_import = await _apply_admin_student_import(
            context.session, context.request, action
        )
        context.artifacts.append(student_import)
        context.results.append(
            MascotAction(
                kind="structured_import",
                status="completed",
                payload={
                    "intent": "admin_student_import",
                    "created": student_import.get("created", 0),
                },
                result_summary=student_import["summary"],
            )
        )
        context.reply_parts.append(student_import["summary"])
        return True  # Handled


class TeacherAttendanceImportHandler(ActionHandler):
    """Handler for teacher attendance imports."""

    @property
    def intent(self) -> str:
        return "teacher_attendance_import"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _apply_teacher_attendance_import,
        )
        
        attendance_result = await _apply_teacher_attendance_import(
            context.session, context.request, action
        )
        context.artifacts.append(attendance_result)
        context.results.append(
            MascotAction(
                kind="structured_import",
                status="completed",
                payload={
                    "intent": "teacher_attendance_import",
                    "imported": attendance_result.get("imported", 0),
                },
                result_summary=attendance_result["summary"],
            )
        )
        context.reply_parts.append(attendance_result["summary"])
        return True  # Handled


class TeacherMarksImportHandler(ActionHandler):
    """Handler for teacher marks imports."""

    @property
    def intent(self) -> str:
        return "teacher_marks_import"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _apply_teacher_marks_import,
        )
        
        marks_result = await _apply_teacher_marks_import(
            context.session, context.request, action
        )
        context.artifacts.append(marks_result)
        context.results.append(
            MascotAction(
                kind="structured_import",
                status="completed",
                payload={
                    "intent": "teacher_marks_import",
                    "imported": marks_result.get("imported", 0),
                    "exam_id": marks_result.get("exam_id"),
                },
                result_summary=marks_result["summary"],
            )
        )
        context.reply_parts.append(marks_result["summary"])
        return True  # Handled


# ============================================================================
# GROUP 9: CONTENT INGESTION (1 handler)
# ============================================================================

class ContentIngestHandler(ActionHandler):
    """Handler for content ingestion from URLs and YouTube."""

    @property
    def intent(self) -> str:
        return "content_ingest"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            _resolve_subject,
            _safe_uuid,
            run_url_ingestion,
        )
        from src.domains.platform.schemas.ai_runtime import InternalIngestURLRequest
        from src.domains.platform.models.document import Document
        from uuid import uuid4
        
        url = str(action.get("url") or "").strip()
        if not url:
            context.results.append(
                MascotAction(
                    kind="content_ingest",
                    status="failed",
                    payload=action,
                    result_summary="Missing content URL.",
                )
            )
            context.reply_parts.append("I need a URL or YouTube link to ingest.")
            return True
        
        if action.get("source_kind") == "youtube":
            from src.infrastructure.llm.cache import invalidate_tenant_cache
            from src.infrastructure.llm.providers import (
                get_embedding_provider,
                get_vector_store_provider,
            )
            from src.infrastructure.vector_store.ingestion import ingest_youtube
            
            subject = await _resolve_subject(
                context.session, context.request, context.translated_message
            )
            document_id = str(uuid4())
            chunks = ingest_youtube(
                url=url,
                document_id=document_id,
                tenant_id=context.request.tenant_id or "",
                subject_id=str(subject.id) if subject else None,
                notebook_id=str(context.active_notebook.id) if context.active_notebook else None,
            )
            if chunks:
                embeddings = await get_embedding_provider().embed_batch(
                    [chunk.text for chunk in chunks]
                )
                get_vector_store_provider(context.request.tenant_id or "").add_chunks(
                    [
                        {
                            "text": chunk.text,
                            "document_id": chunk.document_id,
                            "page_number": chunk.page_number,
                            "section_title": chunk.section_title or "",
                            "subject_id": chunk.subject_id or "",
                            "notebook_id": chunk.notebook_id or "",
                            "source_file": chunk.source_file or "",
                        }
                        for chunk in chunks
                    ],
                    embeddings,
                )
            invalidate_tenant_cache(context.request.tenant_id or "")
            ingest = {
                "document_id": document_id,
                "title": action.get("title") or "YouTube lecture",
                "chunks_created": len(chunks),
            }
        else:
            ingest = await run_url_ingestion(
                InternalIngestURLRequest(
                    tenant_id=context.request.tenant_id or "",
                    url=url,
                    title=action.get("title"),
                    notebook_id=(
                        UUID(str(context.active_notebook.id))
                        if context.active_notebook
                        else None
                    ),
                ),
                trace_id=context.trace_id,
            )
            
            if context.active_notebook and context.request.user_id and context.request.tenant_id:
                subject = (
                    await _resolve_subject(
                        context.session, context.request, context.translated_message
                    )
                    if action.get("source_kind") == "youtube"
                    else None
                )
                document = Document(
                    id=UUID(str(ingest["document_id"])),
                    tenant_id=_safe_uuid(context.request.tenant_id),
                    subject_id=subject.id if subject else None,
                    notebook_id=context.active_notebook.id,
                    uploaded_by=_safe_uuid(context.request.user_id),
                    file_name=ingest.get("title") or url[:120],
                    file_type="youtube"
                    if action.get("source_kind") == "youtube"
                    else "url",
                    storage_path=url,
                    ingestion_status="completed",
                    chunk_count=int(ingest.get("chunks_created", 0)),
                )
                context.session.add(document)
                await context.session.commit()
        
        context.results.append(
            MascotAction(
                kind="content_ingest",
                status="completed",
                payload={
                    "url": url,
                    "document_id": ingest.get("document_id"),
                },
                result_summary=f"Ingested {ingest.get('title') or 'that link'} into the knowledge base.",
            )
        )
        context.reply_parts.append(
            f"Ingested {ingest.get('title') or 'that link'} into the knowledge base."
        )
        return True  # Handled


# ============================================================================
# GROUP 10: STUDY TOOL (1 handler)
# ============================================================================

class StudyToolHandler(ActionHandler):
    """Handler for study tool invocations."""

    @property
    def intent(self) -> str:
        return "study_tool"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import (
            run_study_tool,
            _save_generated,
            _build_adaptive_quiz_profile_for_request,
        )
        from src.domains.platform.schemas.ai_runtime import InternalStudyToolGenerateRequest
        from uuid import UUID
        
        topic = (action.get("topic") or context.translated_message).strip()
        if not topic:
            context.results.append(
                MascotAction(
                    kind="clarify",
                    status="needs_input",
                    payload=action,
                    result_summary="Missing topic for study tool.",
                )
            )
            context.reply_parts.append("Tell me the topic too.")
            return True
        
        tool = action["tool"]
        
        # Inject mastery context
        profile = _build_adaptive_quiz_profile_for_request(
            context.request,
            topic=topic,
        )
        final_prompt = topic
        if profile and profile.get("prompt_suffix"):
            final_prompt = f"{topic}\n\n[Pedagogy Instruction: {profile['prompt_suffix']}]"
        
        tool_result = await run_study_tool(
            InternalStudyToolGenerateRequest(
                tenant_id=context.request.tenant_id or "",
                tool=tool,
                topic=final_prompt,
                notebook_id=(
                    UUID(str(context.active_notebook.id))
                    if context.active_notebook
                    else None
                ),
            ),
            trace_id=context.trace_id,
        )
        
        generated = await _save_generated(
            context.session,
            context.request,
            context.active_notebook,
            tool,
            topic,
            tool_result,
        )
        
        if generated:
            context.results.append(
                MascotAction(
                    kind="generated_content_save",
                    status="completed",
                    payload={"generated_content_id": str(generated.id)},
                    result_summary="Saved generated content to the notebook library.",
                )
            )
        
        context.artifacts.append(
            {
                "tool": tool,
                "data": tool_result.get("data"),
                "citations": tool_result.get("citations", []),
            }
        )
        context.results.append(
            MascotAction(
                kind="study_tool",
                status="completed",
                payload={"tool": tool, "topic": topic},
                result_summary=f"Generated {tool.replace('_', ' ')} for {topic}.",
            )
        )
        context.reply_parts.append(f"Generated {tool.replace('_', ' ')} for {topic}.")
        return True  # Handled


# ============================================================================
# GROUP 11: FALLBACK QUERY (1 handler)
# ============================================================================

class QueryHandler(ActionHandler):
    """Fallback handler for general AI queries."""

    @property
    def intent(self) -> str:
        return "query"

    async def execute(self, action: dict[str, Any], context: ActionExecutionContext) -> bool:
        from src.domains.platform.services.mascot_orchestrator import run_text_query
        from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest
        from uuid import UUID
        
        topic = (action.get("topic") or context.translated_message).strip()
        mode = action.get("mode", "qa")
        
        query_result = await run_text_query(
            InternalAIQueryRequest(
                tenant_id=context.request.tenant_id or "",
                query=topic or context.translated_message,
                mode=mode,
                notebook_id=(
                    UUID(str(context.active_notebook.id))
                    if context.active_notebook
                    else None
                ),
                language="english",
                response_length="default",
                expertise_level="standard",
            ),
            trace_id=context.trace_id,
        )
        
        context.artifacts.append(
            {
                "tool": mode,
                "answer": query_result.get("answer"),
                "citations": query_result.get("citations", []),
                "mode": query_result.get("mode"),
            }
        )
        context.results.append(
            MascotAction(
                kind="query",
                status="completed",
                payload={"mode": mode, "topic": topic},
                result_summary=f"Answered using {mode.replace('_', ' ')} mode.",
            )
        )
        
        if query_result.get("answer"):
            context.reply_parts.append(str(query_result["answer"]).strip())
        
        return True  # Handled


class ActionHandlerFactory:
    """Factory for creating and managing action handlers."""

    def __init__(self):
        """Initialize factory with all available handlers."""
        self._handlers: dict[str, ActionHandler] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register all action handlers."""
        handlers = [
            NotebookCreateHandler(),
            NotebookUpdateHandler(),
            NavigateHandler(),
            TeacherInsightsReportHandler(),
            TeacherDoubtHeatmapHandler(),
            TeacherAssessmentGenerateHandler(),
            TeacherAttendanceMarkHandler(),
            TeacherHomeworkCreateHandler(),
            ParentProgressReportHandler(),
            StudyPathReportHandler(),
            StudyPathExecuteHandler(),
            AdminReleaseGateReportHandler(),
            AdminOnboardingReportHandler(),
            AdminAIReviewReportHandler(),
            TeacherRosterImportHandler(),
            AdminTeacherImportHandler(),
            AdminStudentImportHandler(),
            TeacherAttendanceImportHandler(),
            TeacherMarksImportHandler(),
            ContentIngestHandler(),
            StudyToolHandler(),
            QueryHandler(),
        ]
        for handler in handlers:
            self._handlers[handler.intent] = handler

    def get_handler(self, intent: str) -> Optional[ActionHandler]:
        """Get handler for given intent, returns None if not found."""
        return self._handlers.get(intent)

    def get_all_intents(self) -> list[str]:
        """Get list of all registered intents."""
        return list(self._handlers.keys())


# Global factory instance
_action_handler_factory = ActionHandlerFactory()


def get_action_handler_factory() -> ActionHandlerFactory:
    """Get the global action handler factory."""
    return _action_handler_factory
