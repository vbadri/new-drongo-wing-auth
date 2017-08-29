from ._common import MySQLTable


class LoginAttempt(MySQLTable):
    SCHEMA = """
        CREATE TABLE auth_login_attempts (
            _id INT AUTO_INCREMENT PRIMARY KEY,
            user_uuid CHAR(32) NOT NULL,
            attempted_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            status CHAR(8),
            session_id CHAR(64),
            FOREIGN KEY (user_uuid) REFERENCES auth_users(uuid)
        )
    """

    def add(self, user_uuid, session_id, status):
        query = """
            INSERT INTO
                auth_login_attempts (user_uuid, session_id, status)
            VALUES
                (%s, %s, %s)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (
                user_uuid,
                session_id,
                status
            ))
            self.connection.commit()

    def get_for_user(self, user_uuid):
        query = """
            SELECT
                (user_uuid, session_id, status)
            FROM
                auth_login_attempts
            WHERE
                `user_uuid` = %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (
                user_uuid,
            ))
            return cursor.fetchall()
