import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email_classification import EmailClassification


class Gmail_api_client:
    __scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
    __creds = None
    __not_spam_label_id = 'Label_7181974657700970591'
    __spam_label_id = 'Label_2209700380525172462'
    __personal_label_id = 'CATEGORY_PERSONAL'
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

    def list_emails(self, label_ids, message_ids, query=None, next_page_token=None, initial_call=False):
        """
            Recursive function to handle reading email ids for further processing

            Parameters:
                label_ids (list): gmail labels to target.
                message_ids (list): list of message ids to append results to.
                query (str):  custom query per gmail spec.
                next_page_token (str): page token for fetching further results.
                initial_call (bool): is this the first non-recursive call?
            Returns:
                  None
        """
        if not initial_call and next_page_token is None:
            return

        service = build('gmail', 'v1', credentials=self.creds)
        results = service.users().messages().list(userId='me',
                                                  includeSpamTrash=False,
                                                  labelIds=label_ids,
                                                  maxResults=50,
                                                  pageToken=next_page_token,
                                                  q=query).execute()

        for message in results['messages']:
            message_ids.append(message['id'])
        if 'nextPageToken' in results:
            return self.list_emails(label_ids, message_ids, query, results['nextPageToken'])
        else:
            return self.list_emails(label_ids, message_ids, query)

    def get_email_metadata(self, message_id):
        """
            Parameters:
                message_id - message id that uniquely identifies gmail email

            Returns: Email metadata as an class
        """


    def get_emails(self):
        """
            Function to get gmail email data
            :return:
        """
        # get list of email ids
        self.list_emails([self.__spam_label_id], self.__message_ids[EmailClassification.SPAM], initial_call=True)
        self.list_emails([self.__not_spam_label_id], self.__message_ids[EmailClassification.NOT_SPAM], initial_call= True)
        self.list_emails([self.__personal_label_id], self.__message_ids[EmailClassification.NOT_SPAM], initial_call= True, query='-is:unread')

        print(f'Total spam emails: {len(self.__message_ids[EmailClassification.SPAM])}')
        print(f'Total non spam emails: {len(self.__message_ids[EmailClassification.NOT_SPAM])}')

        # read email metadata
        for key in self.__message_ids.keys():
            for message_id in self.__message_ids[key]:
                x = self.get_email_metadata(message_id)

        # map and return
