"""VidyaOS backend FastAPI application entry point."""
from src.bootstrap.app_factory import create_app

app = create_app()
