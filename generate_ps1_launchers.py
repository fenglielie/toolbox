import os
import argparse

EXCLUDES = {
    "generate_ps1_launchers.py",
    "install.py",
    "test.py",
    "demo.py",
}


def find_py_files(root_dir, exclude_dir):
    py_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.abspath(exclude_dir) in os.path.abspath(dirpath):
            continue
        for filename in filenames:
            if filename.endswith(".py") and filename not in EXCLUDES:
                py_files.append(os.path.join(dirpath, filename))
    return py_files


def make_relative_path(from_dir, to_file):
    rel_path = os.path.relpath(to_file, from_dir)
    return rel_path.replace("\\", "/")


def generate_ps1_content(py_path, ps1_dir, use_abs):
    if use_abs:
        source_path = os.path.abspath(py_path).replace("\\", "/")
        return f"""\
# Auto-generated launcher for {os.path.basename(py_path)}
$scriptPath = "{source_path}"
python $scriptPath @args
"""
    else:
        rel_path = make_relative_path(ps1_dir, py_path)
        return f"""\
# Auto-generated launcher for {os.path.basename(py_path)}
$scriptPath = Join-Path $PSScriptRoot "{rel_path}"
python $scriptPath @args
"""


def generate_all_ps1_scripts(source_dir, ps1_dir, use_abs_path=False, force=False):
    source_dir = os.path.abspath(source_dir)
    ps1_dir = os.path.abspath(ps1_dir)
    os.makedirs(ps1_dir, exist_ok=True)

    py_files = find_py_files(source_dir, exclude_dir=ps1_dir)

    for py_file in py_files:
        base_name = os.path.splitext(os.path.basename(py_file))[0]
        ps1_filename = f"{base_name}.ps1"
        ps1_path = os.path.join(ps1_dir, ps1_filename)

        if os.path.exists(ps1_path) and not force:
            print(f"Skipped existing file: {ps1_path}")
            continue

        content = generate_ps1_content(py_file, ps1_dir, use_abs=use_abs_path)
        with open(ps1_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Generated: {ps1_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate PS1 launchers for Python scripts"
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default=".",
        help="Directory to search for .py files (default = .)",
    )
    parser.add_argument(
        "--ps1-dir",
        type=str,
        required=True,
        help="Directory to store generated .ps1 scripts",
    )
    parser.add_argument(
        "--use-abs-path", action="store_true", help="Use absolute path in .ps1 scripts"
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing .ps1 files"
    )
    args = parser.parse_args()

    generate_all_ps1_scripts(
        source_dir=args.source_dir,
        ps1_dir=args.ps1_dir,
        use_abs_path=args.use_abs_path,
        force=args.force,
    )


if __name__ == "__main__":
    main()
