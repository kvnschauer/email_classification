import json
from PostgresDbConnector import PostgresDbConnector
from os import listdir
from typing import List
from ProtonEmail import ProtonEmail
from EmailClassification import EmailClassification

'''
    Script to load email data into postgre SQL locally

    For Proton emails:
    - data is loaded from json meta data files for each email
    - label Ids property distinguishes if email is spam or not
    - label id JPbYQkCIbN3IOjoHlGGvMoOiojOoOBsvbpM2NyXpt8KJlzwId64o72Sy0nHD7MzYEGMV9PZKz2Z4vXF9COCBFQ== is not spam
    - label id qdbSPKYNNaPjSnyK64SYLOXRdwh9dJw9w912z4XV9mFvKSFqdy7Yt3_JYu4GgeLEcNLbNhH4XZzw-N6QZtbikg== is spam
'''
db_connector: PostgresDbConnector = PostgresDbConnector()
proton_emails: List[ProtonEmail] = []
proton_emails_path = 'C:\\Users\\Kevin\\Documents\\Email backups\\Proton\\kvnschauer@protonmail.com\\mail_20250409_160756'

proton_emails_metadata_files = \
[
    file_name for file_name in
    listdir(proton_emails_path)
    if file_name.endswith('.json')
]

for file in proton_emails_metadata_files:
    with open(proton_emails_path + '\\' + file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'Payload' in data and 'Sender' in data['Payload']:
                new_email: ProtonEmail = ProtonEmail(data, file)
                if not new_email.get_classification() == EmailClassification.Unknown:
                    is_spam = True if new_email.get_classification() == EmailClassification.SPAM else False
                    db_connector.upsert(new_email.email_id, is_spam, new_email.sender_address, new_email.sender_name, new_email.subject)