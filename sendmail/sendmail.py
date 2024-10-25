#!/usr/bin/env python3

import argparse
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import json
import sys


def send_email(subject, body, sender, receiver, host, port, username, password):
    message = MIMEText(body, "plain", "utf-8")
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = Header(subject, "utf-8")  # type: ignore

    try:
        smtpObj = smtplib.SMTP_SSL(host, port)
        smtpObj.login(username, password)
        smtpObj.sendmail(sender, receiver, message.as_string())
        print("Email sent successfully")
    except smtplib.SMTPException as e:
        print("Error: Failed to send email. {}".format(e))
    finally:
        smtpObj.quit() if "smtpObj" in locals() else None


def main():
    parser = argparse.ArgumentParser(description="Send Email")
    parser.add_argument("receiver", help="Email receiver")
    parser.add_argument("-s", "--subject", required=True, help="Email subject")
    parser.add_argument(
        "-c",
        "--config",
        default="mail-config.json",
        help="Configuration file path, default is mail-config.json",
    )
    parser.add_argument("-m", "--message", help="Email content")
    args = parser.parse_args()

    try:
        with open(args.config, "r") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print("Error: Configuration file '{}' not found.".format(args.config))
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Configuration file '{}' is not a valid JSON.".format(args.config))
        sys.exit(1)

    required_keys = ["username", "password", "sender", "host", "port"]
    for key in required_keys:
        if key not in config:
            print("Error: Missing required key '{}' in configuration file.".format(key))
            sys.exit(1)

    mail_user = config["username"]
    mail_pass = config["password"]
    sender = config["sender"]
    host = config["host"]
    port = config["port"]

    receiver = args.receiver

    if args.message:
        body = args.message
    else:
        body = sys.stdin.read()

    send_email(args.subject, body, sender, receiver, host, port, mail_user, mail_pass)


if __name__ == "__main__":
    main()

"""
mail-config.json

{
    "username": "xxxxxxxx@163.com",
    "password": "xxxxxxxxxxxxxxxx",
    "sender": "xxxxxxxx@163.com",
    "host": "smtp.163.com",
    "port": 465
}
"""

"""
demo

(1)
python3 sendmail.py -s "subject" receiver@example.com
<input content, enter+ctrl+d>

(2)
python3 sendmail.py -s "subject" receiver@example.com < content.txt

(3)
cat content.txt | python3 sendmail.py -s "subject" receiver@example.com

(4)
python3 sendmail.py -s "subject" -m "content" receiver@example.com
"""
