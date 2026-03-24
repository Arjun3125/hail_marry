import logging
import json
from decimal import Decimal
from sqlalchemy import func
from config import settings
from database import SessionLocal
from src.infrastructure.llm.cache import _get_redis as _get_redis_client

# We will need to import the actual models used for Attendance and Fees.
# Assuming standard domain layouts based on the previous tools:
from src.domains.academic.models.attendance import DailyAttendance
from src.domains.administrative.models.fee import FeeRecord
from src.domains.identity.models.user import User

logger = logging.getLogger(__name__)

REDIS_TTL = 900  # 15 minutes cache

from sqlalchemy.orm import Session

def aggregate_tenant_analytics(tenant_id: str, db: Session | None = None):
    """
    Calculate heavy analytics for a specific tenant and store in Redis.
    """
    owns_session = db is None
    if owns_session:
        db = SessionLocal()
    
    redis_client = _get_redis_client()
    try:
        # 1. School Attendance Summary
        # Simple count for demonstration. In reality, it matches the erp_tools logic.
        total_students = db.query(User).filter_by(tenant_id=tenant_id, role="student", is_active=True).count()
        today_attendance = db.query(DailyAttendance).filter_by(tenant_id=tenant_id).count() # Simplified
        
        attendance_data = {
            "total_students": total_students,
            "present_today": today_attendance,
            "absent_today": total_students - today_attendance if total_students > today_attendance else 0
        }
        
        redis_client.setex(
            f"tenant:{tenant_id}:analytics:attendance",
            REDIS_TTL,
            json.dumps(attendance_data)
        )
        
        # 2. Fee Pending Report
        total_pending = db.query(func.sum(FeeRecord.balance_amount)).filter(
            FeeRecord.tenant_id == tenant_id,
            FeeRecord.status == "pending"
        ).scalar() or Decimal("0.00")
        
        fee_data = {
            "total_pending_amount": float(total_pending),
            "currency": "USD" # Replace with tenant currency
        }
        
        redis_client.setex(
            f"tenant:{tenant_id}:analytics:fees",
            REDIS_TTL,
            json.dumps(fee_data)
        )
        
        logger.info(f"Successfully aggregated analytics for tenant {tenant_id}")
        
    finally:
        if owns_session:
            db.close()


def run_analytics_aggregation():
    """
    Find all active tenants and trigger analytics aggregation.
    """
    logger.info("Starting background analytics aggregation...")
    db = SessionLocal()
    try:
        from src.domains.identity.models.tenant import Tenant
        tenants = db.query(Tenant).filter_by(is_active=True).all()
        for t in tenants:
            aggregate_tenant_analytics(t.id, db=db)
    except Exception as e:
        logger.error(f"Failed to run global analytics aggregation: {e}")
    finally:
        db.close()
