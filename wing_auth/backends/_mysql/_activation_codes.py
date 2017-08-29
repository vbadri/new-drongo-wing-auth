from ._common import MySQLTable

import uuid


class ActivationCode(MySQLTable):
    SCHEMA = """
        CREATE TABLE auth_activation_codes (
            _id INT AUTO_INCREMENT PRIMARY KEY,
            user_uuid CHAR(32) NOT NULL UNIQUE,
            code VARCHAR(128) NOT NULL UNIQUE,
            created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_uuid) REFERENCES auth_users(uuid)
        )
    """

    def create(self, user_uuid):
        code = uuid.uuid4().hex
        query = """
            INSERT INTO
                `auth_activation_codes` (`user_uuid`, `code`)
            VALUES
                (%s, %s)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (
                user_uuid,
                code
            ))
            self.connection.commit()

        return code

    def verify(self, user_uuid, code):
        query = """
            SELECT
                COUNT(*) as `count`
            FROM
                auth_activation_codes
            WHERE
                `user_uuid` = %s AND `code` = %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (
                user_uuid,
                code
            ))
            result = cursor.fetchone()
            return result['count'] == 1
