"""Property DB model

Revision ID: 107f6798265c
Revises: a80a3a22e81b
Create Date: 2021-10-02 05:22:10.817485

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '107f6798265c'
down_revision = 'a80a3a22e81b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('properties',
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('id', sa.Integer(), autoincrement=True,
                              nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('slug', sa.String(length=255), nullable=False),
                    sa.Column('data', sa.JSON(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('properties')
    # ### end Alembic commands ###
