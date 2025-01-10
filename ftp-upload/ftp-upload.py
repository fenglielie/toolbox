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


def upload_file(ftp, local_file, remote_dir):
    """
    上传单个文件
    """
    try:
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
    except Exception as e:
        logging.error(f"Error uploading file '{local_file}': {e}")


def upload_directory(ftp, local_dir, remote_dir):
    """
    递归上传文件夹及其内容，跳过隐藏文件夹（以.开头的文件夹）
    """
    # 先在FTP上创建顶层文件夹
    if not create_directory(ftp, remote_dir):
        logging.error(f"Failed to create directory: {remote_dir}")
        return

    for root, dirs, files in os.walk(local_dir):
        # 过滤掉隐藏文件夹（以.开头的文件夹）
        dirs[:] = [d for d in dirs if not d.startswith(".")]  # 只保留非隐藏文件夹

        # 计算相对路径并构建目标远程路径
        relative_path = os.path.relpath(root, local_dir)
        target_remote_dir = os.path.join(remote_dir, relative_path).replace("\\", "/")

        # 上传文件
        for file in files:
            local_file_path = os.path.join(root, file)
            upload_file(ftp, local_file_path, target_remote_dir)


def upload(local_path, remote_dir, config):
    """
    上传文件或文件夹，判断上传对象类型
    """
    try:
        # 连接到FTP服务器
        ftp = FTP(config["ftp_host"], encoding=config["ftp_encoding"])
        ftp.login(user=config["ftp_user"], passwd=config["ftp_pass"])
        logging.info(f"Successfully connected to {config['ftp_host']}")

        # 判断上传的是文件还是文件夹
        if os.path.isdir(local_path):
            logging.info(f"Uploading folder: {local_path}")
            upload_directory(ftp, local_path, remote_dir)
        elif os.path.isfile(local_path):
            logging.info(f"Uploading file: {local_path}")
            upload_file(ftp, local_path, remote_dir)
        else:
            logging.error(f"Invalid path: {local_path}")

        ftp.quit()

    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


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
    parser = argparse.ArgumentParser(description="FTP File/Folder Upload Tool")
    parser.add_argument(
        "-c",
        "--config",
        default="ftp-config.json",
        help="Configuration file path, default is ftp-config.json",
    )
    parser.add_argument("path", help="Path to the local file or folder to upload.")
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

    # 使目录支持~
    local_path = os.path.expanduser(args.path)
    destination_path = os.path.expanduser(args.destination)
    config_path = os.path.expanduser(args.config)

    # 加载配置
    try:
        config = load_config(config_path)
    except ValueError as e:
        logging.error(e)
        sys.exit(1)

    # 验证配置内容
    required_keys = ["ftp_host", "ftp_user", "ftp_pass", "ftp_encoding"]
    for key in required_keys:
        if key not in config:
            logging.error(f"Missing required key '{key}' in configuration file.")
            sys.exit(1)

    # 执行文件或文件夹上传
    upload(local_path, destination_path, config)


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
