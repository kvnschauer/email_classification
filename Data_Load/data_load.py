import json

from Data_Load.gmail_api_client import GmailApiClient
from os import listdir
from typing import List
from Data_Load.proton_email import ProtonEmail
from Data_Load.proton_imap_client import ProtonImapClient
from email_base import EmailBase
from email_classification import EmailClassification
from postgres_db_client import PostgresDbConnector

emails: List[EmailBase] = []
config_file_path = 'C:\\repos\\email_classification\\config.json'
config = json.load(open(config_file_path))
db_connector: PostgresDbConnector = PostgresDbConnector(config)

def load_proton_emails_from_backup():
    """
        Script to load email data into postgres SQL locally

        For Proton emails:
        - data is loaded from json meta data files for each email
        - label Ids property distinguishes if email is spam or not
        - label id JPbYQkCIbN3IOjoHlGGvMoOiojOoOBsvbpM2NyXpt8KJlzwId64o72Sy0nHD7MzYEGMV9PZKz2Z4vXF9COCBFQ== is not spam
        - label id qdbSPKYNNaPjSnyK64SYLOXRdwh9dJw9w912z4XV9mFvKSFqdy7Yt3_JYu4GgeLEcNLbNhH4XZzw-N6QZtbikg== is spam
    """
    proton_emails_path = 'C:\\Users\\Kevin\\Documents\\Email backups\\Proton\\kvnschauer@protonmail.com\\mail_20250930_210020'

    proton_emails_metadata_files = \
    [
        file_name for file_name in
        listdir(proton_emails_path)
        if file_name.endswith('.json')
    ]
    print('Loading proton emails...')

    # process proton emails
    for file in proton_emails_metadata_files:
        with open(proton_emails_path + '\\' + file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if 'Payload' in data and 'Sender' in data['Payload']:
                    new_email: ProtonEmail = ProtonEmail(data, file)
                    new_email.set_classification()
                    new_email.email_source = 'Proton'
                    emails.append(new_email)
            except Exception as e:
                print(f'Error processing file {file}. Error: {e}')



def load_gmail_emails(emails: List[EmailBase]):
    client = GmailApiClient()
    gmail_emails = client.get_emails_all()
    emails += gmail_emails

def load_data_all():
    proton_imap_client = ProtonImapClient(config)
    #proton_imap_client.read_emails_all(emails)
    load_gmail_emails(emails)

    # load emails to db
    for i, email in enumerate(emails):
        print(f'Upserting email {i} / {len(emails)}')
        if not email.classification == EmailClassification.UNKNOWN:
            is_spam = True if email.classification == EmailClassification.SPAM else False
            db_connector.upsert_email(email.email_id, is_spam, email.sender_address, email.sender_name,
                                email.subject, email.email_source, email.size_bytes)