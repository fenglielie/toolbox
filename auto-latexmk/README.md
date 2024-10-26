# LaTeX 批量编译和清理脚本 auto-latexmk

本脚本用于批量编译和清理指定目录下的 LaTeX `.tex` 文件，支持根据文件内容选择适当的编译引擎。默认使用 `xelatex` 编译引擎，可通过命令行参数进行设置。

## 功能说明

- **编译模式**：递归查找指定目录下的主 `.tex` 文件（包含 `\documentclass` 的文件），根据 shebang 或文件内容自动选择合适的 LaTeX 编译引擎，并记录编译结果。
- **清理模式**：删除指定目录下的 `.aux` 文件夹及其内容。
- **支持的编译引擎**：`xelatex`, `pdflatex`, `lualatex`。

## 使用说明

### 基本用法

```bash
python auto-latexmk.py <root_dir> [--mode <mode>] [--log-level <level>] [--engine <engine>]
```

### 参数说明

- `root_dir`：需要查找 `.tex` 文件的根目录。
- `--mode`：操作模式，默认为 `compile`。
  - `clean`：清理 `.aux` 文件夹。
  - `compile`：编译 `.tex` 文件。
  - `both`：同时执行清理和编译操作。
- `--log-level`：日志级别，可选值为 `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`，默认 `WARNING`。
- `--engine`：默认编译引擎，支持 `xelatex`, `pdflatex`, `lualatex`，默认 `xelatex`。

### 示例

1. **编译指定目录中的 `.tex` 文件**：

   ```bash
   python auto-latexmk.py /path/to/directory --mode compile
   ```

2. **清理指定目录中的 `.aux` 文件夹**：

   ```bash
   python auto-latexmk.py /path/to/directory --mode clean
   ```

3. **先清理 `.aux` 文件夹再编译 `.tex` 文件，日志级别设置为 DEBUG**：

   ```bash
   python auto-latexmk.py /path/to/directory --mode both --log-level DEBUG
   ```

4. **指定默认编译引擎为 `pdflatex`**：

   ```bash
   python auto-latexmk.py /path/to/directory --engine pdflatex
   ```

## 实现原理

1. **编译引擎选择**：根据 `.tex` 文件首行的 shebang（例如`% !TEX program = xelatex`）或文件内容（检测头部是否存在 `ctex` ）自动选择编译引擎，否则使用默认的编译引擎。
2. **文件检测**：递归遍历文件夹，编译包含 `\documentclass` 的 `.tex` 文件。
3. **编译过程**：使用 `latexmk` 命令编译 `.tex` 文件，超时时间为 120 秒。
4. **结果统计**：记录成功和失败的文件数，并在控制台输出。
