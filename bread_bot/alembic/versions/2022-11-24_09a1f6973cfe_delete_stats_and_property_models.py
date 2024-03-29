"""Delete stats and property models

Revision ID: 09a1f6973cfe
Revises: 02e91180226d
Create Date: 2022-11-24 03:17:50.846316

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "09a1f6973cfe"
down_revision = "02e91180226d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("stats")
    op.drop_table("properties")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "properties",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("slug", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("data", postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="properties_pkey"),
    )
    op.create_table(
        "stats",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("member_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("slug", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("count", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("chat_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.chat_id"], name="stats_chat_id_fkey", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], name="stats_member_id_fkey", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="stats_pkey"),
    )
    # ### end Alembic commands ###
