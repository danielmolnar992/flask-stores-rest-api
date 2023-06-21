"""empty message

Revision ID: d56d673c6e39
Revises: 19d3b12c676b
Create Date: 2023-03-06 10:29:17.542614

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd56d673c6e39'
down_revision = '19d3b12c676b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(), nullable=False))
        batch_op.create_unique_constraint('email_costr', ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('email_costr', type_='unique')
        batch_op.drop_column('email')

    # ### end Alembic commands ###
