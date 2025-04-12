import json
from os import listdir
from typing import List
from proton_email import Proton_Email

'''
    Script to load email data into postgre SQL locally

    For Proton emails:
    - data is loaded from json meta data files for each email
    - label Ids property distinguishes if email is spam or not
    - label id JPbYQkCIbN3IOjoHlGGvMoOiojOoOBsvbpM2NyXpt8KJlzwId64o72Sy0nHD7MzYEGMV9PZKz2Z4vXF9COCBFQ== is not spam
    - label id qdbSPKYNNaPjSnyK64SYLOXRdwh9dJw9w912z4XV9mFvKSFqdy7Yt3_JYu4GgeLEcNLbNhH4XZzw-N6QZtbikg== is spam
'''
proton_emails: List[Proton_Email] = []
proton_emails_path = 'C:\\Users\\Kevin\\Documents\\Email backups\\Proton\\kvnschauer@protonmail.com\\mail_20250409_160756'
proton_emails_metadata_files = \
[
    file_name for file_name in
    listdir(proton_emails_path)
    if file_name.endswith('.json')
]

for index in range(0, 1, 1):
    with open(proton_emails_path + '\\' + proton_emails_metadata_files[0], 'r', encoding='utf-8') as f:
        data = json.load(f)
        new_email = Proton_Email(data)

