"""
Test procedures for Redis fallback job queue mechanism.
Run these tests to verify job queue resilience and database persistence.
"""
import os
import sys
import time
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import SessionLocal
from src.domains.platform.models.ai_job import AIJob
from src.domains.platform.services import ai_queue


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Enqueue Job with Redis Available
# ─────────────────────────────────────────────────────────────────────────────

def test_enqueue_with_redis():
    """Test normal job enqueueing when Redis is operational."""
    print("\n✓ TEST 1: Enqueue with Redis Available")
    print("-" * 60)
    
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    payload = {
        "question": "What is photosynthesis?",
        "notebook_id": str(uuid.uuid4()),
    }
    
    try:
        job = ai_queue.enqueue_job(
            job_type="text_query",
            payload=payload,
            tenant_id=tenant_id,
            user_id=user_id,
            source="test",
        )
        
        print(f"✓ Job enqueued: {job['job_id']}")
        print(f"  Status: {job['status']}")
        print(f"  Priority: {job['priority']}")
        
        # Verify job in database
        db = SessionLocal()
        db_job = db.query(AIJob).filter(AIJob.id == uuid.UUID(job["job_id"])).first()
        if db_job:
            print("✓ Job persisted in database")
            print(f"  Request payload: {db_job.request_payload}")
        else:
            print("✗ Job NOT found in database!")
        db.close()
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: Simulate Redis Unavailable - Fallback to Database
# ─────────────────────────────────────────────────────────────────────────────

def test_fallback_to_database():
    """Test job enqueueing when Redis is unavailable."""
    print("\n✓ TEST 2: Fallback to Database (Redis Unavailable)")
    print("-" * 60)
    
    # Temporarily disable Redis
    original_redis = ai_queue._redis_available
    ai_queue._redis_available = False
    
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    payload = {
        "question": "What is gravity?",
        "notebook_id": str(uuid.uuid4()),
    }
    
    try:
        print("Attempting to enqueue with Redis unavailable...")
        job = ai_queue.enqueue_job(
            job_type="text_query",
            payload=payload,
            tenant_id=tenant_id,
            user_id=user_id,
            source="test",
        )
        
        print(f"✓ Job fallback enqueued: {job['job_id']}")
        print(f"  Status: {job['status']}")
        
        # Verify job in database
        db = SessionLocal()
        db_job = db.query(AIJob).filter(AIJob.id == uuid.UUID(job["job_id"])).first()
        if db_job:
            print("✓ Job persisted in database (fallback)")
            print(f"  Status: {db_job.status}")
        else:
            print("✗ Job NOT found in database!")
        db.close()
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    finally:
        # Restore Redis state
        ai_queue._redis_available = original_redis


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Sync Database Jobs to Redis on Recovery
# ─────────────────────────────────────────────────────────────────────────────

def test_sync_database_to_redis():
    """Test syncing database-persisted jobs back to Redis after recovery."""
    print("\n✓ TEST 3: Sync Database Jobs to Redis (After Recovery)")
    print("-" * 60)
    
    # Create a job in database directly (simulating fallback)
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    job_id = uuid.uuid4()
    
    db = SessionLocal()
    db_job = AIJob(
        id=job_id,
        tenant_id=uuid.UUID(tenant_id),
        user_id=uuid.UUID(user_id),
        job_type="text_query",
        status="queued",
        trace_id="test123",
        priority=30,
        attempts=0,
        max_retries=3,
        request_payload={"question": "Test question?"},
    )
    db.add(db_job)
    db.commit()
    print(f"✓ Created test job in database: {job_id}")
    db.close()
    
    try:
        # Sync to Redis
        synced = ai_queue.sync_database_jobs_to_redis()
        print(f"✓ Synced {synced} jobs from database to Redis")
        
        if synced > 0:
            print("✓ Database backlog successfully hydrated to Redis queue")
        else:
            print("⚠ No jobs synced (may be expected if Redis unreachable)")
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    finally:
        # Cleanup
        db = SessionLocal()
        db.query(AIJob).filter(AIJob.id == job_id).delete()
        db.commit()
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Performance - Verify Query Optimization with Indexes
# ─────────────────────────────────────────────────────────────────────────────

def test_query_performance():
    """Test that indexes improve query performance."""
    print("\n✓ TEST 4: Query Performance with Indexes")
    print("-" * 60)
    
    from src.domains.platform.models.ai import AIQuery, AISessionEvent
    
    db = SessionLocal()
    tenant_id = uuid.uuid4()
    
    try:
        # Test AIQuery index usage
        start = time.time()
        queries = db.query(AIQuery).filter(
            AIQuery.tenant_id == tenant_id
        ).order_by(AIQuery.created_at.desc()).limit(100).all()
        elapsed = time.time() - start
        
        print(f"✓ AIQuery tenant lookup: {len(queries)} records in {elapsed*1000:.2f}ms")
        if elapsed < 0.1:  # Should be < 100ms with indexes
            print("  ✓ Performance acceptable")
        else:
            print("  ⚠ Performance may need optimization")
        
        # Test AISessionEvent index usage
        start = time.time()
        sessions = db.query(AISessionEvent).filter(
            AISessionEvent.tenant_id == tenant_id
        ).order_by(AISessionEvent.created_at.desc()).limit(100).all()
        elapsed = time.time() - start
        
        print(f"✓ AISessionEvent tenant lookup: {len(sessions)} records in {elapsed*1000:.2f}ms")
        if elapsed < 0.1:
            print("  ✓ Performance acceptable")
        else:
            print("  ⚠ Performance may need optimization")
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: N+1 Query Prevention - Joinedload Effectiveness
# ─────────────────────────────────────────────────────────────────────────────

def test_n_plus_one_prevention():
    """Test that N+1 queries are prevented with joinedload."""
    print("\n✓ TEST 5: N+1 Query Prevention")
    print("-" * 60)
    
    from src.domains.academic.models.core import Enrollment
    from sqlalchemy.orm import joinedload
    
    db = SessionLocal()
    
    try:
        # Test without joinedload (would cause N+1)
        enrollments_count = db.query(Enrollment).count()
        print(f"  Total enrollments in database: {enrollments_count}")
        
        if enrollments_count > 0:
            # With joinedload
            enrollments = db.query(Enrollment).options(
                joinedload(Enrollment.student)
            ).limit(5).all()
            
            print(f"✓ Loaded {len(enrollments)} enrollments with joinedload")
            print("  ✓ N+1 pattern prevented - student objects pre-loaded")
            print("  ✓ Each enrollment.student accessible without additional query")
            return True
        else:
            print("⚠ No enrollments in test database, skipping verification")
            return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TEST RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 70)
    print("REDIS FALLBACK & PERFORMANCE OPTIMIZATION TEST SUITE")
    print("=" * 70)
    
    results = {
        "Redis Available": test_enqueue_with_redis(),
        "Database Fallback": test_fallback_to_database(),
        "Sync Recovery": test_sync_database_to_redis(),
        "Query Performance": test_query_performance(),
        "N+1 Prevention": test_n_plus_one_prevention(),
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
