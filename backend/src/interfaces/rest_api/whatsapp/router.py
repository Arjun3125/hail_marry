"""WhatsApp routing and webhook handler for Twilio API."""
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Optional
from database import get_db
from sqlalchemy.orm import Session
from src.domains.identity.models.user import User
from src.domains.identity.models.tenant import Tenant
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

def get_or_create_whatsapp_user(phone: str, db: Session) -> User:
    """Gets existing user by phone, or auto-creates them."""
    user = db.query(User).filter(User.phone_number == phone, User.whatsapp_linked == True).first()
    if user:
        return user
    
    # Needs a default tenant for external signups
    tenant = db.query(Tenant).first()
    if not tenant:
        raise HTTPException(status_code=500, detail="System not initialized with a tenant.")

    # Create temporary email for auto-signup
    temp_email = f"wa_{phone.replace('+', '')}@vidyaos.whatsapp.local"
    
    user = User(
        tenant_id=tenant.id,
        email=temp_email,
        full_name="WhatsApp Student",
        role="student",
        phone_number=phone,
        whatsapp_linked=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def process_whatsapp_message(
    user: User, 
    body: str, 
    media_url: Optional[str], 
    db: Session
):
    """Passes message to AI Gateway."""
    from src.interfaces.rest_api.whatsapp.agent import handle_whatsapp_intent
    from twilio.rest import Client
    from config import settings
    
    try:
        # Route query to agent
        response_text = await handle_whatsapp_intent(user, body, media_url, db)
        
        # Send reply back via Twilio
        if getattr(settings, "TWILIO_ACCOUNT_SID", None) and getattr(settings, "TWILIO_AUTH_TOKEN", None):
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                body=response_text,
                to=user.phone_number
            )
        else:
            logger.warning(f"Mock WhatsApp Send to {user.phone_number}: {response_text}")
            
    except Exception as e:
        logger.error(f"WhatsApp processing error: {e}")
        # Could send error reply to user here


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Twilio Webhook endpoint for WhatsApp.
    Expects application/x-www-form-urlencoded
    """
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "")
        body = form_data.get("Body", "").strip()
        num_media = int(form_data.get("NumMedia", 0))
        media_url = form_data.get("MediaUrl0") if num_media > 0 else None

        if not from_number.startswith("whatsapp:"):
            logger.warning(f"Invalid WhatsApp sender format: {from_number}")
            return PlainTextResponse("OK")

        # Strip 'whatsapp:' prefix
        phone = from_number.replace("whatsapp:", "")
        
        # Get DB Session manually since it's a webhook
        db_gen = get_db()
        db = next(db_gen)

        user = get_or_create_whatsapp_user(phone, db)

        # Offload AI orchestration to background task to avoid Twilio 15-second timeout
        background_tasks.add_task(process_whatsapp_message, user, body, media_url, db)

        return PlainTextResponse("OK")
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
        return PlainTextResponse("OK", status_code=200) # Always return 200 to Twilio
