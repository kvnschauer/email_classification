import psycopg2
from psycopg2 import Error
import pandas as pd

class PostgresDbConnector:

    __host = 'localhost'
    __database = 'localDB'
    __user = 'email_classifier'
    __password = ''
    __port = '5432'
    __upsert_emails_sproc = 'public.email_upsert'
    __read_emails_bulk_function = 'public.emails_bulk_read'

    def __init__(self, config):
        self.__password = config['localPostgresPassword']

    """
        Creates and returns local postgresql DB connection
    """
    def __connect(self):
        try:
            connection = psycopg2.connect(database=self.__database,
                                    user=self.__user,
                                    password=self.__password,
                                    host=self.__host,
                                    port=self.__port)
            return connection
        except Error as e:
            print(f'Error connecting to DB:  {e}')

    """
        Inserts or updates an email in the database
        
        parameters:
            email_id - email id from source system
            is_spam - spam classification
            sender_address - sender email address
            sender_name - sender name of the email
            subject - subject of the email
            source - source of the email (gmail or proton)
    """
    def upsert_email(self, email_id: str, is_spam: bool, sender_address: str, sender_name: str, subject: str, source: str, size_bytes: int):
        connection = self.__connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f'CALL {self.__upsert_emails_sproc}(%s, %s, %s, %s, %s, %s, %s, %s);',
                           (email_id, is_spam, sender_address, sender_name, subject, source, size_bytes, None))
            connection.commit()
        except Exception as e:
            print(f"Error upserting email: {e}")
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    """
        Get emails in batches of 100
        
        parameters:
            idSearchAfter - database id to search after
            
        returns:
            up to 100 emails from the db
    """
    def read_emails_bulk(self, id_search_after):
        connection = self.__connect()
        cursor = connection.cursor()

        try:
            results = cursor.execute(f'SELECT * FROM {self.__read_emails_bulk_function}(%s)', (id_search_after))
            dataset = pd.DataFrame(cursor.fetchall(), columns=['id', 'email_id', 'is_spam', 'sender_address', 'sender_name', 'subject', 'create_datetime_utc'])
        except Exception as e:
            print(f"Error getting emails: {e}")
            raise
        finally:
            cursor.close()
            connection.close()