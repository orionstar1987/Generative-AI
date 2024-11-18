"""Add translation fields to UserSession

Revision ID: 852dcf8454c7
Revises: a61e03c8ff33
Create Date: 2024-11-15 14:07:51.875722

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '852dcf8454c7'
down_revision: Union[str, None] = 'a61e03c8ff33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE [dbo].[UserInteraction]
    ADD 
        [TranslatedMessage] NVARCHAR(MAX) NULL,
        [TranslatedAnswer] NVARCHAR(MAX) NULL,
        [QuestionStatus] INT NULL;
    """)


def downgrade() -> None:
    op.execute("""
    ALTER TABLE [dbo].[UserInteraction]
    DROP COLUMN 
        [TranslatedMessage],
        [TranslatedAnswer],
        [QuestionStatus];
    """)
