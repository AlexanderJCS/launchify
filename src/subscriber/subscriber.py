from .email_receiver import EmailReceiver
from ..emailer import emailer


class Subscriber:
    def __init__(self, receiver: EmailReceiver, config: dict, secret: dict):
        self._receiver = receiver
        self._secret = secret
        self._config = config

        self.last_email_date = self._receiver.get_last_email()["date"]

    def _add_subscription(self, email: str) -> None:
        """
        Adds a subscription to the _secret file.

        :param email: The email to add
        """

        self._secret["receiver"]["emails"].append(email)
        self._secret["receiver"]["emails"] = list(set(self._secret["receiver"]["emails"]))

    def _remove_subscription(self, email: str) -> None:
        """
        Removes a subscription from the secret file.

        :param email: The email to remove
        """

        try:
            self._secret["receiver"]["emails"].remove(email)

        except ValueError:
            pass

    def check(self) -> bool:
        """
        Checks for new subscriptions and unsubscriptions.

        :return: If changes were made to the _secret file
        """

        email = self._receiver.get_last_email()

        if email is None or email["date"] == self.last_email_date:
            return False

        self.last_email_date = email["date"]

        # A list of strings to search for "subscribe" or "unsubscribe" in
        email_contents: list[str] = [email["Subject"]]

        # Add any plaintext attachments to the list of strings to search
        for attachment in email.get_payload():
            if attachment.get_content_type() != "text/plain":
                continue

            email_contents.append(attachment.get_payload(decode=True).decode())

        # if the email contains "subscribe", add it to the _secret file
        for content in email_contents:
            if content.lower().strip() == "subscribe":
                self._add_subscription(email["From"])

                emailer.send_email(
                    body=self._config["subscription"]["subscribe"]["message"],
                    subject=self._config["subscription"]["subscribe"]["subject"],
                    to=email["From"],
                    sender=self._secret["sender"]["username"],
                    password=self._secret["sender"]["password"]
                )

                return True

            if content.lower().strip() == "unsubscribe":
                self._remove_subscription(email["From"])

                emailer.send_email(
                    body=self._config["subscription"]["unsubscribe"]["message"],
                    subject=self._config["subscription"]["unsubscribe"]["subject"],
                    to=email["From"],
                    sender=self._secret["sender"]["username"],
                    password=self._secret["sender"]["password"]
                )

                return True

        return False

    def get_secret(self) -> dict:
        """
        :return: The secret file
        """

        return self._secret
