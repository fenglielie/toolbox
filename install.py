#!/usr/bin/env python3

import os
import shutil
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


def copy_files(py_files, install_dir, force_overwrite, keep_ext):
    os.makedirs(install_dir, exist_ok=True)
    seen = set()

    for src_path in py_files:
        base_name = os.path.splitext(os.path.basename(src_path))[0]
        filename = base_name + ".py" if keep_ext else base_name
        dest_path = os.path.join(install_dir, filename)

        if filename in seen and not force_overwrite:
            print(f"Skipped duplicate: {filename}")
            continue

        if os.path.exists(dest_path) and not force_overwrite:
            print(f"Skipped existing file: {dest_path}")
            continue

        shutil.copy2(src_path, dest_path)
        seen.add(filename)
        print(f"Copied: {src_path} -> {dest_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Install all .py files into a directory"
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default=".",
        help="Directory to search for .py files (default = .)",
    )
    parser.add_argument(
        "--install-dir",
        type=str,
        required=True,
        help="Directory to copy .py files to (flat)",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Overwrite files with the same name"
    )
    parser.add_argument(
        "--keep-ext",
        action="store_true",
        default=(os.name == "nt"),
        help="Keep .py extension in copied filenames (default: True on Windows, False on Unix)",
    )
    args = parser.parse_args()

    py_files = find_py_files(args.source_dir, exclude_dir=args.install_dir)
    copy_files(py_files, args.install_dir, args.force, args.keep_ext)


if __name__ == "__main__":
    main()
