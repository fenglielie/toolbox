#!/usr/bin/env python3

import argparse
import logging
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import socket
import threading
import time

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pychat-server.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

clients = {}


def handle_client(client_socket, username):
    """处理客户端连接"""
    try:
        clients[username] = client_socket
        logging.info(f"新用户加入: {username}")
        broadcast(f"{username} 加入了聊天室！", "系统")

        while True:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break
            logging.debug(f"{username} 发送消息: {message}")
            broadcast(message, username)
    except ConnectionResetError:
        logging.warning(f"{username} 连接被重置")
    finally:
        if username in clients:
            del clients[username]
            logging.info(f"{username} 断开连接")
            broadcast(f"{username} 退出了聊天室。", "系统")
        client_socket.close()


def broadcast(message, sender):
    """广播消息给所有客户端，附带时间戳"""
    timestamp = time.strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {sender}: {message}"

    for user, client in list(clients.items()):
        try:
            client.send(formatted_message.encode("utf-8"))
        except Exception:
            logging.warning(f"无法向 {user} 发送消息，移除该用户")
            del clients[user]


def start_server(host, port):
    """启动服务器"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host, port))
    except Exception as e:
        logging.error(f"无法绑定到 {host}:{port}，错误: {e}")
        return

    server.listen(5)
    logging.info(f"服务器启动，监听 {host}:{port}...")

    while True:
        client_socket, addr = server.accept()
        logging.info(f"新连接: {addr}")

        username = client_socket.recv(1024).decode("utf-8").strip()
        if not username or username in clients:
            logging.warning(f"用户名 {username} 被占用，拒绝连接")
            client_socket.send("USERNAME_TAKEN".encode("utf-8"))
            client_socket.close()
            continue

        threading.Thread(
            target=handle_client, args=(client_socket, username), daemon=True
        ).start()


class ChatClient:
    def __init__(self, root, host, port):
        self.root = root
        self.username = None

        # 连接服务器
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((host, port))
        except Exception:
            messagebox.showerror("错误", f"无法连接到服务器 {host}:{port}")
            root.quit()
            return

        # 获取用户名
        self.username = self.get_username()
        if not self.username:
            root.quit()
            return

        # 发送用户名
        self.client_socket.send(self.username.encode("utf-8"))
        response = self.client_socket.recv(1024).decode("utf-8")
        if response == "USERNAME_TAKEN":
            messagebox.showerror("错误", "用户名已被占用，请重试。")
            root.quit()
            return

        self.root.title(f"聊天室 - {self.username}")

        # 聊天显示框
        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state="disabled", width=50, height=15
        )
        self.chat_area.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

        # 输入框
        self.text_input = tk.Text(root, height=4, width=40)
        self.text_input.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # 按钮框（用于垂直排列按钮）
        self.button_frame = tk.Frame(root)
        self.button_frame.grid(
            row=1, column=1, rowspan=2, padx=5, pady=5, sticky="nsew"
        )

        # 发送按钮
        self.send_button = tk.Button(
            self.button_frame, text="发送", command=self.send_message
        )
        self.send_button.pack(fill="both", expand=True)

        # 清空按钮
        self.clear_button = tk.Button(
            self.button_frame, text="清空", command=self.clear_input
        )
        self.clear_button.pack(fill="both", expand=True)

        # 绑定回车键
        self.text_input.bind("<Return>", lambda event: self.send_message())

        # 启动接收消息的线程
        self.receive_thread = threading.Thread(
            target=self.receive_messages, daemon=True
        )
        self.receive_thread.start()

        # 调整布局
        root.grid_rowconfigure(0, weight=3)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=0)
        root.grid_columnconfigure(0, weight=4)
        root.grid_columnconfigure(1, weight=1)

    def get_username(self):
        """获取用户名"""
        return simpledialog.askstring("用户名", "请输入您的用户名：")

    def send_message(self):
        """发送消息"""
        message = self.text_input.get("1.0", tk.END).strip()
        if message:
            try:
                self.client_socket.send(message.encode("utf-8"))
                self.text_input.delete("1.0", tk.END)
            except Exception:
                messagebox.showerror("错误", "无法发送消息，服务器可能已断开。")

    def clear_input(self):
        """清空输入框"""
        self.text_input.delete("1.0", tk.END)

    def receive_messages(self):
        """接收消息"""
        while True:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                if not message:
                    break
                self.display_message(message)
            except Exception:
                messagebox.showerror("错误", "连接丢失。")
                self.root.quit()
                return

    def display_message(self, message):
        """显示消息"""
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state="disabled")
        self.chat_area.yview(tk.END)


def start_client(host, port):
    root = tk.Tk()
    ChatClient(root, host, port)
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Python Chat Application")

    parser.add_argument(
        "--mode",
        choices=["server", "client"],
        default="client",
        help="运行模式: server (服务端) 或 client (客户端)，默认: client",
    )
    parser.add_argument("--host", type=str, required=True, help="IP 地址")
    parser.add_argument("--port", type=int, required=True, help="端口")

    # 关于模式
    #   1. 客户端模式 --mode client
    #   2. 服务端模式 --mode client
    # 缺省时默认为客户端模式

    # 关于端口
    # 客户端的端口要求和服务端的端口保持一致，才能顺利连接，例如 --port 5555
    # 如果在远程服务器上部署，则需要在服务器的防火墙中开启相应端口

    # 关于host
    # 可以完全在本地测试，此时客户端和服务端都使用 --host 127.0.0.1
    # 如果需要在远程服务器上部署，那么
    #   1. 对于服务端，需要监听任何ip，使用 --host 0.0.0.0
    #   2. 对于客户端，需要使用服务器的公网ip，并访问指定端口，例如 --host xxx.xxx.xxx.xxx

    args = parser.parse_args()
    if args.mode == "server":
        start_server(args.host, args.port)
    else:
        start_client(args.host, args.port)


if __name__ == "__main__":
    main()
