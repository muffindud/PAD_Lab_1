import psycopg


class PostgresConn:
    def __init__(self, host, port, user, password, dbname):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname

        self.conn = psycopg.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
        )

    def get_last_id(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(id) FROM users")
        return cursor.fetchone()[0]

    def check_if_updated(self, last_id):
        return self.get_last_id() != last_id

    def get_data_since_last_id(self, last_id):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT id, username, email FROM users WHERE id >= {last_id}")
        return cursor.fetchall()

    def get_all_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, username, email FROM users")
        return cursor.fetchall()

    def get_user_id(self, username):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT id FROM users WHERE username = '{username}'")
        return cursor.fetchone()[0]
