from email_base import EmailBase
from email_classification import EmailClassification
from typing import List
'''
    Class to manage proton emails
'''
class ProtonEmail(EmailBase):
    label_ids: List[str]

    ''' 
        Take in a dictionary from deserializing json and assigns data to the class
    '''
    def __init__(self, deserialized_email: dict, file_name: str):
        try:
            self.subject = deserialized_email['Payload']['Subject']
            self.email_id = deserialized_email['Payload']['ID']
            self.sender_address = deserialized_email['Payload']['Sender']['Address']
            self.sender_name = deserialized_email['Payload']['Sender']['Name']
            self.label_ids = deserialized_email['Payload']['LabelIDs']
            self.unread = True if deserialized_email['Payload']['Unread'] == '0' else False
        except:
            print(f'Problem loading file {file_name}')

    '''
        Gets the classification of this email as either spam, not spam or notset 
    '''
    def get_classification(self):
        classification = EmailClassification.UNKNOWN
        if not self.label_ids.__contains__(self.__get_sent_label_id()):
            if self.label_ids.__contains__(self.__get_spam_label_id()):
                classification = EmailClassification.SPAM
            elif self.label_ids.__contains__(self.__get_not_spam_label_id())\
                or (self.label_ids.__contains__(self.__get_inbox_label_id()) and not self.unread):
                classification = EmailClassification.NOT_SPAM

        return classification

    @staticmethod
    def __get_spam_label_id(self) -> str:
        return 'qdbSPKYNNaPjSnyK64SYLOXRdwh9dJw9w912z4XV9mFvKSFqdy7Yt3_JYu4GgeLEcNLbNhH4XZzw-N6QZtbikg=='

    @staticmethod
    def __get_not_spam_label_id(self) -> str:
        return 'JPbYQkCIbN3IOjoHlGGvMoOiojOoOBsvbpM2NyXpt8KJlzwId64o72Sy0nHD7MzYEGMV9PZKz2Z4vXF9COCBFQ=='

    @staticmethod
    def __get_inbox_label_id(self) -> str:
        return '0'

    @staticmethod
    def __get_sent_label_id() -> str:
        return '7'