import json
import os.path
import re
import email_base

from email_base import EmailBase
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from typing import List
from email_classification import EmailClassification

class GmailApiClient:
    __scopes = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"]
    __creds = None
    __not_spam_label_id = 'Label_7181974657700970591'
    __spam_label_id = 'Label_2209700380525172462'
    __personal_label_id = 'CATEGORY_PERSONAL'
    __service: Resource
    __token_file_path = 'C:\\repos\\email_classification\\token.json'
    model_identified_spam_label = 'Label_7059055847257710979'
    inbox_label_id = 'INBOX'

    def __init__(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.__token_file_path):
            self.__creds = Credentials.from_authorized_user_file(self.__token_file_path, self.__scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not self.__creds or not self.__creds.valid:
            if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "C:\\repos\\email_classification\\credentials.json", self.__scopes
                )
                self.__creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.__token_file_path, "w") as token:
                token.write(self.__creds.to_json())

        self.__service = build('gmail', 'v1', credentials=self.__creds)


    def move_email(self, remove_label, add_label, email_id):
        """
            Move an email from one label to another

            Parameters:
                remove_label (str): label to move email from
                add_label (str): label to move email to
        """
        body = {
            'addLabelIds': [add_label],
            'removeLabelIds': [remove_label]
        }

        self.__service.users().messages().modify(body=body,
                                                          id=email_id,
                                                          userId='me').execute()

    def list_emails(self, label_ids, message_ids, query=None, next_page_token=None, initial_call=False):
        """
            Recursive function to handle reading email ids for further processing

            Parameters:
                label_ids (list): gmail labels to target.
                message_ids (list): list of message ids to append results to.
                query (str):  custom query per gmail spec.
                next_page_token (str): page token for fetching further results.
                initial_call (bool): is this the first non-recursive call?
        """
        if not initial_call and next_page_token is None:
            return

        results = self.__service.users().messages().list(userId='me',
                                                  includeSpamTrash=False,
                                                  labelIds=label_ids,
                                                  maxResults=50,
                                                  pageToken=next_page_token,
                                                  q=query).execute()
        if results['resultSizeEstimate'] == 0:
            return

        for message in results['messages']:
            message_ids.append(message['id'])
        if 'nextPageToken' in results:
            return self.list_emails(label_ids, message_ids, query, results['nextPageToken'])
        else:
            return self.list_emails(label_ids, message_ids, query)

    def __get_email_metadata(self, message_id):
        """
            Get the email metadata from a gmail message ID

            Parameters:
                message_id - message id that uniquely identifies gmail email

            Returns: email metadata as an class
        """
        email_metadata = self.__service.users().messages().get(userId='me',
                                              id=message_id,
                                              format='metadata',
                                              metadataHeaders=['Subject', 'From']).execute()

        return email_metadata

    def get_emails_by_label(self, label, classification, query: str = ''):
        emails: List[EmailBase] = []
        message_ids = []

        if query and len(query) > 0:
            self.list_emails([label], message_ids, initial_call=True, query= query)
        else:
            self.list_emails([label], message_ids, initial_call=True)

        for i, message_id in enumerate(message_ids):
            print(f"Fetching email metadata {i} / {len(message_ids)}")
            new_email = EmailBase()
            new_email.email_id = message_id
            new_email.email_source = 'Gmail'
            new_email.classification = classification

            # fetch and extract metadata
            # if one fails then others can still continue
            try:
                metadata = self.__get_email_metadata(message_id)
                self.__process_metadata(metadata, new_email)

                emails.append(new_email)
            except Exception as e:
                print(f'Error processing message id {message_id} {e}')

        return emails

    def get_emails_all(self):
        """
            Function to get gmail email data

            Returns: list of Gmail emails
        """
        emails: List[email_base] = []

        print('Fetching spam gmail email ids...')
        emails = emails + self.get_emails_by_label(self.__spam_label_id, EmailClassification.SPAM)

        print('Fetching non spam gmail email ids...')
        emails = emails + self.get_emails_by_label(self.__not_spam_label_id, EmailClassification.NOT_SPAM)

        print('Fetching read gmail email ids...')
        emails = emails + self.get_emails_by_label(self.inbox_label_id, EmailClassification.NOT_SPAM, '-is:unread')

        return emails

    @staticmethod
    def __process_metadata(metadata, new_email):
        new_email.size_bytes = metadata['sizeEstimate']

        for header in metadata['payload']['headers']:
            if header['name'] == 'Subject':
                new_email.subject = header['value']
            else:
                email_sender_pattern = r'^.*(?=\s)'
                email_address_pattern = r'(?<=[<]).*(?=[>])'

                sender = re.findall(email_sender_pattern, header['value'])
                sender_address = re.findall(email_address_pattern, header['value'])

                if len(sender) > 0:
                    new_email.sender_name = sender[0]
                    new_email.sender_address = sender_address[0]
                else:
                    # sometimes only the email address is present no sender name
                    if header['value'].index('@') > 0:
                        new_email.sender_address = header['value']
