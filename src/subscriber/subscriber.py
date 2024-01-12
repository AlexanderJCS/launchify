from .email_receiver import EmailReceiver


class Subscriber:
    def __init__(self, receiver: EmailReceiver, config: dict, secret: dict):
        self.receiver = receiver
        self.config = config
        self.secret = secret

    def _add_subscription(self, email: str) -> None:
        """
        Adds a subscription to the secret file.

        :param email: The email to add
        """

        self.secret["subscriptions"].append(email)
        self.secret["subscriptions"] = list(set(self.secret["subscriptions"]))

    def _remove_subscription(self, email: str) -> None:
        """
        Removes a subscription from the secret file.

        :param email: The email to remove
        """

        try:
            self.secret["subscriptions"].remove(email)
        except ValueError:
            pass

    @staticmethod
    def str_cmp(str1, str2) -> bool:
        """
        Compares two strings, ignoring case. Returns False if one of the arguments is not a string.

        :param str1: The first string
        :param str2: The second string
        :return: True if the strings are equal ignoring case, False if they are not equal not strings
        """

        if not isinstance(str1, str) or not isinstance(str2, str):
            return False

        return str1.lower() == str2.lower()

    def check_new_subscriptions(self) -> dict:
        """
        Checks for new subscriptions and adds them to secret.

        :return: The new secret if there are new subscriptions, the same secret otherwise
        """

        for email in self.receiver.get_last_emails(1):
            print(email["Subject"], email["Body"])

            # if the subject or body of the email is "subscribe", add the email to the secret file
            if self.str_cmp(email["Subject"], "subscribe") or \
                    self.str_cmp(email["Body"], "subscribe"):

                print(email["Subject"], email["Body"])

                self._add_subscription(email["From"])

        return self.secret

    def check_unsubscriptions(self) -> dict:
        for email in self.receiver.get_last_emails(1):
            # if the subject or body of the email is "unsubscribe", remove the email from the secret file
            if self.str_cmp(email["Subject"], "unsubscribe") or \
                    self.str_cmp(email["Body"], "unsubscribe"):

                self._remove_subscription(email["From"])

        return self.secret

    def check(self) -> dict:
        """
        Checks for new subscriptions and unsubscriptions.

        :return: The new secret
        """

        self.check_new_subscriptions()
        return self.check_unsubscriptions()
