"""relashionships

Revision ID: 04b40d8736ce
Revises: c08dcfc66564
Create Date: 2023-06-26 17:23:54.364112

"""
import sqlalchemy as sa
from alembic import op
from database import SubjectType
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '04b40d8736ce'
down_revision = 'c08dcfc66564'
branch_labels = None
depends_on = None


def upgrade() -> None:
    subject_type = postgresql.ENUM(SubjectType, name="subject_type")
    subject_type.create(op.get_bind(), checkfirst=True)
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('completed_practices', sa.Column('number_practice', sa.Integer(), nullable=True))
    op.drop_constraint('completed_practices_subject_id_fkey', 'completed_practices', type_='foreignkey')
    op.drop_constraint('completed_practices_user_id_fkey', 'completed_practices', type_='foreignkey')
    op.create_foreign_key(None, 'completed_practices', 'subjects', ['subject_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'completed_practices', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('completed_practices', 'number')
    op.add_column('groups', sa.Column('random_queue', sa.Boolean(), nullable=True))
    op.add_column('queue', sa.Column('number_practice', sa.Integer(), nullable=True))
    op.add_column('queue', sa.Column('number_in_list', sa.Integer(), nullable=True))
    op.drop_constraint('queue_subject_id_fkey', 'queue', type_='foreignkey')
    op.drop_constraint('queue_user_id_fkey', 'queue', type_='foreignkey')
    op.create_foreign_key(None, 'queue', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'queue', 'subjects', ['subject_id'], ['id'], ondelete='CASCADE')
    op.drop_column('queue', 'number')
    op.add_column('schedule', sa.Column('date_protection', sa.Date(), nullable=True))
    op.drop_constraint('schedule_subject_id_fkey', 'schedule', type_='foreignkey')
    op.create_foreign_key(None, 'schedule', 'subjects', ['subject_id'], ['id'], ondelete='CASCADE')
    op.add_column('subjects', sa.Column('count_practices', sa.Integer(), nullable=True))
    op.add_column('subjects', sa.Column('group_id', sa.Integer(), nullable=False))
    op.add_column('subjects', sa.Column('subject_type', subject_type, nullable=False))
    op.drop_constraint('subjects_group_fkey', 'subjects', type_='foreignkey')
    op.create_foreign_key(None, 'subjects', 'groups', ['group_id'], ['id'], ondelete='CASCADE')
    op.drop_column('subjects', 'count')
    op.drop_column('subjects', 'group')
    op.add_column('users', sa.Column('group_id', sa.Integer(), nullable=True))
    op.drop_constraint('users_group_fkey', 'users', type_='foreignkey')
    op.create_foreign_key(None, 'users', 'groups', ['group_id'], ['id'], ondelete='SET NULL')
    op.drop_column('users', 'group')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('group', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.create_foreign_key('users_group_fkey', 'users', 'groups', ['group'], ['id'])
    op.drop_column('users', 'group_id')
    op.add_column('subjects', sa.Column('group', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('subjects', sa.Column('count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'subjects', type_='foreignkey')
    op.create_foreign_key('subjects_group_fkey', 'subjects', 'groups', ['group'], ['id'])
    op.drop_column('subjects', 'subject_type')
    op.drop_column('subjects', 'group_id')
    op.drop_column('subjects', 'count_practices')
    op.drop_constraint(None, 'schedule', type_='foreignkey')
    op.create_foreign_key('schedule_subject_id_fkey', 'schedule', 'subjects', ['subject_id'], ['id'])
    op.drop_column('schedule', 'date_protection')
    op.add_column('queue', sa.Column('number', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'queue', type_='foreignkey')
    op.drop_constraint(None, 'queue', type_='foreignkey')
    op.create_foreign_key('queue_user_id_fkey', 'queue', 'users', ['user_id'], ['id'])
    op.create_foreign_key('queue_subject_id_fkey', 'queue', 'subjects', ['subject_id'], ['id'])
    op.drop_column('queue', 'number_in_list')
    op.drop_column('queue', 'number_practice')
    op.drop_column('groups', 'random_queue')
    op.add_column('completed_practices', sa.Column('number', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'completed_practices', type_='foreignkey')
    op.drop_constraint(None, 'completed_practices', type_='foreignkey')
    op.create_foreign_key('completed_practices_user_id_fkey', 'completed_practices', 'users', ['user_id'], ['id'])
    op.create_foreign_key('completed_practices_subject_id_fkey', 'completed_practices', 'subjects', ['subject_id'], ['id'])
    op.drop_column('completed_practices', 'number_practice')
    subject_type = postgresql.ENUM(SubjectType, name="subject_type")
    subject_type.drop(op.get_bind())
    # ### end Alembic commands ###
