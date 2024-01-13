import json


def main():
    sender_email = input("Sender email address: ")
    sender_password = input("Sender password: ")

    data = {
        "sender": {
            "username": sender_email,
            "password": sender_password
        },

        "receiver": {
            "emails": []
        }
    }

    with open("config/secret.json", "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
