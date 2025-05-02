from email_classification import EmailClassification


class EmailBase:
    email_id: str
    sender_name: str
    sender_address: str
    subject: str
    classification: EmailClassification
    email_source: str