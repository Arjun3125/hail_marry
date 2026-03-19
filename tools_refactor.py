import pathlib
import re

f = pathlib.Path('backend/src/shared/ai_tools/whatsapp_tools.py')
c = f.read_text(encoding='utf-8')

# Swap all SessionLocal to SessionLocalRO
c = c.replace('from database import SessionLocal', 'from database import SessionLocalRO')
c = c.replace('SessionLocal()', 'SessionLocalRO()')

# Substitute the attendance summary
redis_att = '''def get_school_attendance_summary(tenant_id: str) -> str:
    """Get today's school-wide attendance summary."""
    try:
        from src.domains.platform.services.ai_queue import _get_redis_client
        redis_client = _get_redis_client()
        data = redis_client.get(f"tenant:{tenant_id}:analytics:attendance")
        if data:
            import json
            parsed = json.loads(data)
            return f"School Attendance Summary:\\nTotal Students: {parsed['total_students']}\\nPresent: {parsed['present_today']}\\nAbsent: {parsed['absent_today']}"
        return "Attendance summary not available right now. Please try again later."
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("get_school_attendance_summary error: %s", e)
        return "Error accessing attendance summary."
'''

# Substitute the fee report
redis_fee = '''def get_fee_pending_report(tenant_id: str) -> str:
    """Get outstanding fee report for the school."""
    try:
        from src.domains.platform.services.ai_queue import _get_redis_client
        redis_client = _get_redis_client()
        data = redis_client.get(f"tenant:{tenant_id}:analytics:fees")
        if data:
            import json
            parsed = json.loads(data)
            return f"Total pending fees: {parsed.get('total_pending_amount')} {parsed.get('currency', 'USD')}"
        return "Financial report not available right now. Please try again later."
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("get_fee_pending_report error: %s", e)
        return "Error fetching fee report."
'''

c = re.sub(r'def get_school_attendance_summary\(tenant_id: str\) -> str:.*?(?=\n\n\n@tool)', redis_att, c, flags=re.DOTALL)
c = re.sub(r'def get_fee_pending_report\(tenant_id: str\) -> str:.*?(?=\n\n\n@tool)', redis_fee, c, flags=re.DOTALL)
f.write_text(c, encoding='utf-8')
print('Updated whatsapp_tools.py')
