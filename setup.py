import json


def main():
    sender_email = input("Sender email address: ")
    sender_password = input("Sender password: ")

    receiver_emails = input("Enter comma-separated _receiver emails (do not include a space between emails): ")

    data = {
        "sender": {
            "username": sender_email,
            "password": sender_password
        },

        "_receiver": {
            "emails": receiver_emails.split(",")
        }
    }

    with open("config/secret.json", "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
