import pathlib
import re

agent_path = pathlib.Path('backend/src/interfaces/whatsapp_bot/agent.py')
code = agent_path.read_text(encoding='utf-8')

replacement = '''def _classify_intent_similarity(message: str, role: str) -> dict:
    """Use blazingly fast Jaccard similarity to map user queries to tool descriptions.
    
    Returns dict with 'tool_name' and 'is_general_chat'.
    """
    STOPWORDS = {"what", "is", "my", "the", "a", "an", "can", "you", "show", "me", "tell", "about", "did", "do", "i", "have", "any", "for", "of", "to", "please", "kindly"}
    
    TOOL_CORPUS = {
        "get_student_timetable": {"class", "classes", "schedule", "timetable", "period", "today", "subject", "teach"},
        "get_student_tests": {"test", "tests", "exam", "exams", "quiz", "quizzes", "assessment", "score"},
        "get_student_assignments": {"assignment", "assignments", "homework", "pending", "due", "task", "project"},
        "get_student_attendance": {"attendance", "absent", "present", "leave", "holiday", "attended"},
        "get_student_results": {"marks", "results", "score", "grade", "report", "passed", "failed"},
        "get_student_weak_topics": {"weak", "improve", "study", "guide", "bad", "failing", "attention"},
        "get_teacher_absent_students": {"absent", "students", "who", "missing", "attendance", "today"},
        "get_child_performance": {"child", "performance", "doing", "progress", "marks", "results"},
        "get_child_attendance": {"child", "attendance", "absent", "present", "school"},
        "get_child_homework": {"child", "homework", "assignment", "pending", "due"},
        "get_school_attendance_summary": {"attendance", "summary", "school", "total", "students", "present", "absent"},
        "get_fee_pending_report": {"fee", "fees", "pending", "outstanding", "money", "paid", "due", "report"},
        "get_ai_usage_stats": {"ai", "usage", "stats", "statistics", "queries", "bot"},
        "check_library_catalog": {"library", "books", "book", "author", "catalog", "read", "borrow"}
    }
    
    msg_tokens = set(re.findall(r'\\b\\w+\\b', message.lower())) - STOPWORDS
    
    if not msg_tokens:
        return {"tool_name": None, "is_general_chat": True}
        
    best_tool = None
    best_score = 0.0
    
    from src.shared.ai_tools.whatsapp_tools import TOOL_ROLE_MAP
    
    for tool_name, corpus_tokens in TOOL_CORPUS.items():
        # Enforce RBAC at the routing level
        if role not in TOOL_ROLE_MAP.get(tool_name, set()):
            continue
            
        intersection = len(msg_tokens.intersection(corpus_tokens))
        union = len(msg_tokens.union(corpus_tokens))
        score = float(intersection) / union if union > 0 else 0.0
        
        if score > best_score:
            best_score = score
            best_tool = tool_name
            
    # Threshold for vector similarity match
    if best_score >= 0.15:
        return {"tool_name": best_tool, "is_general_chat": False}
        
    return {"tool_name": None, "is_general_chat": True}
'''

# 1. Replace the LLM function
code = re.sub(r'def _classify_intent_llm\(message: str, role: str, history: list\) -> dict:.*?(?=\n\n\n# ─── Graph Nodes ──────────────────────────────────────────────)', replacement, code, flags=re.DOTALL)

# 2. Update node to call similarity instead of llm
code = code.replace('_classify_intent_llm(message, role, history)', '_classify_intent_similarity(message, role)')

agent_path.write_text(code, encoding='utf-8')
print("Successfully replaced slow LLM intent router with fast Jaccard similarity semantic mapper in agent.py")
