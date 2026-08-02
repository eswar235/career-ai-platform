"""Create interview coaching tables

Revision ID: 011
Revises: 010
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create interview coaching tables"""
    # Create interview_sessions table
    op.create_table(
        'interview_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_type', sa.String(50), nullable=True),
        sa.Column('difficulty_level', sa.String(20), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('role', sa.String(100), nullable=True),
        sa.Column('total_questions', sa.Integer(), nullable=True),
        sa.Column('questions_answered', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('overall_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interview_sessions_id'), 'interview_sessions', ['id'], unique=True)
    op.create_index(op.f('ix_interview_sessions_user_id'), 'interview_sessions', ['user_id'])
    op.create_index(op.f('ix_interview_sessions_job_id'), 'interview_sessions', ['job_id'])

    # Create interview_questions table
    op.create_table(
        'interview_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(50), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('question_order', sa.Integer(), nullable=False),
        sa.Column('time_limit_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interview_questions_id'), 'interview_questions', ['id'], unique=True)
    op.create_index(op.f('ix_interview_questions_session_id'), 'interview_questions', ['session_id'])

    # Create interview_answers table
    op.create_table(
        'interview_answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_answer', sa.Text(), nullable=True),
        sa.Column('answer_time_seconds', sa.Integer(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('improvements', sa.Text(), nullable=True),
        sa.Column('ai_model', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['interview_questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interview_answers_id'), 'interview_answers', ['id'], unique=True)
    op.create_index(op.f('ix_interview_answers_question_id'), 'interview_answers', ['question_id'])

    # Create interview_tips table
    op.create_table(
        'interview_tips',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('tip_text', sa.Text(), nullable=False),
        sa.Column('tip_order', sa.Integer(), nullable=True),
        sa.Column('helpful_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interview_tips_id'), 'interview_tips', ['id'], unique=True)
    op.create_index(op.f('ix_interview_tips_user_id'), 'interview_tips', ['user_id'])

    # Create interview_metrics table
    op.create_table(
        'interview_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('average_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('total_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_questions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('strongest_category', sa.String(100), nullable=True),
        sa.Column('weakest_category', sa.String(100), nullable=True),
        sa.Column('improvement_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_metrics'),
    )
    op.create_index(op.f('ix_interview_metrics_id'), 'interview_metrics', ['id'], unique=True)
    op.create_index(op.f('ix_interview_metrics_user_id'), 'interview_metrics', ['user_id'])


def downgrade() -> None:
    """Downgrade interview coaching tables"""
    op.drop_index(op.f('ix_interview_metrics_user_id'), table_name='interview_metrics')
    op.drop_index(op.f('ix_interview_metrics_id'), table_name='interview_metrics')
    op.drop_table('interview_metrics')

    op.drop_index(op.f('ix_interview_tips_user_id'), table_name='interview_tips')
    op.drop_index(op.f('ix_interview_tips_id'), table_name='interview_tips')
    op.drop_table('interview_tips')

    op.drop_index(op.f('ix_interview_answers_question_id'), table_name='interview_answers')
    op.drop_index(op.f('ix_interview_answers_id'), table_name='interview_answers')
    op.drop_table('interview_answers')

    op.drop_index(op.f('ix_interview_questions_session_id'), table_name='interview_questions')
    op.drop_index(op.f('ix_interview_questions_id'), table_name='interview_questions')
    op.drop_table('interview_questions')

    op.drop_index(op.f('ix_interview_sessions_job_id'), table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_user_id'), table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_id'), table_name='interview_sessions')
    op.drop_table('interview_sessions')
