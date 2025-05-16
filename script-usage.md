# SCRIPT USAGE

## install.py

`install.py` recursively collects all `.py` files from the source directory (`--source-dir`, default: current directory) and copies them into a single destination directory specified by `--install-dir`. The original directory structure is not preserved.

```bash
python install.py --install-dir scripts/
```

To allow overwriting existing files in the destination directory, use the `-f` or `--force` option:

```bash
python install.py --install-dir scripts/ --force
```

## generate_ps1_launchers.py

`generate_ps1_launchers.py` scans for all `.py` files under the source directory (`--source-dir`, default: current directory) and generates corresponding PowerShell launcher scripts in the specified directory (`--ps1-dir`).

```bash
python generate_ps1_launchers.py --ps1-dir scripts/
```

Each generated `.ps1` file is a wrapper for launching the corresponding Python script, like:

```pwsh
# Auto-generated launcher for xxx.py
$scriptPath = Join-Path $PSScriptRoot "../xxx/xxx.py"
python $scriptPath @args
```

By default, the launcher uses a relative path to locate the target script.
To generate launchers that use absolute paths, add the `--use-abs-path` flag:

```bash
python generate_ps1_launchers.py --ps1-dir scripts/ --use-abs-path
```
