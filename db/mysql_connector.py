import pymysql
from pymysql import Error as MySQLError
from pymysql.cursors import DictCursor
from local_settings import MYSQL_CONFIG


# подключение к MySQL
def get_mysql_connection():
    try:
        return pymysql.connect(
            host=MYSQL_CONFIG["host"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
            cursorclass=DictCursor,
            connect_timeout=2,
            read_timeout=5
        )
        conn.ping(reconnect=True)
        return conn
    except MySQLError as e:
        print(f"Ошибка подключения к SQL: {e}")
        raise
