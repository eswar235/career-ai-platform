"""Create user profile tables

Revision ID: 004
Revises: 003_create_parsed_resumes_table
Create Date: 2024-12-20 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "004"
down_revision = "003_create_parsed_resumes_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # User profiles table
    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("headline", sa.String(255), nullable=True),
        sa.Column("professional_summary", sa.Text(), nullable=True),
        sa.Column("profile_picture_url", sa.String(500), nullable=True),
        sa.Column("completion_percentage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("verified_by_user", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_from_resume_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_from_resume_id"], ["resumes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
    )
    op.create_index("ix_user_profiles_id", "user_profiles", ["id"])
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"])

    # Skills table
    op.create_table(
        "profile_skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("proficiency_level", sa.String(50), nullable=True),
        sa.Column("years_of_experience", sa.Integer(), nullable=True),
        sa.Column("endorsed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["user_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "skill_name", name="uq_profile_skills"),
    )
    op.create_index("ix_profile_skills_id", "profile_skills", ["id"])
    op.create_index("ix_profile_skills_profile_id", "profile_skills", ["profile_id"])

    # Work experience table
    op.create_table(
        "profile_experiences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("company_industry", sa.String(100), nullable=True),
        sa.Column("employment_type", sa.String(50), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("currently_working", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["user_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profile_experiences_id", "profile_experiences", ["id"])
    op.create_index("ix_profile_experiences_profile_id", "profile_experiences", ["profile_id"])

    # Education table
    op.create_table(
        "profile_education",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_name", sa.String(255), nullable=False),
        sa.Column("degree", sa.String(100), nullable=True),
        sa.Column("field_of_study", sa.String(100), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("grade", sa.String(10), nullable=True),
        sa.Column("activities_societies", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["user_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profile_education_id", "profile_education", ["id"])
    op.create_index("ix_profile_education_profile_id", "profile_education", ["profile_id"])

    # Projects table
    op.create_table(
        "profile_projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("skills_used", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("project_url", sa.String(500), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["user_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profile_projects_id", "profile_projects", ["id"])
    op.create_index("ix_profile_projects_profile_id", "profile_projects", ["profile_id"])

    # Certifications table
    op.create_table(
        "profile_certifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("certification_name", sa.String(255), nullable=False),
        sa.Column("issuing_organization", sa.String(255), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.Column("expiration_date", sa.Date(), nullable=True),
        sa.Column("credential_id", sa.String(255), nullable=True),
        sa.Column("credential_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["user_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profile_certifications_id", "profile_certifications", ["id"])
    op.create_index("ix_profile_certifications_profile_id", "profile_certifications", ["profile_id"])

    # Profile versions table
    op.create_table(
        "profile_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("data", postgresql.JSON(), nullable=True),
        sa.Column("changed_fields", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("change_reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["user_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "version_number", name="uq_profile_versions"),
    )
    op.create_index("ix_profile_versions_id", "profile_versions", ["id"])
    op.create_index("ix_profile_versions_profile_id", "profile_versions", ["profile_id"])

    # Profile completion tracking
    op.create_table(
        "profile_completion_tracking",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("personal_info_complete", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("skills_added", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("experience_added", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("education_added", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("projects_added", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("certifications_added", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("profile_picture_added", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("professional_summary_added", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_updated", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["user_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", name="uq_profile_completion_tracking"),
    )
    op.create_index("ix_profile_completion_tracking_id", "profile_completion_tracking", ["id"])


def downgrade() -> None:
    op.drop_index("ix_profile_completion_tracking_id", table_name="profile_completion_tracking")
    op.drop_table("profile_completion_tracking")
    
    op.drop_index("ix_profile_versions_profile_id", table_name="profile_versions")
    op.drop_index("ix_profile_versions_id", table_name="profile_versions")
    op.drop_table("profile_versions")
    
    op.drop_index("ix_profile_certifications_profile_id", table_name="profile_certifications")
    op.drop_index("ix_profile_certifications_id", table_name="profile_certifications")
    op.drop_table("profile_certifications")
    
    op.drop_index("ix_profile_projects_profile_id", table_name="profile_projects")
    op.drop_index("ix_profile_projects_id", table_name="profile_projects")
    op.drop_table("profile_projects")
    
    op.drop_index("ix_profile_education_profile_id", table_name="profile_education")
    op.drop_index("ix_profile_education_id", table_name="profile_education")
    op.drop_table("profile_education")
    
    op.drop_index("ix_profile_experiences_profile_id", table_name="profile_experiences")
    op.drop_index("ix_profile_experiences_id", table_name="profile_experiences")
    op.drop_table("profile_experiences")
    
    op.drop_index("ix_profile_skills_profile_id", table_name="profile_skills")
    op.drop_index("ix_profile_skills_id", table_name="profile_skills")
    op.drop_table("profile_skills")
    
    op.drop_index("ix_user_profiles_user_id", table_name="user_profiles")
    op.drop_index("ix_user_profiles_id", table_name="user_profiles")
    op.drop_table("user_profiles")
