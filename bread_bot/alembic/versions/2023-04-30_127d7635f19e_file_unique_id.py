"""File unique_id

Revision ID: 127d7635f19e
Revises: 0fb0f6b627b2
Create Date: 2023-04-30 12:25:12.124190

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "127d7635f19e"
down_revision = "0fb0f6b627b2"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("answer_entities", sa.Column("file_unique_id", sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("answer_entities", "file_unique_id")
    # ### end Alembic commands ###