"""phase 1 core platform contracts

Revision ID: 20260406_0015
Revises: 20260331_0014
Create Date: 2026-04-06

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "20260406_0015"
down_revision = "20260331_0014"
branch_labels = None
depends_on = None


def _column_names(inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def _unique_names(inspector, table_name: str) -> set[str]:
    return {constraint["name"] for constraint in inspector.get_unique_constraints(table_name)}


def _check_names(inspector, table_name: str) -> set[str]:
    try:
        return {constraint["name"] for constraint in inspector.get_check_constraints(table_name)}
    except NotImplementedError:
        return set()


def _create_student_profiles_table(dialect: str) -> None:
    json_type = sa.JSON().with_variant(sa.dialects.postgresql.JSONB(astext_type=sa.Text()), "postgresql")

    op.create_table(
        "student_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("current_class_id", UUID(as_uuid=True), nullable=True),
        sa.Column("current_batch_id", UUID(as_uuid=True), nullable=True),
        sa.Column("primary_parent_id", UUID(as_uuid=True), nullable=True),
        sa.Column("guardian_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("present_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attendance_pct", sa.Float(), nullable=False, server_default="0"),
        sa.Column("absent_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overall_score_pct", sa.Float(), nullable=True),
        sa.Column("strongest_subject", sa.String(length=100), nullable=True),
        sa.Column("weakest_subject", sa.String(length=100), nullable=True),
        sa.Column("subject_mastery_map", json_type, nullable=True),
        sa.Column("current_streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_reviews_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dropout_risk", sa.String(length=20), nullable=False, server_default="low"),
        sa.Column("academic_risk", sa.String(length=20), nullable=False, server_default="low"),
        sa.Column("fee_risk", sa.String(length=20), nullable=False, server_default="low"),
        sa.Column("exam_readiness_pct", sa.Float(), nullable=True),
        sa.Column("predicted_score", sa.Float(), nullable=True),
        sa.Column("last_computed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_student_profiles_tenant_id", "student_profiles", ["tenant_id"])
    op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"])
    op.create_index("ix_student_profiles_current_class_id", "student_profiles", ["current_class_id"])
    op.create_index("ix_student_profiles_current_batch_id", "student_profiles", ["current_batch_id"])
    op.create_index("ix_student_profiles_primary_parent_id", "student_profiles", ["primary_parent_id"])

    if dialect == "postgresql":
        op.create_foreign_key(
            "fk_student_profiles_tenant",
            "student_profiles",
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_foreign_key(
            "fk_student_profiles_user",
            "student_profiles",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_foreign_key(
            "fk_student_profiles_current_class",
            "student_profiles",
            "classes",
            ["current_class_id"],
            ["id"],
        )
        op.create_foreign_key(
            "fk_student_profiles_current_batch",
            "student_profiles",
            "batches",
            ["current_batch_id"],
            ["id"],
        )
        op.create_foreign_key(
            "fk_student_profiles_primary_parent",
            "student_profiles",
            "users",
            ["primary_parent_id"],
            ["id"],
        )
        for column_name in (
            "guardian_count",
            "total_days",
            "present_days",
            "attendance_pct",
            "absent_streak",
            "current_streak_days",
            "longest_streak_days",
            "total_reviews_completed",
            "dropout_risk",
            "academic_risk",
            "fee_risk",
        ):
            op.execute(f"ALTER TABLE student_profiles ALTER COLUMN {column_name} DROP DEFAULT")


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    table_names = set(inspector.get_table_names())
    dialect = conn.dialect.name

    if "student_profiles" not in table_names:
        _create_student_profiles_table(dialect)
    else:
        student_profile_columns = _column_names(inspector, "student_profiles")
        student_profile_indexes = _index_names(inspector, "student_profiles")
        if "current_class_id" not in student_profile_columns:
            op.add_column("student_profiles", sa.Column("current_class_id", UUID(as_uuid=True), nullable=True))
        if "current_batch_id" not in student_profile_columns:
            op.add_column("student_profiles", sa.Column("current_batch_id", UUID(as_uuid=True), nullable=True))
        if "primary_parent_id" not in student_profile_columns:
            op.add_column("student_profiles", sa.Column("primary_parent_id", UUID(as_uuid=True), nullable=True))
        if "guardian_count" not in student_profile_columns:
            op.add_column(
                "student_profiles",
                sa.Column("guardian_count", sa.Integer(), nullable=False, server_default="0"),
            )
        if "ix_student_profiles_current_class_id" not in student_profile_indexes:
            op.create_index("ix_student_profiles_current_class_id", "student_profiles", ["current_class_id"])
        if "ix_student_profiles_current_batch_id" not in student_profile_indexes:
            op.create_index("ix_student_profiles_current_batch_id", "student_profiles", ["current_batch_id"])
        if "ix_student_profiles_primary_parent_id" not in student_profile_indexes:
            op.create_index("ix_student_profiles_primary_parent_id", "student_profiles", ["primary_parent_id"])
        if dialect == "postgresql":
            op.execute(
                "ALTER TABLE student_profiles "
                "ALTER COLUMN guardian_count DROP DEFAULT"
            )

    if "parent_links" in table_names:
        unique_names = _unique_names(inspector, "parent_links")
        if "uq_parent_link_tenant_parent_child" not in unique_names:
            with op.batch_alter_table("parent_links") as batch_op:
                batch_op.create_unique_constraint(
                    "uq_parent_link_tenant_parent_child",
                    ["tenant_id", "parent_id", "child_id"],
                )

    if "enrollments" in table_names:
        unique_names = _unique_names(inspector, "enrollments")
        if "uq_enrollment_tenant_student_class_year" not in unique_names:
            with op.batch_alter_table("enrollments") as batch_op:
                batch_op.create_unique_constraint(
                    "uq_enrollment_tenant_student_class_year",
                    ["tenant_id", "student_id", "class_id", "academic_year"],
                )

    if "batch_enrollments" in table_names:
        unique_names = _unique_names(inspector, "batch_enrollments")
        if "uq_batch_enrollment_tenant_batch_student" not in unique_names:
            with op.batch_alter_table("batch_enrollments") as batch_op:
                batch_op.create_unique_constraint(
                    "uq_batch_enrollment_tenant_batch_student",
                    ["tenant_id", "batch_id", "student_id"],
                )

    if "fee_structures" in table_names:
        check_names = _check_names(inspector, "fee_structures")
        if "ck_fee_structure_amount_non_negative" not in check_names:
            with op.batch_alter_table("fee_structures") as batch_op:
                batch_op.create_check_constraint(
                    "ck_fee_structure_amount_non_negative",
                    "amount >= 0",
                )

    if "fee_invoices" in table_names:
        unique_names = _unique_names(inspector, "fee_invoices")
        check_names = _check_names(inspector, "fee_invoices")
        with op.batch_alter_table("fee_invoices") as batch_op:
            if "uq_fee_invoice_tenant_student_structure_due_date" not in unique_names:
                batch_op.create_unique_constraint(
                    "uq_fee_invoice_tenant_student_structure_due_date",
                    ["tenant_id", "student_id", "fee_structure_id", "due_date"],
                )
            if "ck_fee_invoice_amount_due_non_negative" not in check_names:
                batch_op.create_check_constraint(
                    "ck_fee_invoice_amount_due_non_negative",
                    "amount_due >= 0",
                )
            if "ck_fee_invoice_amount_paid_non_negative" not in check_names:
                batch_op.create_check_constraint(
                    "ck_fee_invoice_amount_paid_non_negative",
                    "amount_paid >= 0",
                )

    if "fee_payments" in table_names:
        check_names = _check_names(inspector, "fee_payments")
        if "ck_fee_payment_amount_positive" not in check_names:
            with op.batch_alter_table("fee_payments") as batch_op:
                batch_op.create_check_constraint(
                    "ck_fee_payment_amount_positive",
                    "amount > 0",
                )

    if "test_series" in table_names:
        test_series_columns = _column_names(inspector, "test_series")
        test_series_checks = _check_names(inspector, "test_series")
        if "assessment_kind" not in test_series_columns:
            op.add_column(
                "test_series",
                sa.Column("assessment_kind", sa.String(length=30), nullable=False, server_default="mock_test"),
            )
        if "grading_mode" not in test_series_columns:
            op.add_column(
                "test_series",
                sa.Column("grading_mode", sa.String(length=30), nullable=False, server_default="manual_review"),
            )
        if "status" not in test_series_columns:
            op.add_column(
                "test_series",
                sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
            )
        if "opens_at" not in test_series_columns:
            op.add_column("test_series", sa.Column("opens_at", sa.DateTime(timezone=True), nullable=True))
        if "closes_at" not in test_series_columns:
            op.add_column("test_series", sa.Column("closes_at", sa.DateTime(timezone=True), nullable=True))
        if "published_at" not in test_series_columns:
            op.add_column("test_series", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
        with op.batch_alter_table("test_series") as batch_op:
            if "ck_test_series_total_marks_positive" not in test_series_checks:
                batch_op.create_check_constraint(
                    "ck_test_series_total_marks_positive",
                    "total_marks > 0",
                )
            if "ck_test_series_duration_minutes_positive" not in test_series_checks:
                batch_op.create_check_constraint(
                    "ck_test_series_duration_minutes_positive",
                    "duration_minutes > 0",
                )
        if dialect == "postgresql":
            for column_name in ("assessment_kind", "grading_mode", "status"):
                op.execute(f"ALTER TABLE test_series ALTER COLUMN {column_name} DROP DEFAULT")


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    table_names = set(inspector.get_table_names())
    dialect = conn.dialect.name

    if "test_series" in table_names:
        test_series_columns = _column_names(inspector, "test_series")
        test_series_checks = _check_names(inspector, "test_series")
        with op.batch_alter_table("test_series") as batch_op:
            if "ck_test_series_duration_minutes_positive" in test_series_checks:
                batch_op.drop_constraint("ck_test_series_duration_minutes_positive", type_="check")
            if "ck_test_series_total_marks_positive" in test_series_checks:
                batch_op.drop_constraint("ck_test_series_total_marks_positive", type_="check")
        for column_name in ("published_at", "closes_at", "opens_at", "status", "grading_mode", "assessment_kind"):
            if column_name in test_series_columns:
                op.drop_column("test_series", column_name)

    if "fee_payments" in table_names:
        check_names = _check_names(inspector, "fee_payments")
        if "ck_fee_payment_amount_positive" in check_names:
            with op.batch_alter_table("fee_payments") as batch_op:
                batch_op.drop_constraint("ck_fee_payment_amount_positive", type_="check")

    if "fee_invoices" in table_names:
        unique_names = _unique_names(inspector, "fee_invoices")
        check_names = _check_names(inspector, "fee_invoices")
        with op.batch_alter_table("fee_invoices") as batch_op:
            if "ck_fee_invoice_amount_paid_non_negative" in check_names:
                batch_op.drop_constraint("ck_fee_invoice_amount_paid_non_negative", type_="check")
            if "ck_fee_invoice_amount_due_non_negative" in check_names:
                batch_op.drop_constraint("ck_fee_invoice_amount_due_non_negative", type_="check")
            if "uq_fee_invoice_tenant_student_structure_due_date" in unique_names:
                batch_op.drop_constraint("uq_fee_invoice_tenant_student_structure_due_date", type_="unique")

    if "fee_structures" in table_names:
        check_names = _check_names(inspector, "fee_structures")
        if "ck_fee_structure_amount_non_negative" in check_names:
            with op.batch_alter_table("fee_structures") as batch_op:
                batch_op.drop_constraint("ck_fee_structure_amount_non_negative", type_="check")

    if "batch_enrollments" in table_names:
        unique_names = _unique_names(inspector, "batch_enrollments")
        if "uq_batch_enrollment_tenant_batch_student" in unique_names:
            with op.batch_alter_table("batch_enrollments") as batch_op:
                batch_op.drop_constraint("uq_batch_enrollment_tenant_batch_student", type_="unique")

    if "enrollments" in table_names:
        unique_names = _unique_names(inspector, "enrollments")
        if "uq_enrollment_tenant_student_class_year" in unique_names:
            with op.batch_alter_table("enrollments") as batch_op:
                batch_op.drop_constraint("uq_enrollment_tenant_student_class_year", type_="unique")

    if "parent_links" in table_names:
        unique_names = _unique_names(inspector, "parent_links")
        if "uq_parent_link_tenant_parent_child" in unique_names:
            with op.batch_alter_table("parent_links") as batch_op:
                batch_op.drop_constraint("uq_parent_link_tenant_parent_child", type_="unique")

    if "student_profiles" in table_names:
        student_profile_columns = _column_names(inspector, "student_profiles")
        student_profile_indexes = _index_names(inspector, "student_profiles")
        if dialect == "postgresql":
            foreign_key_names = {fk["name"] for fk in inspector.get_foreign_keys("student_profiles")}
            for constraint_name in (
                "fk_student_profiles_primary_parent",
                "fk_student_profiles_current_batch",
                "fk_student_profiles_current_class",
                "fk_student_profiles_user",
                "fk_student_profiles_tenant",
            ):
                if constraint_name in foreign_key_names:
                    op.drop_constraint(constraint_name, "student_profiles", type_="foreignkey")
        if "ix_student_profiles_user_id" in student_profile_indexes:
            op.drop_index("ix_student_profiles_user_id", table_name="student_profiles")
        if "ix_student_profiles_tenant_id" in student_profile_indexes:
            op.drop_index("ix_student_profiles_tenant_id", table_name="student_profiles")
        if "ix_student_profiles_primary_parent_id" in student_profile_indexes:
            op.drop_index("ix_student_profiles_primary_parent_id", table_name="student_profiles")
        if "ix_student_profiles_current_batch_id" in student_profile_indexes:
            op.drop_index("ix_student_profiles_current_batch_id", table_name="student_profiles")
        if "ix_student_profiles_current_class_id" in student_profile_indexes:
            op.drop_index("ix_student_profiles_current_class_id", table_name="student_profiles")
        for column_name in ("guardian_count", "primary_parent_id", "current_batch_id", "current_class_id"):
            if column_name in student_profile_columns:
                op.drop_column("student_profiles", column_name)
