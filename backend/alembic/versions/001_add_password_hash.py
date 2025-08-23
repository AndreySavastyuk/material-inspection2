"""Add password_hash field to users table

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле password_hash в таблицу users (не nullable, с временным значением)
    op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=False, 
                                   server_default='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lkra0temp'))


def downgrade() -> None:
    op.drop_column('users', 'password_hash')