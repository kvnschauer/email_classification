from Data_Load.gmail_api_client import GmailApiClient
from Data_Load.proton_imap_client import ProtonImapClient


class SpamCollector:
    proton_imap_client: ProtonImapClient
    gmail_api_client: GmailApiClient

    # for gmail then proton emails
        # read unread emails from inbox
        # classify new emails with model
        # if email is spam move to model spam identified inbox