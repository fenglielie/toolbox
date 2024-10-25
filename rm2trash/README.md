# rm2trash

rm2trash is a custom Python script that moves files and directories to a "trash" directory (`~/.trash`) instead of permanently deleting them.

It provides a safer alternative to rm, giving users the ability to recover mistakenly deleted files and directories by organizing them with a timestamp-based folder structure.

## Features

- **Moves files to trash**: Sends files and directories to `~/.trash` instead of permanently deleting them.
- **Organized trash storage**: Creates a structured storage system within `~/.trash`:
  - First-level folders represent the year, month, and day.
  - Second-level folders are organized by time with a random number appended to avoid name collisions.
- **Optional interactivity**: Prompt confirmation for each deletion, or suppress it for batch operations.
- **Force delete and recursive options**: Includes `--force` and `--recursive` flags similar to the `rm` command.
- **Quiet mode**: Suppress output with the `--quiet` flag.

## Installation

1. Clone or download this script to your local machine.
   ```bash
   wget https://raw.githubusercontent.com/fenglielie/scripts/refs/heads/main/rm2trash/rm2trash.py -O rm2trash
   ```
2. Ensure the script has executable permissions.
   ```bash
   chmod +x rm2trash
   ```
3. Move the script to a directory in your `$PATH` for global access.
   ```bash
   sudo mv rm2trash /usr/local/bin/
   # or
   mv rm2trash ~/.local/bin
   ```

### Dependencies

`rm2trash` is written in Python3 and relies on built-in modules. No additional dependencies are required.

## Usage

The general syntax for `rm2trash` is as follows:

```bash
rm2trash [options] <file1> <file2> ...
```

### Options

- `-f`, `--force`: Ignore nonexistent files and arguments, and never prompt.
- `-i`, `--interactive`: Prompt before every removal.
- `-r`, `--recursive`: Remove directories and their contents recursively.
- `-q`, `--quiet`: Suppress output.

### Example Commands

1. **Basic deletion**:
   ```bash
   rm2trash file.txt
   ```
   Moves `file.txt` to the trash with detailed output.

2. **Suppress output**:
   ```bash
   rm2trash -q file.txt
   ```

3. **Interactive deletion**:
   ```bash
   rm2trash -i file.txt
   ```
   Prompts for confirmation before each deletion.

4. **Recursive deletion**:
   ```bash
   rm2trash -r folder/
   ```
   Moves `folder/` and all its contents to trash, organizing them within a new timestamped directory.

5. **Force deletion without prompt**:
   ```bash
   rm2trash -f nonexistentfile.txt
   ```

### Recovering Files

To recover files, simply navigate to the `~/.trash` directory and locate the date and time-stamped folder containing the files.

## Notes

- The `~/.trash` directory is created automatically if it does not exist.
- Files and directories are organized to avoid name collisions.
