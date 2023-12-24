# Rocket Launch Reminder

A Python program that sends text message (SMS) and email reminders about rocket launches.

![](readme_images/text_message.jpg)

This application offers two types of reminders:
- Daily reminders, which send information about all launches in the next 24 hours at 9:30 AM (by default).
- Pre-launch reminders, which send 15 minutes before a launch (by default).

This program sends text messages using [SMS gateway](https://en.wikipedia.org/wiki/SMS_gateway), which provides a free method of sending text messages with the benefit of sending an email as an alternative.

## Setup

This section covers the setup of the rocket launch reminder application. This tutorial already assumes that Python 3.11 or greater is installed, along with git.

### Email Address

The first step is to set up a Google and Gmail account that the rocket launch reminder program will utilize.

1. Create a Google account [here](https://www.google.com/account/about/).
   1. Press the `Create an account` button on the top right
2. Follow the steps [here](https://support.google.com/mail/answer/185833?hl=en) to create an app password. Save the app password for later.

### Downloading
You can download this project by cloning the repository:
```shell
$ git clone https://github.com/AlexanderJCS/rocket-launch-reminder-v2.git
```

Also make sure to download `requests`, a dependency of this project:
```shell
$ py -m pip install -r requirements.txt
```

### Creating secret.toml
`secret.toml` will contain personal information such as the sender email address, the sender's app password, and the receiver email addresses.

The first step is to understand who will be receiving these messages. If you want the messages to send to your phone via an SMS text message, the email will be `{your-10-digit-phone-number}@{sms-gateway.com}`. To understand which SMS gateway to use, consult the below tables:

SMS gateway domains for U.S. Carriers:

| Mobile Carrier     | SMS gateway domain        |
|--------------------|---------------------------|
| Alltel             | sms.alltelwireless.com    |
| AT&T               | txt.att.net               |
| Boost Mobile       | sms.myboostmobile.com     |
| Consumer Cellular  | mailmymobile.net          |
| Cricket Wireless   | mms.cricketwireless.net   |
| Google Fi Wireless | msg.fi.google.com         |
| MetroPCS           | mymetropcs.com            |
| Republic Wireless  | text.republicwireless.com |
| Sprint             | messaging.sprintpcs.com   |
| T-Mobile           | tmomail.net               |
| Ting               | message.ting.com          |
| U.S. Cellular      | email.uscc.net            |
| Verizon Wireless   | vtext.com                 |
| Virgin Mobile      | vmobl.com                 |
| XFinity Mobile     | vtext.com                 |

SMS gateway domains for Canadian carriers:

| Mobile Carrier        | SMS gateway domain   |
|-----------------------|----------------------|
| Bell Canada           | txt.bell.ca          |
| Bell MTS              | text.mts.net         |
| Fido Solutions        | fido.ca              |
| Freedom Mobile        | txt.freedommobile.ca |
| Koodo Mobile          | msg.telus.com        |
| PC Mobile             | mobiletxt.ca         |
| Rogers Communications | None                 |
| SaskTel               | sms.sasktel.com      |
| Telus                 | msg.telus.com        |

For example, if I had the Verizon Wireless mobile carrier, and my phone number is `980-555-4518`, the receiver email would be `9805554518@vtext.com`.

Keep note of your SMS gateway address, since this will be needed for the next steps.

The next step is to create the `secret.toml` configuration file. First, `cd` to the cloned directory from the last step.
```shell
$ cd rocket-launch-reminder-v2
```

Then, run `setup.py`. Make sure you have the email address and app password prepared from step 1. Do not include spaces in your app password.

```shell
$ py setup.py

Sender email address: youremail@gmail.com
Sender password: your_16_digit_app_password
Enter comma-separated receiver emails (do not include a space between emails): 9805554518@vtext.com,my_email@example.com
```

### Adjusting config.toml

You can adjust `config/config.toml` to your liking to configure how the program behaves.

### Running the program!

You can run the program by performing:
```shell
$ py -m src.main
```
Assuming you are in the project's root directory

## Contributing

Contributions are welcome. For larger contributions, please create an issue to discuss before a pull request.
