#!/usr/bin/env python3

import subprocess
import getpass
import re
import sys
import argparse
import json
from pathlib import Path


def load_credentials(config_path: Path) -> tuple[str, str]:
    """
    Load username and password from a JSON config file.
    If the file does not exist, prompt the user to enter them manually.

    :param config_path: Path to the JSON config file
    :return: (username, password) tuple
    """
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            username = config.get("username")
            password = config.get("password")
            if not username or not password:
                raise ValueError("Missing 'username' or 'password' in config file.")
            return username, password
        except Exception as e:
            print(f"Failed to read config file: {e}")
            sys.exit(1)
    else:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        return username, password


def login_and_fetch_html(username: str, password: str) -> str:
    """
    Use curl to log in with the provided credentials and return the HTML response.

    :param username: The login username
    :param password: The login password
    :return: HTML response as a decoded string
    """
    url = "http://wlt.ustc.edu.cn/cgi-bin/ip"
    post_data = f"cmd=set&name={username}&password={password}&type=0&exp=0"

    try:
        result = subprocess.run(
            ["curl", "-s", "-d", post_data, url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        html_bytes = result.stdout
    except subprocess.CalledProcessError as e:
        print("Network request failed:", e.stderr.decode("utf-8", errors="ignore"))
        sys.exit(1)

    return html_bytes.decode("gb2312", errors="ignore")


def extract_body_from_html(html: str) -> bool:
    """
    Extract the <body> content from the HTML and check for success keywords.

    :param html: Full HTML content
    :return: True if login success keywords are found, False otherwise
    """
    match = re.search(r"<body.*?>.*?</body>", html, re.DOTALL | re.IGNORECASE)
    if not match:
        return False
    body = match.group(0)

    success_keywords = ["成功", "成功连接", "登录成功", "连接已建立"]
    return any(keyword in body for keyword in success_keywords)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    :return: argparse.Namespace object with parsed arguments
    """
    parser = argparse.ArgumentParser(description="USTC wlt login script.")
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to JSON file containing username and password.",
        default=Path.home() / ".config/wlt/wlt-config.json"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    username, password = load_credentials(args.config)
    html = login_and_fetch_html(username, password)
    if extract_body_from_html(html):
        print("Login successful.")
    else:
        print("Login failed.")


if __name__ == "__main__":
    main()
