import psycopg2
from psycopg2 import Error
class PostgresDbConnector:

    __host = 'localhost'
    __database = 'localDB'
    __user = 'email_classifier'
    __password = ''
    __port = '5432'
    __upsert_sproc_name = 'public.emails_upsert'

    def __init__(self, config):
        self.__password = config['localPostresPassword']

    def __connect(self):
        try:
            connection = psycopg2.connect(database=self.__database,
                                    user=self.__user,
                                    password=self.__password,
                                    host=self.__host,
                                    port=self.__host)
            return connection
        except Error as e:
            print(f'Error connecting to DB:  {e}')

    def upsert(self, email_id: str, is_spam: bool, sender_address: str, sender_name: str, subject: str, source: str):
        connection = self.__connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f'CALL {self.__upsert_sproc_name}(%s, %s, %s, %s, %s, %s, %s);', (email_id, is_spam, sender_address, sender_name, subject, source, None))
            connection.commit()
        except Exception as e:
            print(f"Error upserting email: {e}")
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
