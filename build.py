import os
import subprocess


def package_script(script_path, build_dir, output_dir):
    """使用 PyInstaller 打包脚本为单文件可执行文件"""
    command = [
        "pyinstaller",
        "--distpath",
        output_dir,  # 指定可执行文件输出路径
        "--workpath",
        build_dir,  # 指定统一的临时构建文件夹
        "--specpath",
        build_dir,  # .spec 文件路径
        "--onefile",  # 打包为单文件
        "--noconfirm",  # 不提示覆盖确认
        script_path,
    ]
    subprocess.run(command, check=True)


def main():
    # 定义 build 和 out 目录
    project_dir = os.path.abspath(".")
    build_dir = os.path.join(project_dir, "build")
    output_dir = os.path.join(project_dir, "out")
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # 遍历当前目录的子文件夹
    for root, dirs, files in os.walk(project_dir):
        # 忽略当前目录下的脚本，只考虑子文件夹中的脚本
        if root == project_dir:
            continue

        for file in files:
            if file.endswith(".py") and "test" not in file:
                script_path = os.path.join(root, file)
                script_name = os.path.splitext(file)[0]

                # 打包脚本
                print(f"Packaging {script_name} from {root}...")
                package_script(script_path, build_dir, output_dir)

    print("All scripts packaged successfully.")


if __name__ == "__main__":
    main()
