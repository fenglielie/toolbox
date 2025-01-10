# FTP 文件上传脚本 ftp-upload

## 功能介绍

这个 Python 脚本用于简化本地文件或文件夹上传到FTP服务器的流程，
脚本可以读取配置文件，自动连接FTP服务器并上传文件或文件夹中的所有内容（不含隐藏文件夹），在 FTP 服务器上会自动创建不存在的目录。


## 使用示例

1. **上传文件**：

```bash
python3 ftp-upload.py -d "/remote/path" /local/path/to/file.txt
```

2. **上传文件夹**：（不会在 FTP 服务器上创建`folder/`文件夹）

```bash
python3 ftp-upload.py -d "/remote/path" /local/path/to/folder
```

3. **使用自定义配置文件上传**：

```bash
python3 ftp-upload.py -c custom-config.json -d "/remote/path" /local/path/to/file.txt
```

4. **上传文件到FTP服务器的根目录**：

```bash
python3 ftp-upload.py -d "/" /local/path/to/file.txt
```


## 配置文件

脚本默认从 `ftp-config.json` 中读取配置信息，如下所示：

```json
{
    "ftp_host": "ftp.example.com",
    "ftp_user": "your_username",
    "ftp_pass": "your_password",
    "ftp_encoding": "gbk"
}
```

- `ftp_host`: FTP服务器的地址（例如：ftp.example.com）
- `ftp_user`: FTP服务器的用户名
- `ftp_pass`: FTP服务器的密码
- `ftp_encoding`: FTP编码（gbk或utf-8）

可以通过 `--config` 选项指定配置文件路径，例如：

```bash
python3 ftp-upload.py -c custom-config.json -d "/remote/path" /local/path/to/file.txt
```


## 补充

注意：如果FTP服务器上存在同名文件，会自动用新文件进行覆盖！
