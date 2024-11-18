"""initial db schema

Revision ID: a61e03c8ff33
Revises:
Create Date: 2024-10-27 12:35:15.241328

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a61e03c8ff33'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE [dbo].[UserSession](
        [SessionId] [uniqueidentifier] NOT NULL,
        [User] [nvarchar](1024) NOT NULL,
        [Property] [nvarchar](30),
        [Department] [nvarchar](30),
        [CreatedOnUtc] [datetime] NOT NULL,
        [UpdatedOnUtc] [datetime] NOT NULL,
     CONSTRAINT [PK_UserSession] PRIMARY KEY CLUSTERED 
    (
        [SessionId] ASC
    ));
    
    CREATE TABLE [dbo].[UserInteraction](
        [UserInteractionId] [uniqueidentifier] NOT NULL,
        [UserSessionId] [uniqueidentifier] NULL,
        [Question] [nvarchar](4000) NOT NULL,
        [Answer] [nvarchar](4000) NOT NULL,
        [CreatedOnUtc] [datetime] NOT NULL,
        [UpdatedOnUtc] [datetime] NOT NULL,
        [Category] [varchar](200) NULL,
     CONSTRAINT [PK_UserInteraction] PRIMARY KEY CLUSTERED 
    (
        [UserInteractionId] ASC
    ));
    
    CREATE TABLE [dbo].[UserInteractionFeedback] (
        [UserInteractionId] UNIQUEIDENTIFIER NOT NULL,
        [UpVoted]           BIT              NULL,
        [CreatedOnUtc]      DATETIME         NOT NULL,
        [UpdatedOnUtc]      DATETIME         NOT NULL,
        CONSTRAINT [PK_UserInteractionFeedback] PRIMARY KEY CLUSTERED ([UserInteractionId] ASC)
    );
    
    CREATE TABLE [dbo].[UserFeedback] (
        [FeedbackId] INT IDENTITY(1,1) PRIMARY KEY,
        [FeedbackText] [nvarchar](4000) NULL,
        [Property] [nvarchar](30),
        [Email] [nvarchar](50),
        [Screenshot] [nvarchar](max) NULL,
        [CreatedOnUtc] [datetime] NOT NULL,
    )
    """)

    op.execute("""
    CREATE procedure [add_userinteraction]
    (
        @id nvarchar(36),
        @sessionId nvarchar(36),
        @question nvarchar(4000),
        @answer nvarchar(4000),
        @category nvarchar(200)
    )
    AS
    BEGIN
         SET NOCOUNT ON -- to prevent extra result sets from
        -- interfering with SELECT statements.
        -- Insert statements for procedure here
        insert into dbo.UserInteraction(UserInteractionId, UserSessionId, Question, Answer,Category, CreatedOnUtc,UpdatedOnUtc)
        values(@id, @sessionId, @question,@answer, @category, GETUTCDATE(),GETUTCDATE())
        return 0
    END;
    """)

    op.execute("""
    CREATE procedure [add_userinteractionfeedback]
    (
        @id nvarchar(36),
        @upvote bit
    )
    AS
    BEGIN
         SET NOCOUNT ON -- to prevent extra result sets from
        insert into dbo.UserInteractionFeedback(UserInteractionId, UpVoted, CreatedOnUtc,UpdatedOnUtc)
        values(@id, @upvote, GETUTCDATE(),GETUTCDATE())
        return 0
    END;
    """)

    op.execute("""
    CREATE procedure [dbo].[add_usersession]
    (
        @id nvarchar(36),
        @user nvarchar(1024),
        @property NVARCHAR(30) = NULL,
        @department NVARCHAR(30) = NULL
    )
    AS
    BEGIN
         SET NOCOUNT ON -- to prevent extra result sets from
        -- interfering with SELECT statements.
        -- Insert statements for procedure here
        insert into dbo.UserSession(SessionId, [User], [Property], [Department], CreatedOnUtc, UpdatedOnUtc)
        values(@id, @user, @property, @department, GETUTCDATE(), GETUTCDATE())
        return 0
    END;
    """)

    op.execute("""
    CREATE PROCEDURE [get_userinteractions]
    (
        @sessionId nvarchar(36)
    )
    AS
    BEGIN

        SELECT UserInteractionId, UserSessionId, Question, Answer, CreatedOnUtc from UserInteraction where UserSessionId = @sessionId

    END;
    """)

    op.execute("""
    CREATE PROCEDURE [get_usersessions]
    (
        @user nvarchar(1024)
    )
    AS
    BEGIN

        SELECT top 20 SessionId, Question, us.CreatedOnUtc
    FROM (
     SELECT *, ROW_NUMBER() OVER (PARTITION BY
     UserSessionId ORDER BY createdOnUtc asc  ) AS row_number
     FROM UserInteraction where UserSessionId is not null
    ) AS ui Inner Join UserSession us on us.SessionId = ui.UserSessionId
    WHERE ui.row_number = 1  and us.[User]=@user order by us.CreatedOnUtc desc

    END;
    """)

    op.execute("""
    CREATE procedure [update_userinteraction]
    (
        @id nvarchar(36),
        @answer nvarchar(4000)
    )
    AS
    BEGIN
        SET NOCOUNT ON -- to prevent extra result sets from
        update  dbo.UserInteraction
        set Answer = @answer,
        UpdatedOnUtc = GETUTCDATE()
        where UserInteractionId = @id
    END;
    """)

    op.execute("""
    CREATE procedure [update_userinteractionfeedback]
    (
        @id nvarchar(36),
        @upvote bit
    )
    AS
    BEGIN
        SET NOCOUNT ON -- to prevent extra result sets from
        update  dbo.UserInteractionFeedback
        set UpVoted = @upvote,
        UpdatedOnUtc = GETUTCDATE()
        where UserInteractionId = @id
    END;
    """)


def downgrade() -> None:
    # Drop stored procedures
    op.execute("""
    DROP PROCEDURE IF EXISTS [add_userinteraction];
    DROP PROCEDURE IF EXISTS [add_userinteractionfeedback];
    DROP PROCEDURE IF EXISTS [add_usersession];
    DROP PROCEDURE IF EXISTS [get_userinteractions];
    DROP PROCEDURE IF EXISTS [get_usersessions];
    DROP PROCEDURE IF EXISTS [update_userinteraction];
    DROP PROCEDURE IF EXISTS [update_userinteractionfeedback];
    """)

    # Drop tables
    op.execute("""
    DROP TABLE [dbo].[UserInteractionFeedback];
    DROP TABLE [dbo].[UserInteraction];
    DROP TABLE [dbo].[UserSession];
    DROP TABLE [dbo].[UserFeedback]
    """)
