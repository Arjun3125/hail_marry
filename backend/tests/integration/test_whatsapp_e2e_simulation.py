import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient
from src.domains.identity.models.user import User
from src.domains.identity.models.tenant import Tenant

def _setup_whatsapp_environment(db_session):
    tenant = Tenant(id=uuid4(), name="WhatsApp Test School", domain="wa-test.edu")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant

@pytest.fixture
def mock_whatsapp_payload():
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "12345", "phone_number_id": "67890"},
                            "contacts": [{"profile": {"name": "Test User"}, "wa_id": "919876543210"}],
                            "messages": [
                                {
                                    "from": "919876543210",
                                    "id": "msg_id_123",
                                    "timestamp": "1670000000",
                                    "text": {"body": "How does photosynthesis work?"},
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }

@patch("src.interfaces.rest_api.whatsapp.router.send_text_message", new_callable=AsyncMock)
@patch("src.interfaces.rest_api.whatsapp.agent.run_text_query", new_callable=AsyncMock)
@patch("src.interfaces.rest_api.whatsapp.agent.get_fast_llm")
def test_whatsapp_webhook_text_query(mock_get_llm, mock_run_query, mock_send, client, db_session):
    tenant = _setup_whatsapp_environment(db_session)
    
    # Mock LLM and Chain
    mock_chain = MagicMock()
    # Mock the return value of the chain.invoke to return a WhatsAppIntent
    from src.interfaces.rest_api.whatsapp.agent import WhatsAppIntent
    mock_chain.invoke.return_value = WhatsAppIntent(action="query", extracted_topic="photosynthesis")
    
    # Mock the prompt | structured_llm chain
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = MagicMock()
    mock_get_llm.return_value = mock_llm
    
    # We need to patch the chain inside handle_whatsapp_intent 
    # instead of get_fast_llm if we want to be precise, 
    # but let's just patch the invoke in the agent module directly if possible or the prompt pipe.
    with patch("src.interfaces.rest_api.whatsapp.agent.PromptTemplate.from_template") as mock_prompt:
        mock_prompt.return_value.__or__.return_value = mock_chain
        
        mock_run_query.return_value = {
            "answer": "Photosynthesis is the process by which plants make food.",
            "citations": [{"source": "Science Textbook"}]
        }
        mock_send.return_value = {"success": True}

        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{"from": "919876543210", "type": "text", "text": {"body": "biochem query"}}]
                    }
                }]
            }]
        }

        # The webhook returns OK immediately because it uses BackgroundTasks
        response = client.post("/api/whatsapp/webhook", json=payload)
        assert response.status_code == 200
        assert response.text == "OK"

        # Now we manually trigger the task since TestClient background tasks need to be waited on or tested directly
        # Usually TestClient processes background tasks before returning if we use a specific config, 
        # but let's verify if the side effects happened.
        
        # Wait for potential async? Actually TestClient runs them synchronously.
        mock_run_query.assert_called_once()
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        assert "919876543210" in args
        assert "Photosynthesis" in args[1]
        assert "Science Textbook" in args[1]

@patch("src.interfaces.rest_api.whatsapp.router.send_text_message", new_callable=AsyncMock)
@patch("src.interfaces.rest_api.whatsapp.agent.run_study_tool", new_callable=AsyncMock)
@patch("src.interfaces.rest_api.whatsapp.agent.get_fast_llm")
def test_whatsapp_webhook_study_tool(mock_get_llm, mock_run_tool, mock_send, client, db_session):
    tenant = _setup_whatsapp_environment(db_session)
    
    from src.interfaces.rest_api.whatsapp.agent import WhatsAppIntent
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = WhatsAppIntent(action="quiz", extracted_topic="Biology")
    
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    
    with patch("src.interfaces.rest_api.whatsapp.agent.PromptTemplate.from_template") as mock_prompt:
        mock_prompt.return_value.__or__.return_value = mock_chain
        
        mock_run_tool.return_value = {
            "tool_data": '{"questions": [{"q": "What is life?", "options": ["A", "B", "C"]}]}'
        }
        mock_send.return_value = {"success": True}

        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{"from": "919876543211", "type": "text", "text": {"body": "make a quiz"}}]
                    }
                }]
            }]
        }

        response = client.post("/api/whatsapp/webhook", json=payload)
        assert response.status_code == 200
        
        mock_run_tool.assert_called_once()
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        assert "What is life?" in args[1]
        assert "A. A" in args[1]

def test_whatsapp_webhook_verification(client):
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "valid_token",
        "hub.challenge": "12345"
    }
    with patch("src.interfaces.rest_api.whatsapp.router.settings") as mock_settings:
        mock_settings.whatsapp.verify_token = "valid_token"
        response = client.get("/api/whatsapp/webhook", params=params)
        assert response.status_code == 200
        assert response.text == "12345"
