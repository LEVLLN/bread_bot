"""Delete other entities

Revision ID: zx2082b0765e
Revises: zfb25f1a876b
Create Date: 2022-12-20 14:19:07.025858

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "zx2082b0765e"
down_revision = "zfb25f1a876b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("voice_entities")
    op.drop_table("text_entities")
    op.drop_table("gif_entities")
    op.drop_table("sticker_entities")
    op.drop_table("photo_entities")
    op.drop_table("video_entities")
    op.drop_table("video_note_entities")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "video_note_entities",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("key", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("value", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "reaction_type",
            postgresql.ENUM("TRIGGER", "SUBSTRING", name="answerentitytypesenum"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("pack_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["pack_id"], ["answer_packs.id"], name="video_note_entities_pack_id_fkey", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="video_note_entities_pkey"),
    )
    op.create_table(
        "video_entities",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("key", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("value", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "reaction_type",
            postgresql.ENUM("TRIGGER", "SUBSTRING", name="answerentitytypesenum"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("pack_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["pack_id"], ["answer_packs.id"], name="video_entities_pack_id_fkey", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="video_entities_pkey"),
    )
    op.create_table(
        "photo_entities",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("key", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("value", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "reaction_type",
            postgresql.ENUM("TRIGGER", "SUBSTRING", name="answerentitytypesenum"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("pack_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("description", sa.TEXT(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["pack_id"], ["answer_packs.id"], name="photo_entities_pack_id_fkey", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="photo_entities_pkey"),
    )
    op.create_table(
        "sticker_entities",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("key", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("value", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "reaction_type",
            postgresql.ENUM("TRIGGER", "SUBSTRING", name="answerentitytypesenum"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("pack_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["pack_id"], ["answer_packs.id"], name="sticker_entities_pack_id_fkey", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="sticker_entities_pkey"),
    )
    op.create_table(
        "gif_entities",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("key", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("value", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "reaction_type",
            postgresql.ENUM("TRIGGER", "SUBSTRING", name="answerentitytypesenum"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("pack_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["pack_id"], ["answer_packs.id"], name="gif_entities_pack_id_fkey", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="gif_entities_pkey"),
    )
    op.create_table(
        "text_entities",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("key", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("value", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "reaction_type",
            postgresql.ENUM("TRIGGER", "SUBSTRING", name="answerentitytypesenum"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("pack_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["pack_id"], ["answer_packs.id"], name="text_entities_pack_id_fkey", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="text_entities_pkey"),
    )
    op.create_table(
        "voice_entities",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("key", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("value", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "reaction_type",
            postgresql.ENUM("TRIGGER", "SUBSTRING", name="answerentitytypesenum"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("pack_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["pack_id"], ["answer_packs.id"], name="voice_entities_pack_id_fkey", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="voice_entities_pkey"),
    )
    # ### end Alembic commands ###
