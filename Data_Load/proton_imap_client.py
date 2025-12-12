import imaplib
import email
from email import policy

from Data_Load.proton_email import ProtonEmail

class ProtonImapClient:

    __port = None
    __ip = None
    __password = None

    def __init__(self, config):
        self.__port = config["protonImapPort"]
        self.__ip = config["protonImapIp"]
        self.__password = config["protonImapPassword"]

    def read_email_from_folder(self, folder_name):
        emails = []
        with imaplib.IMAP4(host=self.__ip, port=self.__port) as imap_client:
            imap_client.starttls()
            imap_client.login("kvnschauer@protonmail.com", self.__password)

            # loop through folders and read email data
            print(f"Reading emails from folder {folder_name}")
            status, _ = imap_client.select(folder_name)
            if status.lower() == "ok":
                status, email_ids = imap_client.search(None, 'ALL')
                split_emails = email_ids[0].split()
                counter = 0

                for email_id in split_emails:
                    print(f"Processing email {counter}/{len(split_emails)}")
                    # fetch email metadata
                    typ, data = imap_client.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(data[0][1], policy=policy.default)
                    new_email = ProtonEmail(msg)

                    # determine if the email has been seen
                    status, data = imap_client.fetch(email_id, "(FLAGS)")
                    flags = data[0].decode()
                    is_read = "\\Seen" in flags
                    new_email.unread = not is_read
                    new_email.email_folder = folder_name.replace('"','')
                    new_email.email_source = "Proton"
                    new_email.set_classification()

                    emails.append(new_email)
                    counter+=1
            else:
                print(f"Error selecting folder {folder_name}")

        return emails

    def read_emails_all(self, emails):
        emails = []
        folders = {
            '"Folders/Spam identified"',
            '"Folders/Not Spam"',
            '"INBOX"'
        }

        # loop through folders and read email data
        for folder in folders:
            emails = emails + self.read_email_from_folder(folder)

        return emails