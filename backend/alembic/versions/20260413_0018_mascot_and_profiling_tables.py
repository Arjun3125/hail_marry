"""Add mascot and profiling tables for personalized AI companion system.

Revision ID: 20260413_0018
Revises: 20260412_0017
Create Date: 2026-04-13

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


revision = "20260413_0018"
down_revision = "20260412_0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create mascot and profiling tables."""
    # student_mascot_memory
    op.create_table(
        "student_mascot_memory",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("student_id", UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("total_interactions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_interaction_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_summary", sa.Text(), nullable=True),
        sa.Column("last_emotional_state", sa.String(20), nullable=True),
        sa.Column("preferred_explanation_style", sa.String(50), nullable=True),
        sa.Column("mascot_tone_setting", sa.String(50), nullable=True, server_default="'encouraging'"),
        sa.Column("context_snapshot", JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("student_id", "tenant_id", name="uq_student_mascot_memory_student_tenant"),
    )

    # student_personality_profiles
    op.create_table(
        "student_personality_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("student_id", UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("learning_style_detected", sa.String(50), nullable=True),
        sa.Column("learning_style_stated", sa.String(50), nullable=True),
        sa.Column("reasoning_type", sa.String(50), nullable=True),
        sa.Column("primary_motivation_driver", sa.String(50), nullable=True),
        sa.Column("stress_threshold", sa.Float(), nullable=True),
        sa.Column("self_esteem_score", sa.Float(), nullable=True),
        sa.Column("resilience_score", sa.Float(), nullable=True),
        sa.Column("humor_index", sa.Float(), nullable=True),
        sa.Column("social_orientation", sa.String(50), nullable=True),
        sa.Column("locus_of_control", sa.String(50), nullable=True),
        sa.Column("mindset_orientation", sa.String(50), nullable=True),
        sa.Column("peak_study_hour", sa.Integer(), nullable=True),
        sa.Column("help_seeking_style", sa.String(50), nullable=True),
        sa.Column("career_aspiration_text", sa.Text(), nullable=True),
        sa.Column("interest_tags", sa.ARRAY(sa.String(100)), nullable=True),
        sa.Column("parental_pressure_level", sa.String(20), nullable=True),
        sa.Column("profile_completeness_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("profile_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("student_id", "tenant_id", name="uq_student_personality_profiles_student_tenant"),
    )

    # profile_signals
    op.create_table(
        "profile_signals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("student_id", UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("signal_type", sa.String(100), nullable=False),
        sa.Column("signal_value", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("extraction_method", sa.String(50), nullable=False),
        sa.Column("extraction_channel", sa.String(50), nullable=False),
        sa.Column("promoted_to_profile", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # mascot_conversation_turns
    op.create_table(
        "mascot_conversation_turns",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("student_id", UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", UUID(as_uuid=True), nullable=False),
        sa.Column("turn_number", sa.Integer(), nullable=False),
        sa.Column("student_message", sa.Text(), nullable=True),
        sa.Column("mascot_response", sa.Text(), nullable=True),
        sa.Column("emotional_state", sa.String(20), nullable=True),
        sa.Column("elicitation_question_key", sa.String(100), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # elicitation_log
    op.create_table(
        "elicitation_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("student_id", UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("question_key", sa.String(100), nullable=False),
        sa.Column("asked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("response_text", sa.Text(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("skipped_count", sa.Integer(), nullable=False, server_default="0"),
    )

    # Indexes
    op.create_index("ix_student_mascot_memory_student_id", "student_mascot_memory", ["student_id"])
    op.create_index("ix_student_mascot_memory_tenant_id", "student_mascot_memory", ["tenant_id"])
    op.create_index("ix_student_personality_profiles_student_id", "student_personality_profiles", ["student_id"])
    op.create_index("ix_student_personality_profiles_tenant_id", "student_personality_profiles", ["tenant_id"])
    op.create_index("ix_profile_signals_student_id", "profile_signals", ["student_id"])
    op.create_index("ix_profile_signals_tenant_id", "profile_signals", ["tenant_id"])
    op.create_index("ix_profile_signals_signal_type", "profile_signals", ["signal_type"])
    op.create_index("ix_profile_signals_promoted", "profile_signals", ["promoted_to_profile"])
    op.create_index("ix_mascot_conversation_turns_student_id", "mascot_conversation_turns", ["student_id"])
    op.create_index("ix_mascot_conversation_turns_tenant_id", "mascot_conversation_turns", ["tenant_id"])
    op.create_index("ix_mascot_conversation_turns_session_id", "mascot_conversation_turns", ["session_id"])
    op.create_index("ix_mascot_conversation_turns_created_at", "mascot_conversation_turns", ["created_at"])
    op.create_index("ix_elicitation_log_student_id", "elicitation_log", ["student_id"])
    op.create_index("ix_elicitation_log_tenant_id", "elicitation_log", ["tenant_id"])
    op.create_index("ix_elicitation_log_question_key", "elicitation_log", ["question_key"])


def downgrade() -> None:
    """Drop mascot and profiling tables."""
    op.drop_index("ix_elicitation_log_question_key", "elicitation_log")
    op.drop_index("ix_elicitation_log_tenant_id", "elicitation_log")
    op.drop_index("ix_elicitation_log_student_id", "elicitation_log")
    op.drop_index("ix_mascot_conversation_turns_created_at", "mascot_conversation_turns")
    op.drop_index("ix_mascot_conversation_turns_session_id", "mascot_conversation_turns")
    op.drop_index("ix_mascot_conversation_turns_tenant_id", "mascot_conversation_turns")
    op.drop_index("ix_mascot_conversation_turns_student_id", "mascot_conversation_turns")
    op.drop_index("ix_profile_signals_promoted", "profile_signals")
    op.drop_index("ix_profile_signals_signal_type", "profile_signals")
    op.drop_index("ix_profile_signals_tenant_id", "profile_signals")
    op.drop_index("ix_profile_signals_student_id", "profile_signals")
    op.drop_index("ix_student_personality_profiles_tenant_id", "student_personality_profiles")
    op.drop_index("ix_student_personality_profiles_student_id", "student_personality_profiles")
    op.drop_index("ix_student_mascot_memory_tenant_id", "student_mascot_memory")
    op.drop_index("ix_student_mascot_memory_student_id", "student_mascot_memory")

    op.drop_table("elicitation_log")
    op.drop_table("mascot_conversation_turns")
    op.drop_table("profile_signals")
    op.drop_table("student_personality_profiles")
    op.drop_table("student_mascot_memory")