"""Create Post Table

Revision ID: 2a4f5dac1e9d
Revises: 
Create Date: 2022-01-28 22:13:49.580193

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a4f5dac1e9d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
    )

    pass


def downgrade():
    op.drop_table("posts")
    pass
