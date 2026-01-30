import json
import pandas as pd

from Data_Load.gmail_api_client import GmailApiClient
from Data_Load.proton_imap_client import ProtonImapClient
from email_classification import EmailClassification
from model import Model
from email_base import EmailBase

config_file_path = 'C:\\repos\\email_classification\\config.json'
config = json.load(open(config_file_path))

class SpamCollector:
    proton_imap_client: ProtonImapClient
    gmail_api_client: GmailApiClient
    model: Model

    def __init__(self):
        self.gmail_api_client = GmailApiClient()
        self.model = Model()
        self.proton_imap_client = ProtonImapClient(config)

    def classify_and_process_emails(self):
        # for gmail then proton emails
            # read unread emails from inbox
            # classify new emails with model
            # if email is spam move to model spam identified inbox

        gmail_emails = self.gmail_api_client.get_emails_by_label(self.gmail_api_client.inbox_label_id, EmailClassification.UNKNOWN, 'is:unread category:primary')

        gmail_emails_df = self.__map_email_to_df(gmail_emails)

        if len(gmail_emails_df) != 0:
            print("processing gmail emails")
            gmail_predictions = self.model.classify_new_mail(gmail_emails_df)

            for index, email in enumerate(gmail_emails):
                if gmail_predictions[index]:
                    self.gmail_api_client.move_email(self.gmail_api_client.inbox_label_id, self.gmail_api_client.model_identified_spam_label, email.email_id)

        proton_emails = self.proton_imap_client.read_email_from_folder('"INBOX"', True)
        if len(proton_emails) > 0:
            proton_email_df = self.__map_email_to_df(proton_emails)
            proton_predictions = self.model.classify_new_mail(proton_email_df)
            for index, email in enumerate(proton_emails):
                if proton_predictions[index]:
                    self.proton_imap_client.move_email(email.uid, '"INBOX"', '"Folders/Model Spam Identified"')


    def __map_email_to_df(self, new_emails):
        emails_df: pd.DataFrame = pd.DataFrame({'sender_local':[], 'sender_domain': [], 'subject': []})

        for email in new_emails:
            new_row: pd.DataFrame = pd.DataFrame({
                'sender_local': [self.model.get_email_local(email.sender_address)],
                'sender_domain': [self.model.get_email_domain(email.sender_address)],
                'subject': email.subject
            })
            emails_df = pd.concat([emails_df, new_row], ignore_index=True)

        return emails_df