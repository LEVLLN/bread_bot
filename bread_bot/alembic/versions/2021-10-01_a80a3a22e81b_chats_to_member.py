"""chats_to_member

Revision ID: a80a3a22e81b
Revises: 54869121a43f
Create Date: 2021-10-01 21:06:52.319261

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a80a3a22e81b"
down_revision = "54869121a43f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "chats_to_members",
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=True),
        sa.Column("chat_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.alter_column("users", "is_admin", existing_type=sa.BOOLEAN(), nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("users", "is_admin", existing_type=sa.BOOLEAN(), nullable=True)
    op.drop_table("chats_to_members")
    # ### end Alembic commands ###
