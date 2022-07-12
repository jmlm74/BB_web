"""empty message

Revision ID: edc64b66f76d
Revises: 5e581574af16
Create Date: 2022-06-28 09:41:06.262419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'edc64b66f76d'
down_revision = '5e581574af16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('repo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('repo_name', sa.String(length=180), nullable=False),
    sa.Column('repo_passphrase', sa.String(length=50), nullable=True),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_on', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('repo_name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('repo')
    # ### end Alembic commands ###