import json

from gmail_api_client import Gmail_api_client
from postgres_db_connector import PostgresDbConnector
from os import listdir
from typing import List
from proton_email import ProtonEmail
from email_classification import EmailClassification

'''
    Script to load email data into postgre SQL locally

    For Proton emails:
    - data is loaded from json meta data files for each email
    - label Ids property distinguishes if email is spam or not
    - label id JPbYQkCIbN3IOjoHlGGvMoOiojOoOBsvbpM2NyXpt8KJlzwId64o72Sy0nHD7MzYEGMV9PZKz2Z4vXF9COCBFQ== is not spam
    - label id qdbSPKYNNaPjSnyK64SYLOXRdwh9dJw9w912z4XV9mFvKSFqdy7Yt3_JYu4GgeLEcNLbNhH4XZzw-N6QZtbikg== is spam
'''

def load_proton_email():
    proton_emails: List[ProtonEmail] = []
    proton_emails_path = 'C:\\Users\\Kevin\\Documents\\Email backups\\Proton\\kvnschauer@protonmail.com\\mail_20250414_210820'
    config_file_path = 'C:\\repos\\email_classification\\config.json'
    config = json.load(open(config_file_path))
    db_connector: PostgresDbConnector = PostgresDbConnector(config)

    proton_emails_metadata_files = \
    [
        file_name for file_name in
        listdir(proton_emails_path)
        if file_name.endswith('.json')
    ]

    for file in proton_emails_metadata_files:
        with open(proton_emails_path + '\\' + file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if 'Payload' in data and 'Sender' in data['Payload']:
                    new_email: ProtonEmail = ProtonEmail(data, file)
                    if not new_email.get_classification() == EmailClassification.Unknown:
                        is_spam = True if new_email.get_classification() == EmailClassification.SPAM else False
                        db_connector.upsert(new_email.email_id, is_spam, new_email.sender_address, new_email.sender_name,
                                            new_email.subject, 'Proton')
            except Exception as e:
                print(f'Error processing file {file}. Error: {e}')
def load_gmail_emails():
    client = Gmail_api_client()
    client.get_emails()
#load_proton_email()
load_gmail_emails()