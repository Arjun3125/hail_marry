from unittest.mock import AsyncMock, patch


@patch("src.domains.platform.routes.whatsapp.send_text_message", new_callable=AsyncMock)
@patch("src.domains.platform.routes.whatsapp.process_inbound_message", new_callable=AsyncMock)
@patch("src.domains.platform.routes.whatsapp.verify_webhook_signature", return_value=True)
def test_whatsapp_webhook_text_query(
    mock_verify_signature,
    mock_process_inbound,
    mock_send,
    client,
    db_session,
):
    mock_process_inbound.return_value = {
        "response_type": "text",
        "response_text": (
            "Photosynthesis is the process by which plants make food.\n\n"
            "Source: Science Textbook"
        ),
    }
    mock_send.return_value = {"success": True}

    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "919876543210",
                        "id": "wamid.query-123",
                        "type": "text",
                        "text": {"body": "biochem query"},
                    }]
                }
            }]
        }]
    }

    response = client.post("/api/whatsapp/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    mock_verify_signature.assert_called_once()
    mock_process_inbound.assert_awaited_once()
    mock_send.assert_awaited_once_with(
        "919876543210",
        "Photosynthesis is the process by which plants make food.\n\nSource: Science Textbook",
    )


@patch("src.domains.platform.routes.whatsapp.send_text_message", new_callable=AsyncMock)
@patch("src.domains.platform.routes.whatsapp.process_inbound_message", new_callable=AsyncMock)
@patch("src.domains.platform.routes.whatsapp.verify_webhook_signature", return_value=True)
def test_whatsapp_webhook_study_tool(
    mock_verify_signature,
    mock_process_inbound,
    mock_send,
    client,
    db_session,
):
    mock_process_inbound.return_value = {
        "response_type": "text",
        "response_text": "1. What is life?\nA. A\nB. B\nC. C",
    }
    mock_send.return_value = {"success": True}

    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "919876543211",
                        "id": "wamid.quiz-123",
                        "type": "text",
                        "text": {"body": "make a quiz"},
                    }]
                }
            }]
        }]
    }

    response = client.post("/api/whatsapp/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    mock_verify_signature.assert_called_once()
    mock_process_inbound.assert_awaited_once()
    mock_send.assert_awaited_once_with("919876543211", "1. What is life?\nA. A\nB. B\nC. C")


def test_whatsapp_webhook_verification(client):
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "valid_token",
        "hub.challenge": "12345",
    }
    with patch("src.domains.platform.routes.whatsapp.WHATSAPP_VERIFY_TOKEN", "valid_token"):
        response = client.get("/api/whatsapp/webhook", params=params)
        assert response.status_code == 200
        assert response.json() == 12345
