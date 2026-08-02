"""Create application tracker tables

Revision ID: 009
Revises: 008
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create application tracker tables"""
    # Create job_applications table
    op.create_table(
        'job_applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='applied'),
        sa.Column('application_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('applied_via', sa.String(100), nullable=True),
        sa.Column('cover_letter_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cover_letter_id'], ['cover_letters.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'job_id', name='uq_user_job_application'),
    )
    op.create_index(op.f('ix_job_applications_id'), 'job_applications', ['id'], unique=True)
    op.create_index(op.f('ix_job_applications_user_id'), 'job_applications', ['user_id'])
    op.create_index(op.f('ix_job_applications_job_id'), 'job_applications', ['job_id'])
    op.create_index(op.f('ix_job_applications_status'), 'job_applications', ['status'])

    # Create interviews table
    op.create_table(
        'interviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interview_type', sa.String(50), nullable=True),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('interviewer_name', sa.String(255), nullable=True),
        sa.Column('interviewer_email', sa.String(255), nullable=True),
        sa.Column('meeting_link', sa.String(500), nullable=True),
        sa.Column('preparation_notes', sa.Text(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('interview_score', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='scheduled'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['job_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interviews_id'), 'interviews', ['id'], unique=True)
    op.create_index(op.f('ix_interviews_application_id'), 'interviews', ['application_id'])
    op.create_index(op.f('ix_interviews_scheduled_date'), 'interviews', ['scheduled_date'])

    # Create application_activities table
    op.create_table(
        'application_activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('previous_status', sa.String(50), nullable=True),
        sa.Column('new_status', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['job_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_application_activities_id'), 'application_activities', ['id'], unique=True)
    op.create_index(op.f('ix_application_activities_application_id'), 'application_activities', ['application_id'])

    # Create job_offers table
    op.create_table(
        'job_offers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='received'),
        sa.Column('salary', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('bonus', sa.Integer(), nullable=True),
        sa.Column('benefits', sa.Text(), nullable=True),
        sa.Column('offer_letter_url', sa.String(500), nullable=True),
        sa.Column('offer_expiration_date', sa.Date(), nullable=True),
        sa.Column('negotiation_notes', sa.Text(), nullable=True),
        sa.Column('accepted_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['job_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('application_id', name='uq_application_offer'),
    )
    op.create_index(op.f('ix_job_offers_id'), 'job_offers', ['id'], unique=True)
    op.create_index(op.f('ix_job_offers_application_id'), 'job_offers', ['application_id'])


def downgrade() -> None:
    """Downgrade application tracker tables"""
    op.drop_index(op.f('ix_job_offers_application_id'), table_name='job_offers')
    op.drop_index(op.f('ix_job_offers_id'), table_name='job_offers')
    op.drop_table('job_offers')

    op.drop_index(op.f('ix_application_activities_application_id'), table_name='application_activities')
    op.drop_index(op.f('ix_application_activities_id'), table_name='application_activities')
    op.drop_table('application_activities')

    op.drop_index(op.f('ix_interviews_scheduled_date'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_application_id'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_id'), table_name='interviews')
    op.drop_table('interviews')

    op.drop_index(op.f('ix_job_applications_status'), table_name='job_applications')
    op.drop_index(op.f('ix_job_applications_job_id'), table_name='job_applications')
    op.drop_index(op.f('ix_job_applications_user_id'), table_name='job_applications')
    op.drop_index(op.f('ix_job_applications_id'), table_name='job_applications')
    op.drop_table('job_applications')
