# SCRIPT USAGE

## install.py

`install.py` recursively collects all `.py` files from the source directory (`--source-dir`, default: current directory) and copies them into a single destination directory specified by `--install-dir` (default: `~/.local/scripts/toolbox`). The original directory structure is not preserved.

```bash
python install.py --install-dir ~/.local/scripts/toolbox
```

To allow overwriting existing files in the destination directory, use the `-f` or `--force` option:

```bash
python install.py --install-dir ~/.local/scripts/toolbox --force
```

On Windows, it generates PowerShell launcher scripts for each Python script.
```pwsh
# Auto-generated launcher for xxx.py
$scriptPath = Join-Path $PSScriptRoot "xxx.py"
python $scriptPath @args
```
