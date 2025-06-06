"""add role, is_deleted, blocked_at fields

Revision ID: 96fa7ea6e3d1
Revises: 422fdcb18e36
Create Date: 2025-05-12 07:47:43.626153

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96fa7ea6e3d1'
down_revision: Union[str, None] = '422fdcb18e36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # Создаём ENUM-тип до использования
    user_role_enum = postgresql.ENUM('admin', 'user', name='user_role_enum')
    user_role_enum.create(op.get_bind())

    op.add_column('users', sa.Column('blocked_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('users', sa.Column('role', sa.Enum('admin', 'user', name='user_role_enum'), nullable=False, server_default='user'))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'role')
    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'blocked_at')

    # Удаляем ENUM-тип после удаления поля
    user_role_enum = postgresql.ENUM('admin', 'user', name='user_role_enum')
    user_role_enum.drop(op.get_bind())
    # ### end Alembic commands ###
