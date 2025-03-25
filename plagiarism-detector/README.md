# 抄袭检测小工具


该工具可以用于检测学生提交的代码文件中的抄袭行为，支持分析 MATLAB（`.m`）、Python（`.py`）和Jupyter Notebook（`.ipynb`）三种代码文件。
通过计算代码之间的相似度来检测抄袭，使用 TF-IDF 和余弦相似度方法进行文本比对。


## 安装依赖

确保安装以下 Python 库：

```bash
pip install scikit-learn pandas nbconvert
```

## 使用说明

脚本的使用方法如下：

```bash
python plagiarism-detector.py <root_dir> [--threshold <threshold>] [--export <export_dir>] [-v]
```

- `<root_dir>`: 学生代码文件所在的根目录。该目录下应该包含各个学生的文件夹，每个学生的文件夹中包含其代码文件。
- `--threshold <threshold>`: 设置相似度阈值，用于判断两个学生的代码是否相似。默认值为 `0.8`。
- `--export <export_dir>`: 指定导出中间文件和最终结果的目录。默认情况下不会导出任何内容。
- `-v` 或 `--verbose`: 增加日志的详细级别，`-v` 显示 `INFO` 级别日志，`-vv` 显示 `DEBUG` 级别日志。（默认显示 `WARNING` 级别日志）

使用示例如下

1. 默认
```bash
python plagiarism-detector.py /path/to/student/folder
```

2. 调整相似度阈值，并导出中间文件和结果
```bash
python plagiarism-detector.py /path/to/student/folder --threshold 0.85 --export /path/to/export
```

3. 获取详细输出信息用于调试
```bash
python plagiarism_detector.py /path/to/student/folder -vv
```

若检测到抄袭，将在控制台中显示类似如下表格：
```
--- Plagiarism Detection Results ---
 Student A   Student B   Similarity
 student_1   student_2   0.85
 student_3   student_4   0.80
```

## 补充说明

1. 文件编码：对于不同编码格式的文件，脚本会依次尝试使用 UTF-8 和 GBK 编码进行读取。如果文件无法读取，将输出警告信息。
2. 文件格式支持：目前只支持 `.py`、`.m`、`.ipynb` 格式的代码文件，对于 `.ipynb` 通过自动转换为 `.py` 文件进行处理，对于其它格式的源文件暂不支持。
3. 相似度阈值：默认相似度阈值为 0.8，表示两个学生的代码相似度超过 80% 时，视为抄袭。可以通过命令行参数调整。
