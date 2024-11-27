#!/usr/bin/env python3

import os
import subprocess
import logging
import argparse
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed


LOG_COLORS = {
    "DEBUG": "\033[34m",  # blue
    "INFO": "\033[0m",  # reset # 实际没有使用这个等级
    "WARNING": "\033[33m",  # yellow # 实际没有使用这个等级
    "ERROR": "\033[31m",  # red
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        color = LOG_COLORS.get(record.levelname, "\033[0m")
        return f"{color}{super().format(record)}\033[0m"


def clean_aux_directory(root_dir):
    """
    清理 root_dir 及其子目录中的 .aux/ 文件夹。
    如果 .aux/ 文件夹不存在，不会报错。
    """
    for subdir, _, _ in os.walk(root_dir, topdown=True):
        aux_dir_path = os.path.join(subdir, ".aux").replace("\\", "/")
        if os.path.exists(aux_dir_path) and os.path.isdir(aux_dir_path):
            try:
                shutil.rmtree(aux_dir_path)
                logging.debug(f"Deleted: {aux_dir_path}")
            except Exception as e:
                logging.error(f"Failed to delete {aux_dir_path}: {e}")


def run_compile_task(task):
    # 获取任务参数
    tex_file = task["tex_file"]
    subdir = task["subdir"]
    engine = task["engine"]

    # 临时目录和输出目录
    out_dir = subdir
    aux_dir = os.path.abspath(os.path.join(subdir, ".aux")).replace("\\", "/")

    # 构造latexmk命令参数
    latex_full_command = [
        "latexmk",
        "-file-line-error",
        "-halt-on-error",
        "-interaction=nonstopmode",
        "-synctex=1",
        f"-{engine}",
        f"-auxdir={aux_dir}",
        f"-outdir={out_dir}",
        tex_file,
    ]

    logging.debug(f"Compiling {tex_file} ({engine})")
    logging.debug(f"Full command: {' '.join(latex_full_command)}")

    start_time = time.time()
    task_result = task.copy()
    try:
        # 运行latexmk命令
        result = subprocess.run(
            latex_full_command,
            cwd=subdir,  # 切换到对应目录中
            capture_output=True,  # 获取输出
            timeout=120,  # 设置超时时间
        )

        if result.returncode == 0:
            logging.debug(f"Successfully compiled {tex_file}")
            task_result.update(
                {
                    "success": True,
                    "elapsed_time": time.time() - start_time,
                }
            )

        else:
            logging.error(f"Failed to compile {tex_file}")
            task_result.update(
                {
                    "success": False,
                    "elapsed_time": time.time() - start_time,
                    "error_msg": result.stderr.decode("utf-8"),
                    "full_command": latex_full_command,
                }
            )

    except subprocess.TimeoutExpired:
        logging.error(f"Compilation of {tex_file} timed out.")
        task_result.update(
            {
                "success": False,
                "elapsed_time": time.time() - start_time,
                "error_msg": "Compilation timed out.",
                "full_command": latex_full_command,
            }
        )
    except Exception as e:
        logging.error(f"Error during compilation of {tex_file}: {e}")
        task_result.update(
            {
                "success": False,
                "elapsed_time": time.time() - start_time,
                "error_msg": f"{e}",
                "full_command": latex_full_command,
            }
        )

    return task_result


def run_compile_tasks(tasks):
    """
    执行编译任务
    """

    task_nums = len(tasks)
    task_cnt = 0
    task_results = []

    # 并行地执行任务
    print(f"Processing {len(tasks)} tasks in parallel...")

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(run_compile_task, task): task for task in tasks}
        for future in as_completed(futures):
            try:
                task_result = future.result()
                task_results.append(task_result)

                # 立刻展示当前任务的信息
                show_current_compile_result(task_result, task_nums, task_cnt)
            except Exception as e:
                logging.error(f"Error running task: {futures[future][0]} ({e})")

            task_cnt += 1

    return task_results


def generate_compile_tasks(root_dir, default_engine):
    """
    生成编译任务列表
    """

    def is_main_tex_file(tex_file_path):
        """检测tex文件是否是主文件"""
        try:
            with open(tex_file_path, "r", encoding="utf-8") as f:
                content = f.read()
                return "\\documentclass" in content
        except Exception as e:
            logging.error(f"Error reading {tex_file_path}: {e}")
            return False

    def get_tex_engine(tex_file_path, default_engine):
        """检测tex文件适用的编译引擎"""

        try:
            # check shebang
            with open(tex_file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line.startswith("% !TEX"):
                    first_line = first_line.strip()
                    logging.debug(f"Found shebang in {tex_file_path}: {first_line}")
                    if "xelatex" in first_line:
                        return "xelatex"
                    elif "pdflatex" in first_line:
                        return "pdflatex"
                    elif "lualatex" in first_line:
                        return "lualatex"

            # use xelatex if found ctex before \begin{document}
            with open(tex_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if r"\begin{document}" in line:
                        break
                    if "ctex" in line:
                        logging.debug(f"Found 'ctex' in {tex_file_path}: {line}")
                        return "xelatex"

        except Exception as e:
            logging.error(f"Error reading {tex_file_path}: {e}")
            return default_engine

        return default_engine

    tasks = []
    SKIP_DIRS = [".git", ".aux"]
    for subdir, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]  # 去除.git/等子文件夹

        # 初步筛选 .tex 后缀的文件
        tex_file_list = [f for f in files if f.endswith(".tex")]
        for tex_file_item in tex_file_list:
            # 获取主tex文件的完整路径
            tex_file = os.path.abspath(os.path.join(subdir, tex_file_item)).replace(
                "\\", "/"
            )
            if is_main_tex_file(tex_file):
                # 获取对应的编译引擎
                engine = get_tex_engine(tex_file, default_engine)
                if engine == "pdflatex":
                    engine = "pdf"

                # 生成单独的一个构建任务（字典，包括主文件完整路径，对应文件夹，编译引擎）
                tasks.append(
                    {
                        "tex_file": tex_file,
                        "subdir": subdir,
                        "engine": engine,
                    }
                )

    return tasks


def show_current_compile_result(task_result, task_nums, task_cnt):

    tex_file = task_result["tex_file"]
    engine = task_result["engine"]
    elapsed_time = task_result["elapsed_time"]

    if task_result["success"]:
        print(
            f"\033[32m [✓] ({task_cnt+1}/{task_nums}) {tex_file} ({engine}) ({elapsed_time:.2f}s)\033[0m"
        )

    else:
        print(
            f"\033[31m [x] ({task_cnt+1}/{task_nums}) {tex_file} ({engine}) ({elapsed_time:.2f}s)\033[0m"
        )
        print(f"\033[35mfull_command:\n{task_result['full_command']}\033[0m")
        print(f"\033[35merror_msg:\n{task_result['error_msg']}\033[0m")


def show_compile_results(tasks_results):
    """
    显示编译结果
    """

    sucess_cnt = 0
    failed_cnt = 0

    for task_result in tasks_results:
        if task_result["success"]:
            sucess_cnt += 1
        else:
            failed_cnt += 1

    print(f"Succeeded: {sucess_cnt}   Failed: {failed_cnt}")

    if failed_cnt == 0:
        return

    print("Failed tasks:")
    for task_result in tasks_results:
        if not task_result["success"]:
            print(
                f"\033[31m [x] {task_result['tex_file']} ({task_result['engine']})\033[0m"
            )
            print(f"\033[35mfull_command:\n{task_result['full_command']}\033[0m")
            print(f"\033[35merror_msg:\n{task_result['error_msg']}\033[0m")


def parse_args():
    """解析命令行参数"""

    parser = argparse.ArgumentParser(
        description="Compile or clean .tex files in the given directory."
    )
    parser.add_argument(
        "root_dir", type=str, help="The root directory to search for .tex files."
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["clean", "compile", "both"],
        default="compile",
        help="Choose the operation mode: 'clean' to clean .aux files, 'compile' to compile .tex files, or 'both' to clean and compile (default: compile).",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--engine",
        type=str,
        choices=["xelatex", "pdflatex", "lualatex"],
        default="xelatex",
        help="Set the default LaTeX engine (default: xelatex).",
    )

    return parser.parse_args()


def main():
    # 解析命令行参数
    args = parse_args()

    root_dir = args.root_dir
    mode = args.mode
    default_engine = args.engine

    # 初始化日志
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter("%(message)s"))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else logging.INFO)

    # 展示主要的选项信息
    logging.debug(f"Root directory: {root_dir}")
    logging.debug(f"Mode: {mode}")
    logging.debug(f"Default engine: {default_engine}")

    if mode in ["clean", "both"]:
        # 需要清理所有的.aux/文件夹
        clean_aux_directory(root_dir)

    if mode in ["compile", "both"]:
        # 生成编译任务列表
        tasks = generate_compile_tasks(root_dir, default_engine)
        # 执行编译任务
        tasks_results = run_compile_tasks(tasks)
        # 展示编译结果
        show_compile_results(tasks_results)


if __name__ == "__main__":
    main()
