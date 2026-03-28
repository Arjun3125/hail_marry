# WhatsApp Integration Migration: Twilio to Meta Cloud API

## Context
Initial implementation was built using the Twilio SDK for rapid prototyping. To eliminate third-party server dependencies and associated costs, the next phase involves migrating to the **Official Meta WhatsApp Cloud API**. This provides 1,000 free service-initiated conversations per month.

## Planned Changes

### 1. Removing Twilio Sub-system
- Uninstall `twilio` Python package.
- Clean up `backend/config.py` by removing `TwilioSettings`.
- Update `backend/src/interfaces/rest_api/whatsapp/router.py` to stop using Twilio-specific logic (form-encoded data).

### 2. Implementing Meta Webhook Handshake
- **GET Verification:** Implement the `hub.verify_token` challenge in the webhook route. This is required by Meta to activate the webhook.
- **POST JSON Parsing:** Meta sends data as a nested JSON structure. We will need to update the router to parse `entry[0].changes[0].value.messages[0]` and `entry[0].changes[0].value.contacts[0].wa_id`.

### 3. Native REST Delivery (Zero-Dependency)
- Use `httpx.post` to communicate directly with `https://graph.facebook.com/v18.0/{phone_number_id}/messages`.
- Build the JSON message payloads (Text, Interactive buttons, etc.) manually from scratch.

### 4. Meta Media Retrieval
- For file/image uploads (Phase 6), we must fetch the Media URL from Meta using the `media_id`, then download the binary content using the Bearer access token.

## Implementation Steps
1. **Meta App Setup:** Configure Meta Developer account and get `ACCESS_TOKEN` and `PHONE_NUMBER_ID`.
2. **Webhook Update:** Deploy the verification challenge code.
3. **Agent Logic Update:** Switch from Twilio SDK to native REST calls in `agent.py`.
4. **Testing:** Simulate Meta webhooks locally and verify RAG functionality via WhatsApp.

---
*Created by Antigravity AI - Status: Infrastructure Ready for Migration*
