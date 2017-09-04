# from ._common import MySQLTable
#
# import uuid
#
#
# class User(MySQLTable):
#     SCHEMA = """
#         CREATE TABLE auth_users (
#             _id INT AUTO_INCREMENT PRIMARY KEY,
#             uuid CHAR(32) NOT NULL UNIQUE,
#             username VARCHAR(128) NOT NULL UNIQUE,
#             email VARCHAR(256) UNIQUE,
#             password VARCHAR(1024),
#             is_active BOOL,
#             created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
#             last_login_on DATETIME NULL
#         )
#     """
#
#     def create(self, username, password, active=False):
#         user_uuid = uuid.uuid4().hex
#         password = pbkdf2_sha256.hash(password)
#         active = 1 if active else 0
#
#         query = """
#             INSERT INTO
#                 `auth_users` (`uuid`, `username`, `password`, `is_active`)
#             VALUES
#                 (%s, %s, %s, %s)
#         """
#         with self.connection.cursor() as cursor:
#             cursor.execute(query, (
#                 user_uuid,
#                 username,
#                 password,
#                 active
#             ))
#             self.connection.commit()
#
#     def check_exists(self, username):
#         query = """
#             SELECT
#                 COUNT(`username`)
#             FROM
#                 auth_users
#             WHERE
#                 `username` = %s
#         """
#         with self.connection.cursor() as cursor:
#             cursor.execute(query, (username, ))
#             result = self.fetchone()
#
#     def verify_login(self, username, password):
#         query = """
#             SELECT
#                 `username`, `password`
#             FROM
#                 auth_users
#             WHERE
#                 `username` = %s
#         """
#         with self.connection.cursor() as cursor:
#             cursor.execute(query, (
#                 username,
#             ))
#             result = cursor.fetchone()
#             return pbkdf2_sha256.verify(password, result['password'])
#
#     def activate(self, username, code):
#         query = """
#             UPDATE
#                 auth_users
#             SET
#                 active = 1
#             WHERE
#                 `username` = %s
#         """
#         with self.connection.cursor() as cursor:
#             cursor.execute(query, (username, ))
#             self.connection.commit()
#
#     def deactivate(self, username):
#         query = """
#             UPDATE
#                 auth_users
#             SET
#                 active = 0
#             WHERE
#                 `username` = %s
#         """
#         with self.connection.cursor() as cursor:
#             cursor.execute(query, (username, ))
#             self.connection.commit()
#
#     def change_password(self, username, new_password):
#         password = pbkdf2_sha256.hash(new_password)
#         query = """
#             UPDATE
#                 auth_users
#             SET
#                 password = %s
#             WHERE
#                 username = %s
#         """
#         with self.connection.cursor() as cursor:
#             cursor.execute(query, (password, username, ))
#             self.connection.commit()
