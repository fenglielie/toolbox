#!/usr/bin/env python3

import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
import json
import sys
import os


def send_email(
    subject,
    body,
    sender,
    receiver,
    host,
    port,
    username,
    password,
    attachment_paths=None,
):
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = Header(subject, "utf-8")  # type: ignore

    # 添加邮件正文
    message.attach(MIMEText(body, "plain", "utf-8"))

    # 添加附件
    if attachment_paths:
        for attachment_path in attachment_paths:
            if os.path.isfile(attachment_path):
                try:
                    with open(attachment_path, "rb") as attachment_file:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment_file.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(attachment_path)}",
                        )
                        message.attach(part)
                except Exception as e:
                    print(f"Error: Failed to attach file '{attachment_path}'. {e}")
                    sys.exit(1)

    try:
        smtpObj = smtplib.SMTP_SSL(host, port)
        smtpObj.login(username, password)
        smtpObj.sendmail(sender, receiver, message.as_string())
        print("Email sent successfully")
    except smtplib.SMTPException as e:
        print(f"Error: Failed to send email. {e}")
    finally:
        smtpObj.quit() if "smtpObj" in locals() else None


def main():
    parser = argparse.ArgumentParser(description="Send Email with attachments")
    parser.add_argument("receiver", help="Email receiver")
    parser.add_argument("-s", "--subject", required=True, help="Email subject")
    parser.add_argument(
        "-c",
        "--config",
        default="mail-config.json",
        help="Configuration file path, default is mail-config.json",
    )
    parser.add_argument("-m", "--message", help="Email content")
    parser.add_argument(
        "-a",
        "--attach",
        action="append",
        help="Attachment file path (can be used multiple times)",
    )
    args = parser.parse_args()

    try:
        with open(args.config, "r") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Configuration file '{args.config}' is not a valid JSON.")
        sys.exit(1)

    required_keys = ["username", "password", "sender", "host", "port"]
    for key in required_keys:
        if key not in config:
            print(f"Error: Missing required key '{key}' in configuration file.")
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

    send_email(
        args.subject,
        body,
        sender,
        receiver,
        host,
        port,
        mail_user,
        mail_pass,
        args.attachment,
    )


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

(5)
python3 sendmail.py -s "subject" -m "content" -a attachment.pdf receiver@example.com
"""
