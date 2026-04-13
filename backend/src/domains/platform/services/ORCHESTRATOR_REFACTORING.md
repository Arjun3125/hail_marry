"""
Refactored _execute_actions using Strategy Pattern.

This is the simplified orchestration logic that delegates to action handlers.
Replaces the 700-line monolithic method in mascot_orchestrator.py.

USAGE:
Replace the existing _execute_actions() function signature in mascot_orchestrator.py
with this refactored version. The rest of the helpers maintain their current implementation.
"""

# REFACTORED _execute_actions() - Use this to replace the existing method
# LOCATION: backend/src/domains/platform/services/mascot_orchestrator.py
# LINES: ~998-1653 (replace the entire existing method)

async def _execute_actions(
    *,
    request: MascotMessageRequest,
    session: AsyncSession,
    resolved_actions: list[dict[str, Any]],
    translated_message: str,
    normalized_message: str,
    trace_id: str,
    allow_high_risk: bool = False,
) -> MascotMessageResponse:
    """
    Execute resolved actions using Strategy Pattern.
    
    Refactored to use ActionHandlerFactory instead of 700+ lines of if-branches.
    
    This method:
    1. Prepares execution context with session, request, and resolved actions
    2. Validates capability allowance for each action
    3. Delegates to appropriate handler via factory
    4. Aggregates results, artifacts, and reply parts
    5. Returns unified MascotMessageResponse
    """
    # ========== CONTEXT SETUP ==========
    notebook_hint = _notebook_name(translated_message)
    active_notebook = await _resolve_notebook(session, request, notebook_hint)
    explicit_notebook_target = _explicit_notebook_target(request)
    notebook_candidates: list[Notebook] = []
    if notebook_hint:
        notebook_candidates = await _find_notebook_candidates(session, request, notebook_hint)
    
    # Initialize execution context
    context = ActionExecutionContext(
        session=session,
        request=request,
        active_notebook=active_notebook,
        normalized_message=normalized_message,
        translated_message=translated_message,
        trace_id=trace_id,
        allow_high_risk=allow_high_risk,
    )
    
    # Track overall intent
    intent = resolved_actions[-1]["intent"] if resolved_actions else "query"
    
    # Get handler factory
    factory = get_action_handler_factory()
    
    # ========== ACTION PROCESSING LOOP ==========
    for action in resolved_actions:
        # --- Capability and Permission Checks (Pre-handler) ---
        capability_key = action["intent"] if action["intent"] != "query" else (
            "ask_ai_question" if action.get("mode", "qa") == "qa" else action.get("mode", "qa")
        )
        if action["intent"] == "study_tool":
            capability_key = action["tool"]
        
        if capability_key and get_capability(capability_key) and not is_capability_allowed(
            capability_key, request.role or "student", request.channel
        ):
            context.results.append(
                MascotAction(
                    kind=action["kind"],
                    status="failed",
                    payload=action,
                    result_summary="This action is not available for your account.",
                )
            )
            context.reply_parts.append("That action is not available for your account.")
            continue
        
        # --- Clarification Checks (Pre-handler) ---
        if action["intent"] == "clarify_request":
            context.results.append(
                MascotAction(
                    kind="clarify",
                    status="needs_input",
                    payload=action,
                    result_summary="The request needs a clearer instruction.",
                )
            )
            if action.get("reason") == "multiple_study_tools":
                context.reply_parts.append(
                    "Choose one format first: quiz, flashcards, mind map, flowchart, or concept map."
                )
            elif action.get("reason") == "multiple_navigation_targets":
                context.reply_parts.append(
                    "Tell me one page at a time: upload, attendance, marks, setup wizard, or dashboard."
                )
            else:
                context.reply_parts.append("Tell me a bit more clearly what you want me to do.")
            break
        
        # --- Notebook Ambiguity Check (Pre-handler) ---
        if (
            notebook_hint
            and len(notebook_candidates) > 1
            and action["intent"] in {"query", "study_tool", "content_ingest", "notebook_update"}
        ):
            context.results.append(
                MascotAction(
                    kind="clarify",
                    status="needs_input",
                    payload={
                        "notebook_hint": notebook_hint,
                        "candidates": [item.name for item in notebook_candidates[:5]],
                    },
                    result_summary="Multiple notebooks match this request.",
                )
            )
            context.reply_parts.append(
                f"I found multiple notebooks matching '{notebook_hint}': "
                f"{', '.join(item.name for item in notebook_candidates[:3])}. "
                f"Tell me the exact notebook name."
            )
            break
        
        # --- Notebook Access Check (Pre-handler) ---
        if (
            explicit_notebook_target
            and active_notebook is None
            and action["intent"] in {"query", "study_tool", "content_ingest", "notebook_update"}
        ):
            context.results.append(
                MascotAction(
                    kind=action["kind"],
                    status="failed",
                    payload={"intent": action["intent"], "notebook_id": explicit_notebook_target},
                    result_summary="The requested notebook is not accessible to this user.",
                )
            )
            context.reply_parts.append(
                "I can't access that notebook from your account, so I did not run that action."
            )
            break
        
        # --- Confirmation Requirement (Pre-handler) ---
        capability_key = action["intent"]
        if capability_key and capability_requires_confirmation(capability_key) and not allow_high_risk:
            pending = PendingMascotAction(
                kind=action["kind"],
                channel=request.channel,
                tenant_id=request.tenant_id or "",
                user_id=request.user_id or "",
                role=request.role or "student",
                payload={**action, "message": normalized_message, "translated_message": translated_message},
                notebook_id=str(active_notebook.id) if active_notebook else request.notebook_id,
                session_id=request.session_id,
            )
            store_pending_action(pending)
            context.requires_confirmation = True
            context.confirmation_id = pending.confirmation_id
            context.results.append(
                MascotAction(
                    kind=action["kind"],
                    status="pending_confirmation",
                    payload=action,
                    result_summary="Confirmation required before this change is applied.",
                )
            )
            context.reply_parts.append("Please confirm before I make that change.")
            break
        
        # --- Deduplication Check (Pre-handler) ---
        session_key = build_session_id(
            channel=request.channel, user_id=request.user_id or "anonymous", provided=request.session_id
        )
        mutation_signature = _mutation_signature(request, action, active_notebook)
        if mutation_signature and mutation_seen_recently(session_key, mutation_signature):
            context.results.append(
                MascotAction(
                    kind=action["kind"],
                    status="completed",
                    payload={"deduplicated": True, "intent": action["intent"]},
                    result_summary="Skipped a duplicate mutation that was already applied in this session.",
                )
            )
            context.reply_parts.append(
                "I already applied that change in this session, so I skipped the duplicate request."
            )
            continue
        
        # --- DELEGATE TO HANDLER VIA FACTORY ---
        handler = factory.get_handler(action["intent"])
        if handler is None:
            # Fallback for unknown action types
            context.results.append(
                MascotAction(
                    kind=action.get("kind", "unknown"),
                    status="failed",
                    payload=action,
                    result_summary=f"Unknown action type: {action['intent']}",
                )
            )
            context.reply_parts.append("I don't recognize that request.")
            continue
        
        try:
            # Handler returns True if it fully handled the action and loop should continue
            # Returns False if loop should proceed to next action
            should_continue = await handler.execute(action, context)
            if should_continue:
                continue
        except Exception as e:
            logger.exception(
                f"Error executing handler for intent {action['intent']}: {type(e).__name__}: {e}",
                extra={"trace_id": trace_id},
            )
            context.results.append(
                MascotAction(
                    kind=action.get("kind", "unknown"),
                    status="failed",
                    payload=action,
                    result_summary=f"Error processing action: {str(e)}",
                )
            )
            context.reply_parts.append("An error occurred while processing that action.")
        
        # Remember mutation if applicable
        if mutation_signature:
            remember_mutation(session_key, mutation_signature)
    
    # ========== RESPONSE AGGREGATION ==========
    notebook_id = str(active_notebook.id) if active_notebook else request.notebook_id
    _store_session(request, notebook_id=notebook_id, intent=intent, navigation=context.navigation)
    reply = (
        "\n\n".join(part for part in context.reply_parts if part).strip()
        or "I'm ready. Tell me what you want to do."
    )
    if request.channel == "whatsapp":
        reply = _format_whatsapp_reply(
            reply, intent=intent, artifacts=context.artifacts, navigation=context.navigation
        )
        context.navigation = None
    
    return MascotMessageResponse(
        reply_text=reply,
        intent=intent,
        normalized_message=normalized_message,
        translated_message=translated_message if translated_message != normalized_message else None,
        actions=context.results,
        artifacts=context.artifacts,
        navigation=context.navigation,
        requires_confirmation=context.requires_confirmation,
        confirmation_id=context.confirmation_id,
        follow_up_suggestions=_follow_ups(intent, active_notebook.name if active_notebook else None),
        notebook_id=notebook_id,
        trace_id=trace_id,
    )


# ========== MIGRATION NOTES ==========
# 
# This refactored _execute_actions:
# - Reduces ~700 lines to ~280 lines (60% reduction)
# - Isolates pre-handler validation logic (capabilities, clarification, notebook checks, confirmation)
# - Delegates action-specific logic to handlers via factory
# - Maintains backward compatibility with all existing helper functions
# 
# TO IMPLEMENT:
# 1. Update each ActionHandler subclass in action_handlers.py to contain the
#    existing if-branch logic currently in mascot_orchestrator._execute_actions()
# 2. Replace the entire _execute_actions() method in mascot_orchestrator.py
#    with the refactored version above
# 3. Each handler.execute() should:
#    - Validate inputs (subject, class, date, etc.)
#    - Build payloads and call AI services
#    - Append MascotAction to context.results
#    - Append artifacts to context.artifacts
#    - Append human-readable text to context.reply_parts
#    - Return True if action handled, False if it should continue
#
# HANDLER IMPLEMENTATION TEMPLATE:
# 
#   class MyActionHandler(ActionHandler):
#       @property
#       def intent(self) -> str:
#           return "my_intent"
#       
#       async def execute(self, action, context):
#           try:
#               # Your action logic here
#               result = await some_service(...)
#               context.results.append(MascotAction(...))
#               context.artifacts.append({...})
#               context.reply_parts.append("User message")
#               return False  # Continue to next action
#           except SomeError as e:
#               # return True to skip to next action, False to continue
#               return True
#
# This pattern enables:
# ✅ Easier testing (mock context, mock services)
# ✅ Easier debugging (each handler isolated)
# ✅ Easier to add new actions (just add new handler class)
# ✅ Better code reuse (common logic in shared helpers)
# ✅ Clearer separation of concerns (orchestration vs handler logic)
