"""Create automation tables

Revision ID: 010
Revises: 009
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create automation tables"""
    # Create automation_jobs table
    op.create_table(
        'automation_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_url', sa.String(500), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('automation_type', sa.String(100), nullable=True),
        sa.Column('browser_type', sa.String(50), nullable=True, server_default='chrome'),
        sa.Column('headless', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('current_retry', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_automation_jobs_id'), 'automation_jobs', ['id'], unique=True)
    op.create_index(op.f('ix_automation_jobs_user_id'), 'automation_jobs', ['user_id'])
    op.create_index(op.f('ix_automation_jobs_status'), 'automation_jobs', ['status'])
    op.create_index(op.f('ix_automation_jobs_job_id'), 'automation_jobs', ['job_id'])

    # Create automation_steps table
    op.create_table(
        'automation_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('automation_job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(255), nullable=True),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('selector', sa.String(500), nullable=True),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('wait_time_ms', sa.Integer(), nullable=True),
        sa.Column('retry_on_fail', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['automation_job_id'], ['automation_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_automation_steps_id'), 'automation_steps', ['id'], unique=True)
    op.create_index(op.f('ix_automation_steps_automation_job_id'), 'automation_steps', ['automation_job_id'])

    # Create automation_logs table
    op.create_table(
        'automation_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('automation_job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('log_level', sa.String(20), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('screenshot_url', sa.String(500), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['automation_job_id'], ['automation_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_automation_logs_id'), 'automation_logs', ['id'], unique=True)
    op.create_index(op.f('ix_automation_logs_automation_job_id'), 'automation_logs', ['automation_job_id'])


def downgrade() -> None:
    """Downgrade automation tables"""
    op.drop_index(op.f('ix_automation_logs_automation_job_id'), table_name='automation_logs')
    op.drop_index(op.f('ix_automation_logs_id'), table_name='automation_logs')
    op.drop_table('automation_logs')

    op.drop_index(op.f('ix_automation_steps_automation_job_id'), table_name='automation_steps')
    op.drop_index(op.f('ix_automation_steps_id'), table_name='automation_steps')
    op.drop_table('automation_steps')

    op.drop_index(op.f('ix_automation_jobs_job_id'), table_name='automation_jobs')
    op.drop_index(op.f('ix_automation_jobs_status'), table_name='automation_jobs')
    op.drop_index(op.f('ix_automation_jobs_user_id'), table_name='automation_jobs')
    op.drop_index(op.f('ix_automation_jobs_id'), table_name='automation_jobs')
    op.drop_table('automation_jobs')
