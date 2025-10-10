"""baseline after manual schema changes

Revision ID: e62de38aa3eb
Revises: 48f5c2f63db4
Create Date: 2025-10-10 21:42:49.579818

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e62de38aa3eb'
down_revision: Union[str, None] = '48f5c2f63db4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
