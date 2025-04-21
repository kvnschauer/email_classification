import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from EmailClassification import EmailClassification


class Gmail_api_client:
    __scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
    __creds = None
    __not_spam_label_id = 'Label_7181974657700970591'
    __spam_label_id = 'Label_2209700380525172462'
    __inbox_label_id = 'INBOX'
    __message_ids = {EmailClassification.SPAM:[], EmailClassification.NOT_SPAM: [], EmailClassification.UNKNOWN: []}

    def __init__(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", self.__scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                  "credentials.json", self.__scopes
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def list_emails(self, label_ids, message_ids):
        service = build('gmail', 'v1', credentials=self.creds)
        next_page_token = None

        results = service.users().messages().list(userId='me', includeSpamTrash=False, labelIds=label_ids, maxResults=5).execute()
        for message in results['messages']:
            message_ids.append(message['id'])
        if 'nextPageToken' in results:
            next_page_token = results['nextPageToken']

            while next_page_token is not None:
                results = service.users().messages().list(userId='me', includeSpamTrash=False,
                                                          labelIds=label_ids, maxResults=100, pageToken=next_page_token).execute()
                for message in results['messages']:
                    message_ids.append(message['id'])

                if 'nextPageToken' in results:
                    next_page_token = results['nextPageToken']
                else:
                    next_page_token = None

    def get_emails(self):
        # get list of email ids
        self.list_emails([self.__spam_label_id], self.__message_ids[EmailClassification.SPAM])
        self.list_emails([self.__not_spam_label_id], self.__message_ids[EmailClassification.NOT_SPAM])
        self.list_emails([self.__inbox_label_id], self.__message_ids[EmailClassification.UNKNOWN])

        # read email metadata
        # map and return
