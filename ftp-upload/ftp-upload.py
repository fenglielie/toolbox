#!/usr/bin/env python3

import os
import json
import argparse
from ftplib import FTP
import logging
import sys


def create_directory(ftp, remote_dir):
    """
    创建多级目录，确保目录存在
    """
    dirs = remote_dir.strip("/").split("/")  # 切割成目录层级
    current_dir = ""

    for dir in dirs:
        current_dir += "/" + dir
        try:
            # 尝试切换到该目录
            ftp.cwd(current_dir)
        except Exception:
            # 如果目录不存在，则创建
            try:
                ftp.mkd(current_dir)
                logging.info(f"Directory {current_dir} created.")
            except Exception as e:
                logging.error(f"Failed to create directory {current_dir}: {e}")
                return False
    return True


def upload_file(ftp_host, ftp_user, ftp_pass, ftp_encoding, local_file, remote_dir):
    """
    上传文件到指定FTP服务器目录
    """
    # 路径合法性处理：要求路径使用Linux分隔符，并且必须是以/开头的绝对路径（ftp用户可访问的根目录）
    remote_dir = remote_dir.replace("\\", "/")
    if not remote_dir.startswith("/"):
        raise ValueError(
            f"Invalid remote directory: {remote_dir}. It must start with '/'."
        )

    try:
        # 连接到FTP服务器
        ftp = FTP(ftp_host, encoding=ftp_encoding)
        ftp.login(user=ftp_user, passwd=ftp_pass)
        logging.info(f"Successfully connected to {ftp_host}")

        # 确保目标目录存在
        if not create_directory(ftp, remote_dir):
            logging.error(f"Failed to create directory: {remote_dir}")
            return

        # 切换到指定目录
        ftp.cwd(remote_dir)
        logging.info(f"Changed to directory: {remote_dir}")

        # 上传文件
        with open(local_file, "rb") as file:
            ftp.storbinary(f"STOR {os.path.basename(local_file)}", file)
            logging.info(f"File '{local_file}' uploaded successfully to {remote_dir}")

        # 退出FTP
        ftp.quit()
    except Exception as e:
        logging.error(f"Error: {e}")


def load_config(config_path):
    """
    从JSON配置文件中加载FTP配置信息
    """
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = json.load(file)
            return config
    except Exception as e:
        raise ValueError(f"Failed to load config file: {e}")


def main():
    parser = argparse.ArgumentParser(description="FTP File Upload Tool")
    parser.add_argument(
        "-c",
        "--config",
        default="ftp-config.json",
        help="Configuration file path, default is ftp-config.json",
    )
    parser.add_argument("file", help="Path to the local file to upload.")
    parser.add_argument(
        "-d",
        "--destination",
        required=True,
        help="Destination directory on the FTP server.",
    )
    args = parser.parse_args()

    # 初始化日志
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # 加载配置
    try:
        config = load_config(args.config)
    except ValueError as e:
        logging.error(e)
        sys.exit(1)

    # 验证配置内容
    required_keys = ["ftp_host", "ftp_user", "ftp_pass", "ftp_encoding"]
    for key in required_keys:
        if key not in config:
            logging.error(f"Missing required key '{key}' in configuration file.")
            sys.exit(1)

    # 执行文件上传
    try:
        upload_file(
            ftp_host=config["ftp_host"],
            ftp_user=config["ftp_user"],
            ftp_pass=config["ftp_pass"],
            ftp_encoding=config["ftp_encoding"],
            local_file=args.file,
            remote_dir=args.destination,
        )
    except ValueError as e:
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
ftp-config.json

{
    "ftp_host": "ftp.example.com",
    "ftp_user": "your_username",
    "ftp_pass": "your_password",
    "ftp_encoding": "gbk"
}
"""

"""
demo

(1)
python3 ftp-upload.py -d "/remote/path" /local/path/to/file.txt

(2)
python3 ftp-upload.py -c custom-config.json -d "/remote/path" /local/path/to/file.txt

(3)
python3 ftp-upload.py -d "/" /local/path/to/file.txt
"""
