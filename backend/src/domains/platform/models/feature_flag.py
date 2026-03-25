from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class FeatureFlag(Base):
    """
    FeatureFlag model represents a toggleable system feature.
    Centralized point for enabling/disabling whole platform capabilities.
    """
    __tablename__ = "feature_flags"

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=False)  # "AI" or "Non-AI"
    module = Column(String, nullable=True, default="Platform Operations")
    ai_intensity = Column(String, nullable=True, default="No AI")
    enabled = Column(Boolean, default=True, nullable=False)
