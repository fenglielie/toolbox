# README

A set of Python scripts:

- auto-latexmk
- ftp-upload
- latex-check
- local-backup
- progress-monitor
- rm2trash
- sendmail
- fetch-arxiv
- pychat
- plagiarism-detector

## USAGE

`install.py` is a simple script to copy all `.py` files found recursively under the current directory (`--source-dir`) into a single flat directory (`--install-dir`) without preserving subdirectory structure.

For example,
```bash
python install.py --install-dir scripts
```

If some files with the same name already exist in the destination folder, the script will skip copying those files by default.
To force overwrite existing files, use the `-f` or `--force` flag.

`generate_ps1_launchers.py` is a simple script to generate PowerShell launcher scripts for all `.py` files found recursively under the current directory (`--source-dir`) and saves them in a folder (`--ps1-dir`).

For example,
```bash
python generate_ps1_launchers.py --ps1-dir scripts
```

Launcher script demo
```pwsh
# Auto-generated launcher for pychat.py
$scriptPath = Join-Path $PSScriptRoot "../pychat/pychat.py"
python $scriptPath @args
```

The launcher scripts use relative paths to `.py` scripts by default.
To use absolute paths, add the `--use-abs-path` option.
```bash
python generate_ps1_launchers.py --ps1-dir scripts --use-abs-path
```
