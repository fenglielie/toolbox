# Python 邮件发送脚本 sendmail

该脚本用于在日常工作中简化邮件通知的需求，尤其在无法统一邮件工具的多系统环境下，可以跨平台使用，无论是 Linux 还是 Windows 系统都无需依赖其他邮件工具。只要网络可用，即可通过 Python 发送邮件。

## 使用说明

### 基本用法

1. 必须使用 `-s` 或 `--subject` 指定邮件主题。
2. 使用位置参数指定收件人邮箱。
3. 脚本默认从 `stdin` 读取邮件正文，可以在命令行输入正文内容，并使用回车 + `Ctrl+D` 结束输入。*（注意：单独 `Ctrl+D` 无法结束输入）*

> 在使用上尽量模仿系统中的 `mail` 命令。暂不支持附件发送功能。

### 可选用法

- 可以使用 `-m` 或 `--message` 指定邮件正文。
- 可以使用 `-a` 或 `--attach` 指定一个附件的路径，对于多个附件需要多次使用 `-a <file>`。
- 通过 `<` 或 `|` 管道输入文件内容作为邮件正文。

### 示例

- **通过命令行输入内容作为邮件正文**：
    ```bash
    python3 sendmail.py -s "subject" receiver@example.com
    <在命令行中输入正文内容，输入结束按回车 + Ctrl+D 发送>
    ```

- **通过 `<` 传递文件内容作为邮件正文**：
    ```bash
    python3 sendmail.py -s "subject" receiver@example.com < content.txt
    ```

- **通过 `|` 管道传递文件内容作为邮件正文**：
    ```bash
    cat content.txt | python3 sendmail.py -s "subject" receiver@example.com
    ```

- **通过 `-m` 选项指定邮件正文**：
    ```bash
    python3 sendmail.py -s "subject" -m "content" receiver@example.com
    ```

- **通过 `-a` 选项指定邮件附件**：
    ```bash
    python3 sendmail.py -s "subject" -m "content" -a attachment.pdf receiver@example.com
    ```

## 配置文件

脚本默认从 `mail-config.json` 中读取配置信息，如下所示：

```json
{
    "username": "xxxxxxxx@163.com",
    "password": "xxxxxxxxxxxxxxxx",
    "sender": "xxxxxxxx@163.com",
    "host": "smtp.163.com",
    "port": 465
}
```

- `username`：登录邮箱账户。
- `password`：专用客户端密码或授权码（通常不是邮箱登录密码）。
- `sender`：发件人邮箱地址。
- `host`：SMTP 服务器地址。
- `port`：SMTP 服务器端口（通常 SSL 为 `465`）。

> 注意：有的邮箱服务（如网易邮箱）需单独申请“客户端授权码”作为 `password`，需要参考邮箱服务商的具体要求。

### 自定义配置路径

可以通过 `--config` 选项指定配置文件路径，例如：
```bash
python3 sendmail.py -s "subject" -m "content" receiver@example.com --config ${HOME}/.config/mail-config.json
```
