import email
import re

from email_base import EmailBase
from email_classification import EmailClassification
from typing import List

class ProtonEmail(EmailBase):
    """
        Class to manage proton emails
    """
    label_ids: List[str]
    unread: bool
    email_folder: str = ""

    def __init__(self, email_message: email.message.Message):
        self.subject = email_message['Subject']
        self.email_id = email_message['X-Pm-Gluon-Id']

        # parse out sender name and address
        _from = email_message['From']
        _from = _from.replace('"', '')
        if "<" in _from and ">" in _from:
            sender_name_match = re.search(".*(?=<.*>)", _from)
            if sender_name_match is not None:
                self.sender_name = sender_name_match[0]

            sender_addr_match = re.search("(?<=<).*(?=>)", _from)
            if sender_addr_match is not None:
                self.sender_address = sender_addr_match[0]
        else:
            self.sender_address = _from

    def read_proton_email_file(self, deserialized_email: dict, file_name: str):
        """
            Take in a dictionary from deserializing json and assigns data to the class
        """
        try:
            self.subject = deserialized_email['Payload']['Subject']
            self.email_id = deserialized_email['Payload']['ID']
            self.sender_address = deserialized_email['Payload']['Sender']['Address']
            self.sender_name = deserialized_email['Payload']['Sender']['Name']
            self.label_ids = deserialized_email['Payload']['LabelIDs']
            self.unread = True if deserialized_email['Payload']['Unread'] == '0' else False
            self.size_bytes = deserialized_email['Payload']['Size']
        except:
            print(f'Problem loading file {file_name}')

    def set_classification(self):
        """
            Gets the classification of this email as either spam, not spam or notset
        """
        classification = EmailClassification.UNKNOWN
        if not self.sender_address.lower() == "kvnschauer@protonmail.com":
            if self.email_folder.lower() == self.__get_spam_folder_name():
                classification = EmailClassification.SPAM
            elif self.email_folder.lower() == self.__get_not_spam_folder_name() or \
                (self.email_folder.lower() == "inbox" and not self.unread):
                classification = EmailClassification.NOT_SPAM

        self.classification = classification

    @staticmethod
    def __get_spam_label_id() -> str:
        return 'qdbSPKYNNaPjSnyK64SYLOXRdwh9dJw9w912z4XV9mFvKSFqdy7Yt3_JYu4GgeLEcNLbNhH4XZzw-N6QZtbikg=='

    @staticmethod
    def __get_not_spam_label_id() -> str:
        return 'JPbYQkCIbN3IOjoHlGGvMoOiojOoOBsvbpM2NyXpt8KJlzwId64o72Sy0nHD7MzYEGMV9PZKz2Z4vXF9COCBFQ=='

    @staticmethod
    def __get_spam_folder_name():
        return "Folders/Spam identified".lower()

    @staticmethod
    def __get_not_spam_folder_name():
        return "Folders/Not Spam".lower()

    @staticmethod
    def __get_inbox_label_id() -> str:
        return '0'

    @staticmethod
    def __get_sent_label_id() -> str:
        return '7'