"""LangChain Tools exposing ERP functionality to the AI Agent."""
import json
from uuid import UUID

from langchain_core.tools import tool

from src.domains.administrative.services.library import search_catalog, get_library_stats

# Using a global context hack or passing state via RunnableConfig in real LangGraph
# but for simplicity, we mock Db session access for the agent tools if needed
from database import SessionLocalRO
from src.domains.platform.services.ai_queue import _get_redis_client

@tool
def check_library_catalog(query: str, tenant_id: str) -> str:
    """Search the school library catalog for books by title, author, or ISBN.
    
    Args:
        query: What to search for (e.g. 'Photosynthesis', 'Tolstoy').
        tenant_id: The UUID of the school tenant.
    """
    try:
        db = SessionLocalRO()
        books = search_catalog(db, UUID(tenant_id), query=query, limit=5)
        db.close()
        
        if not books:
            return f"No books found matching '{query}' in the library."
            
        results = [f"Title: {b.title}, Category: {b.category}, Available: {b.available_copies}/{b.total_copies}, Shelf: {b.shelf_location or 'N/A'}" for b in books]
        return "Found the following books:\n" + "\n".join(results)
    except Exception as e:
        return f"Error querying library: {str(e)}"

@tool
def get_school_library_stats(tenant_id: str) -> str:
    """Get high-level statistics about the school library (total books, overdue, etc).
    
    Args:
        tenant_id: The UUID of the school tenant.
    """
    try:
        db = SessionLocalRO()
        stats = get_library_stats(db, UUID(tenant_id))
        db.close()
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error fetching library stats: {str(e)}"

@tool
def get_school_financial_report(tenant_id: str) -> str:
    """Get the overall financial fee report for the school (total due, collected, outstanding).
    
    Args:
        tenant_id: The UUID of the school tenant.
    """
    try:
        redis_client = _get_redis_client()
        data = redis_client.get(f"tenant:{tenant_id}:analytics:fees")
        if data:
            parsed = json.loads(data)
            return f"Total pending fees: {parsed.get('total_pending_amount')} {parsed.get('currency', 'USD')}"
        return "Financial report not available right now. Please try again later."
    except Exception as e:
        return f"Error fetching fee report: {str(e)}"
