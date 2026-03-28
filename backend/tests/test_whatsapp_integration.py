import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from src.domains.identity.models.user import User
from src.domains.identity.models.tenant import Tenant
from src.interfaces.rest_api.whatsapp.router import get_or_create_whatsapp_user
from src.interfaces.rest_api.whatsapp.agent import handle_whatsapp_intent, WhatsAppIntent

@pytest.fixture
def mock_db_session():
    db = MagicMock(spec=Session)
    tenant = Tenant(id="tenant-123", name="Test School")
    db.query().first.return_value = tenant
    return db

def test_get_or_create_whatsapp_user(mock_db_session):
    phone = "+123456789"
    # User does not exist, so DB returns None for the first filter
    mock_db_session.query().filter().first.return_value = None
    
    user = get_or_create_whatsapp_user(phone, mock_db_session)
    
    assert user.phone_number == phone
    assert user.whatsapp_linked is True
    assert user.email.startswith("wa_123456789")
    mock_db_session.add.assert_called_once_with(user)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch("src.interfaces.rest_api.whatsapp.agent.get_fast_llm")
@patch("src.interfaces.rest_api.whatsapp.agent.run_study_tool")
async def test_handle_whatsapp_quiz_intent(mock_run_study_tool, mock_get_llm, mock_db_session):
    # Mock LLM Router returning 'quiz' format
    mock_structured_llm = MagicMock()
    mock_chain = MagicMock()
    mock_get_llm.return_value.with_structured_output.return_value = mock_structured_llm
    
    # We patch the | operator manually for test mock, or we mock invoke directly
    prompt_mock = MagicMock()
    prompt_mock.__or__.return_value = mock_chain
    
    with patch("src.interfaces.rest_api.whatsapp.agent.PromptTemplate.from_template", return_value=prompt_mock):
        mock_chain.invoke.return_value = WhatsAppIntent(action="quiz", extracted_topic="Biology")
        
        user = User(tenant_id="t1", id="u1", phone_number="+1")
        mock_run_study_tool.return_value = {
            "tool_data": '{"questions": [{"q": "What is DNA?", "options": ["A", "B"], "answer": 0}]}',
            "citations": []
        }
        
        response = await handle_whatsapp_intent(user, "make a quiz on biology", None, mock_db_session)
        
        # Verify WhatsApp formatting
        assert "Generated Quiz" in response
        assert "What is DNA?" in response
        assert "A." in response
        mock_run_study_tool.assert_called_once()
