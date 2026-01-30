import imaplib
import email
import re
from email import policy

from numpy.f2py.auxfuncs import throw_error

from Data_Load.proton_email import ProtonEmail

class ProtonImapClient:

    __port = None
    __ip = None
    __password = None

    def __init__(self, config):
        self.__port = config["protonImapPort"]
        self.__ip = config["protonImapIp"]
        self.__password = config["protonImapPassword"]

    def read_email_from_folder(self, folder_name, unread_emails = False):
        emails = []
        with imaplib.IMAP4(host=self.__ip, port=self.__port) as imap_client:
            imap_client.starttls()
            imap_client.login("kvnschauer@protonmail.com", self.__password)

            # loop through folders and read email data
            print(f"Reading emails from folder {folder_name}")
            status, _ = imap_client.select(folder_name)
            if status.lower() == "ok":
                criteria = "UNSEEN" if unread_emails else "ALL"
                status, email_ids = imap_client.search(None, criteria)
                split_emails = email_ids[0].split()
                counter = 0

                for email_id in split_emails:
                    print(f"Processing email {counter}/{len(split_emails)}")
                    # fetch email metadata
                    typ, data = imap_client.fetch(email_id, "(UID BODY.PEEK[])")
                    msg = email.message_from_bytes(data[0][1], policy=policy.default)
                    new_email = ProtonEmail(msg)
                    metadata = data[0][0].decode()
                    uid_match = re.search(r"UID\s+(\d+)", metadata)
                    if uid_match:
                        new_email.uid = uid_match.group(1)

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

    def move_email(self, email_id, connect_folder_name, move_folder):
        with imaplib.IMAP4(host=self.__ip, port=self.__port) as imap_client:
            imap_client.starttls()
            imap_client.login("kvnschauer@protonmail.com", self.__password)

            status, _ = imap_client.select(connect_folder_name)
            if status.lower() == "ok":
                typ, resp = imap_client.uid("MOVE", email_id, move_folder)
                if typ != "OK":
                    throw_error(f"Issue moving proton email {email_id}")

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