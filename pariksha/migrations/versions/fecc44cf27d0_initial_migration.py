"""Initial migration

Revision ID: fecc44cf27d0
Revises: 
Create Date: 2024-03-29 22:20:39.846623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fecc44cf27d0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=50), nullable=False),
    sa.Column('verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('student',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teacher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('assignment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=30), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('time_created', sa.DateTime(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=True),
    sa.Column('marks', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quiz',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=30), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('time_created', sa.DateTime(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=True),
    sa.Column('marks', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teaches',
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('teacher_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['student.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id'], ),
    info={'bind_key': None}
    )
    op.create_table('assignment__questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_desc', sa.String(length=700), nullable=False),
    sa.Column('marks', sa.Integer(), nullable=True),
    sa.Column('option_1', sa.String(length=400), nullable=False),
    sa.Column('option_2', sa.String(length=400), nullable=False),
    sa.Column('option_3', sa.String(length=400), nullable=False),
    sa.Column('option_4', sa.String(length=400), nullable=False),
    sa.Column('assignment_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignment.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quiz__questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_desc', sa.String(length=700), nullable=False),
    sa.Column('marks', sa.Integer(), nullable=True),
    sa.Column('option_1', sa.String(length=400), nullable=False),
    sa.Column('option_2', sa.String(length=400), nullable=False),
    sa.Column('option_3', sa.String(length=400), nullable=False),
    sa.Column('option_4', sa.String(length=400), nullable=False),
    sa.Column('quiz_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['quiz_id'], ['quiz.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('submits_assign',
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('assignment_id', sa.Integer(), nullable=True),
    sa.Column('time_submitted', sa.DateTime(), nullable=False),
    sa.Column('marks', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignment.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.id'], ),
    info={'bind_key': None}
    )
    op.create_table('submits_quiz',
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('quiz_id', sa.Integer(), nullable=True),
    sa.Column('time_submitted', sa.DateTime(), nullable=False),
    sa.Column('marks', sa.Integer(), nullable=True),
    sa.Column('terminated', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['quiz_id'], ['quiz.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.id'], ),
    info={'bind_key': None}
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('submits_quiz')
    op.drop_table('submits_assign')
    op.drop_table('quiz__questions')
    op.drop_table('assignment__questions')
    op.drop_table('teaches')
    op.drop_table('quiz')
    op.drop_table('assignment')
    op.drop_table('teacher')
    op.drop_table('student')
    op.drop_table('user')
    # ### end Alembic commands ###