from email_classification import Email_Classification
from typing import List

'''
    Class to manage proton emails
'''
class Proton_Email:
    email_id: str
    sender_name: str
    sender_address: str
    label_ids: List[str]
    subject: str

    ''' 
        Take in a dictionary from deserializing json and assigns data to the class
    '''
    def __init__(self, deserialized_email: dict):
        self.subject = deserialized_email['Payload']['Subject']
        self.email_id = deserialized_email['Payload']['ID']
        self.sender_address = deserialized_email['Payload']['Sender']['Address']
        self.sender_name = deserialized_email['Payload']['Sender']['Name']
        self.label_ids = deserialized_email['Payload']['LabelIDs']


    '''
        Gets the classification of this email as either spam, not spam or notset 
    '''
    def get_classification(self):
        classification = Email_Classification.NOTSET

        if self.label_ids.__contains__(self.get_spam_label_id()):
            classification = Email_Classification.SPAM
        elif self.label_ids.__contains__(self.get_not_spam_label_id()):
            classification = Email_Classification.NOT_SPAM

        return classification

    def get_spam_label_id(self) -> str:
        return 'qdbSPKYNNaPjSnyK64SYLOXRdwh9dJw9w912z4XV9mFvKSFqdy7Yt3_JYu4GgeLEcNLbNhH4XZzw-N6QZtbikg=='

    def get_not_spam_label_id(self) -> str:
        return 'JPbYQkCIbN3IOjoHlGGvMoOiojOoOBsvbpM2NyXpt8KJlzwId64o72Sy0nHD7MzYEGMV9PZKz2Z4vXF9COCBFQ=='


