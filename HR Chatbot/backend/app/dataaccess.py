"""Module to handle the database access."""

from abc import ABC, abstractmethod
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime


class DBAccess(ABC):
    """Abstract class for database access"""

    @abstractmethod
    def add_userinteraction(
        self, interaction_id, session_id, question, answer, category=None
    ):
        """Add user interaction

        Args:
            interaction_id (str): Unique interactio id
            session_id (str): Session id
            question (str): Question user inputted
            answer (str): Answer from LLM
            category (str, optional): User input category identified by LLM . Defaults to None.
        """

    @abstractmethod
    def update_userinteraction(self, interaction_id, answer):
        """Update user interaction

        Args:
            interaction_id (id): interaction id
            answer (string): Answer
        """

    @abstractmethod
    def add_userinteractionfeedback(self, interaction_id, upvote):
        """Add user interaction feedback

        Args:
            interaction_id (id): interaction id
            upvote (bool): Up voted
        """

    @abstractmethod
    def update_userinteractionfeedback(self, interaction_id, upvote):
        """Update user interaction feedback

        Args:
            interaction_id (id): interaction id
            upvote (bool): Up voted
        """

    @abstractmethod
    def add_usersession(self, session_id, user_name, property_value, department):
        """Add user session

        Args:
            session_id (str): Unique session id
            user_name (str): logged in user name
            property_value (Optional[str]): users property
            department (Optional[str]): users department
        """

    @abstractmethod
    def get_usersessions(self, user_name):
        """get sessions by user name

        Args:
            user_name (str): logged in user name

        Returns:
            list: list of user sessions
        """

    @abstractmethod
    def get_userinteractions(self, session_id):
        """Get user interactions by session

        Args:
            session_id (str): Session id to fetch th user interactions

        Returns:
            list: List of user interactions
        """

    @abstractmethod
    def add_userfeedback(self, feedback_text, screenshot, email, property_value):
        """Get user interactions by session

        Args:
            feedback_text (str): feedback text
            screenshot (str): base64 image
            email (str): users email
            property_value (str): users property

        Returns:
            list: List of user interactions
        """


class DataAccess(DBAccess):
    """Class to handle database calls."""

    def __init__(self, connection_string, logger=None):
        """Ininit the database access

        Args:
            connection_string (str): database connection string
            logger (obj, optional):
                Logger object to log the exceptions and information. Defaults to None.
        """
        self.engine = create_engine(connection_string)
        self.logger = logger

    def add_userinteraction(
        self, interaction_id, session_id, question, answer, category=None
    ):
        """Add user interaction

        Args:
            interaction_id (str): Unique interactio id
            session_id (str): Session id
            question (str): Question user inputted
            answer (str): Answer from LLM
            category (str, optional): User input category identified by LLM . Defaults to None.
        """
        connection = None
        result = None
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        try:
            cursor.callproc(
                "add_userinteraction",
                [interaction_id, session_id, question, answer, ""],
            )
            connection.commit()
        except Exception as e:
            if self.logger is not None:
                self.logger.exception(
                    f"Error calling stored procedure 'add_userinteraction' {e}"
                )
            else:
                print(f"Error calling stored procedure 'add_userinteraction' {e}")
        finally:
            # Close cursor and connection
            cursor.close()
            connection.close()
        return result

    def update_userinteraction(self, interaction_id, answer):
        """Update user interaction

        Args:
            interaction_id (id): interaction id
            answer (string): Answer
        """
        connection = None
        result = None
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        try:
            cursor.callproc(
                "update_userinteraction",
                [interaction_id, answer],
            )
            connection.commit()
        except Exception as e:
            if self.logger is not None:
                self.logger.exception(
                    f"Error calling stored procedure 'update_userinteraction' {e}"
                )
        finally:
            # Close cursor and connection
            cursor.close()
            connection.close()
        return result

    def add_userinteractionfeedback(self, interaction_id, upvote):
        """Add user interaction feedback

        Args:
            interaction_id (id): interaction id
            upvote (bool): Up voted
        """
        connection = None
        result = None
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        try:
            cursor.callproc("add_userinteractionfeedback", [interaction_id, upvote])
            connection.commit()
        except Exception as e:
            if self.logger is not None:
                self.logger.exception(
                    f"Error calling stored procedure 'add_userinteractionfeedback' {e}"
                )
        finally:
            # Close cursor and connection
            cursor.close()
            connection.close()
        return result

    def update_userinteractionfeedback(self, interaction_id, upvote):
        """Update user interaction feedback

        Args:
            interaction_id (id): interaction id
            upvote (bool): Up voted
        """
        connection = None
        result = None
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        try:
            cursor.callproc("update_userinteractionfeedback", [interaction_id, upvote])
            connection.commit()
        except Exception as e:
            if self.logger is not None:
                self.logger.exception(
                    f"Error calling stored procedure 'update_userinteractionfeedback' {e}"
                )
        finally:
            # Close cursor and connection
            cursor.close()
            connection.close()
        return result

    def add_usersession(self, session_id, user_name, property_value=None, department=None):
        """Add user session

        Args:
            session_id (str): Unique session id
            user_name (str): logged in user name
            property_value (Optional[str]): users property
            department (Optional[str]): users department
        """
        connection = None
        result = None
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        try:
            cursor.callproc("add_usersession", [session_id, user_name, property_value, department])
            connection.commit()
        except Exception as e:
            if self.logger is not None:
                self.logger.exception(
                    f"Error calling stored procedure 'add_usersession' {e}"
                )
        finally:
            # Close cursor and connection
            cursor.close()
            connection.close()
        return result

    def get_usersessions(self, user_name):
        """get sessions by user name

        Args:
            user_name (str): logged in user name

        Returns:
            list: list of user sessions
        """
        connection = None
        result = None
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        try:
            cursor.callproc("get_usersessions", [user_name])
            df = pd.DataFrame(
                cursor.fetchall(), columns=[col[0] for col in cursor.description]
            )
            result = df.sort_values(by="CreatedOnUtc", ascending=False).to_dict(
                "records"
            )
            connection.commit()
        except Exception as e:
            if self.logger is not None:
                self.logger.exception(
                    f"Error calling stored procedure 'get_usersessions' {e}"
                )
        finally:
            # Close cursor and connection
            cursor.close()
            connection.close()
        return result

    def get_userinteractions(self, session_id):
        """Get user interactions by session

        Args:
            session_id (str): Session id to fetch th user interactions

        Returns:
            list: List of user interactions
        """

        connection = None
        result = None
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        try:
            cursor.callproc("get_userinteractions", [session_id])
            df = pd.DataFrame(
                cursor.fetchall(), columns=[col[0] for col in cursor.description]
            )
            result = df.sort_values(by="CreatedOnUtc").to_dict("records")
            connection.commit()
        except Exception as e:
            print(e)
            if self.logger is not None:
                self.logger.exception(
                    f"Error calling stored procedure 'get_userinteractions' {e}"
                )
        finally:
            # Close cursor and connection
            cursor.close()
            connection.close()
        return result

    def add_userfeedback(self, feedback_text, screenshot, email, property_value):
        connection = None
        feedback_id = None
        created_on_utc = datetime.utcnow().replace(microsecond=0)

        try:
            connection = self.engine.raw_connection()
            cursor = connection.cursor()

            insert_query = f"""
            INSERT INTO [dbo].[UserFeedback] (FeedbackText, Screenshot, Email, Property, CreatedOnUtc)
            VALUES ('{feedback_text}', '{screenshot}', '{email}', '{property_value}', '{created_on_utc}');
            """

            cursor.execute(insert_query)

            connection.commit()

            cursor.execute("SELECT SCOPE_IDENTITY()")
            feedback_id = cursor.fetchone()[0]

        except Exception as e:
            if self.logger is not None:
                self.logger.exception(f"Error inserting into 'UserFeedback': {e}")
            else:
                print(f"Error inserting into 'UserFeedback': {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return feedback_id
