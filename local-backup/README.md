# 备份与回滚脚本 local-backup

该脚本用于自动备份指定的文件或文件夹到带时间戳的目录中，支持日志记录、日志轮替和备份轮替。用户可以选择执行备份或回滚操作，管理备份的数量，以确保备份空间的合理利用。

## 功能介绍

1. **备份**：将配置文件中指定的文件和文件夹复制到目标路径下带时间戳的文件夹中。
2. **回滚**：将最新的备份还原到原路径，覆盖原文件或文件夹。
3. **日志记录**：支持日志记录，采用日志轮替机制，可按大小自动生成日志文件备份。
4. **备份轮替**：在备份数量超过指定数量时，自动删除最旧的备份。

## 使用方法

### 基本用法

运行脚本时，使用 `--config` 参数指定配置文件路径，使用 `--log` 参数指定日志文件路径，以下是具体用法：

```bash
python local-backup.py --config path/to/config.json --log path/to/logfile.log
```

### 备份操作

执行备份操作，将指定文件和文件夹备份到带时间戳的目标文件夹中：

```bash
python local-backup.py --config path/to/config.json --log path/to/logfile.log
```

### 回滚操作

使用 `--rollback` 参数进行回滚，将最新的备份还原到源路径：

```bash
python local-backup.py --config path/to/config.json --log path/to/logfile.log --rollback
```

## 配置文件格式

配置文件需使用 JSON 格式，内容包括以下字段：

- `destination`：备份存放的目标目录。
- `max_backups`：保留的最大备份数量（默认10）。
- `backup_paths`：需要备份的文件或文件夹路径列表。

**示例配置文件 `config.json`：**

```json
{
    "destination": "/path/to/backup/folder",
    "max_backups": 10,
    "backup_paths": [
        "/path/to/file_or_folder1",
        "/path/to/file_or_folder2"
    ]
}
```
