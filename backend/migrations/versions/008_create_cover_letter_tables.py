"""Create cover letter tables

Revision ID: 008
Revises: 007
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create cover letter tables"""
    # Create cover_letters table
    op.create_table(
        'cover_letters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_draft', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('custom_edits', sa.Text(), nullable=True),
        sa.Column('ai_model', sa.String(50), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'job_id', 'version_number', name='uq_user_job_version'),
    )
    op.create_index(op.f('ix_cover_letters_id'), 'cover_letters', ['id'], unique=True)
    op.create_index(op.f('ix_cover_letters_user_id'), 'cover_letters', ['user_id'])
    op.create_index(op.f('ix_cover_letters_job_id'), 'cover_letters', ['job_id'])

    # Create letter_templates table
    op.create_table(
        'letter_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_letter_templates_id'), 'letter_templates', ['id'], unique=True)
    op.create_index(op.f('ix_letter_templates_user_id'), 'letter_templates', ['user_id'])

    # Create letter_exports table
    op.create_table(
        'letter_exports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cover_letter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('format', sa.String(20), nullable=False),
        sa.Column('file_url', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('exported_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['cover_letter_id'], ['cover_letters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_letter_exports_id'), 'letter_exports', ['id'], unique=True)
    op.create_index(op.f('ix_letter_exports_cover_letter_id'), 'letter_exports', ['cover_letter_id'])


def downgrade() -> None:
    """Downgrade cover letter tables"""
    op.drop_index(op.f('ix_letter_exports_cover_letter_id'), table_name='letter_exports')
    op.drop_index(op.f('ix_letter_exports_id'), table_name='letter_exports')
    op.drop_table('letter_exports')

    op.drop_index(op.f('ix_letter_templates_user_id'), table_name='letter_templates')
    op.drop_index(op.f('ix_letter_templates_id'), table_name='letter_templates')
    op.drop_table('letter_templates')

    op.drop_index(op.f('ix_cover_letters_job_id'), table_name='cover_letters')
    op.drop_index(op.f('ix_cover_letters_user_id'), table_name='cover_letters')
    op.drop_index(op.f('ix_cover_letters_id'), table_name='cover_letters')
    op.drop_table('cover_letters')
