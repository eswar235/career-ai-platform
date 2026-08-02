"""Create job matching and embeddings tables

Revision ID: 006
Revises: 005
Create Date: 2024-12-20 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create pgvector extension if not exists
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Resume embeddings table
    op.create_table(
        "resume_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", postgresql.UUID(as_uuid=True), nullable=True),  # Will store as JSON for compatibility
        sa.Column("skills_extracted", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("experience_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_resume_embeddings_user_id"),
    )
    op.create_index("ix_resume_embeddings_id", "resume_embeddings", ["id"])
    op.create_index("ix_resume_embeddings_user_id", "resume_embeddings", ["user_id"])

    # Job embeddings table
    op.create_table(
        "job_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", postgresql.UUID(as_uuid=True), nullable=True),  # Will store as JSON for compatibility
        sa.Column("skills_required_normalized", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", name="uq_job_embeddings_job_id"),
    )
    op.create_index("ix_job_embeddings_id", "job_embeddings", ["id"])
    op.create_index("ix_job_embeddings_job_id", "job_embeddings", ["job_id"])

    # Job matches table
    op.create_table(
        "job_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("match_percentage", sa.Integer(), nullable=False),
        sa.Column("match_score", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("skills_match", sa.Integer(), nullable=True),
        sa.Column("skills_missing", sa.Integer(), nullable=True),
        sa.Column("strengths", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("gaps", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("recommendations", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_job_matches"),
    )
    op.create_index("ix_job_matches_id", "job_matches", ["id"])
    op.create_index("ix_job_matches_user_id", "job_matches", ["user_id"])
    op.create_index("ix_job_matches_job_id", "job_matches", ["job_id"])
    op.create_index("ix_job_matches_percentage", "job_matches", ["match_percentage"])


def downgrade() -> None:
    op.drop_index("ix_job_matches_percentage", table_name="job_matches")
    op.drop_index("ix_job_matches_job_id", table_name="job_matches")
    op.drop_index("ix_job_matches_user_id", table_name="job_matches")
    op.drop_index("ix_job_matches_id", table_name="job_matches")
    op.drop_table("job_matches")

    op.drop_index("ix_job_embeddings_job_id", table_name="job_embeddings")
    op.drop_index("ix_job_embeddings_id", table_name="job_embeddings")
    op.drop_table("job_embeddings")

    op.drop_index("ix_resume_embeddings_user_id", table_name="resume_embeddings")
    op.drop_index("ix_resume_embeddings_id", table_name="resume_embeddings")
    op.drop_table("resume_embeddings")
