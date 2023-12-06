TEMPLATE = """
[sender]
username = "{sender_email}"
password = "{sender_password}"

[receiver]
emails = {receiver_emails}
"""


def main():
    sender_email = input("Sender email address: ")
    sender_password = input("Sender password: ")

    receiver_emails = input("Enter comma-separated receiver emails (do not include a space between emails): ")

    formatted = TEMPLATE.format(
        sender_email=sender_email,
        sender_password=sender_password,
        receiver_emails=str(receiver_emails.split(","))
    )

    with open("config/secret.toml", "w") as f:
        f.write(formatted)


if __name__ == "__main__":
    main()
