import email
import imaplib


class EmailReceiver:
    def __init__(self, username: str, password: str, imap_server: str = "imap.gmail.com"):
        self.username = username
        self.password = password
        self.imap_server = imap_server

    def get_last_emails(self, last_num=1):
        """
        :param last_num: The last number of emails to retrieve. E.g., if this is set to 3, retrieve the last 3 emails
        :return: The last 3 emails. If there is an abort in imaplib, it will return an empty list.
        """

        connection = imaplib.IMAP4_SSL(self.imap_server)
        connection.login(self.username, self.password)

        try:
            status, messages = connection.select("INBOX")

        except imaplib.IMAP4.abort:
            return []

        messages = int(messages[0])

        mail_items = []

        for i in range(messages, messages - last_num, -1):
            res, msg = connection.fetch(str(i), "(RFC822)")

            for response in msg:
                if not isinstance(response, tuple):
                    continue

                mail = email.message_from_bytes(response[1])
                mail_items.append(mail)

        return mail_items
