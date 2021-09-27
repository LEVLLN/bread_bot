"""cascade delete

Revision ID: 89a2d8aa7a11
Revises: 62c624a5b92e
Create Date: 2021-09-27 10:48:48.721769

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '89a2d8aa7a11'
down_revision = '62c624a5b92e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('local_memes_chat_id_fkey', 'local_memes',
                       type_='foreignkey')
    op.create_foreign_key(None, 'local_memes', 'chats', ['chat_id'],
                          ['chat_id'], ondelete='CASCADE')
    op.drop_constraint('stats_chat_id_fkey', 'stats', type_='foreignkey')
    op.create_foreign_key(None, 'stats', 'chats', ['chat_id'], ['chat_id'],
                          ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    pass
    # ### end Alembic commands ###