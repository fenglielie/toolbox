import os
import argparse
import nbformat
from nbconvert import PythonExporter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import logging
import sys


def convert_ipynb_to_py(ipynb_path):
    """Convert Jupyter Notebook to Python script."""
    try:
        with open(ipynb_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        exporter = PythonExporter()
        source, _ = exporter.from_notebook_node(nb)
        return source
    except Exception as e:
        logging.warning(f"Failed to convert {ipynb_path}: {e}")
        return None


def collect_source_code(root_dir, export_dir=None):
    """Collect source code from all student folders."""
    student_files = {}
    found_any_file = False  # Global check: Any code files found?

    for student in os.listdir(root_dir):
        student_path = os.path.join(root_dir, student)
        if not os.path.isdir(student_path):
            continue

        logging.info(f"Processing student: {student}")
        student_content = []
        found_files = False  # Check if this student has code files

        for root, _, files in os.walk(student_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                content = None

                if ext == ".ipynb":
                    content = convert_ipynb_to_py(file_path)
                elif ext in (".py", ".m"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except:
                        try:
                            with open(file_path, "r", encoding="gbk") as f:
                                content = f.read()
                        except Exception as e:
                            logging.warning(f"Cannot read {file_path}: {e}")
                            continue

                if content:
                    found_any_file = True
                    found_files = True
                    rel_path = os.path.relpath(file_path, student_path)
                    student_content.append(f"=== {rel_path} ===\n{content}")

        if student_content:
            student_files[student] = "\n\n".join(student_content)

            if export_dir:
                os.makedirs(export_dir, exist_ok=True)
                with open(
                    os.path.join(export_dir, f"{student}.txt"), "w", encoding="utf-8"
                ) as f:
                    f.write(student_files[student])

        if not found_files:
            logging.warning(f"No source files found for student: {student}")

    if not found_any_file:
        logging.warning("No source files found in the provided directory.")

    return student_files


def detect_plagiarism(student_files, threshold, export_dir=None):
    """Check for plagiarism using TF-IDF and cosine similarity."""
    if not student_files:
        logging.warning("No student files to compare.")
        return

    students = list(student_files.keys())
    documents = list(student_files.values())

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    cos_sim = cosine_similarity(tfidf_matrix)

    results = []
    for i in range(len(students)):
        for j in range(i + 1, len(students)):
            if cos_sim[i][j] >= threshold:
                results.append(
                    {
                        "Student A": students[i],
                        "Student B": students[j],
                        "Similarity": cos_sim[i][j],
                    }
                )

    if results:
        df = pd.DataFrame(results).sort_values(by="Similarity", ascending=False)

        print("\n--- Plagiarism Detection Results ---")
        print(df.to_string(index=False))

        if export_dir:
            result_file = os.path.join(export_dir, "plagiarism_results.csv")
            df.to_csv(result_file, index=False)
            logging.info(f"Results saved to {result_file}")
    else:
        print("\nNo suspicious similarities detected.")


def setup_logger(verbosity):
    """Configure logging level based on verbosity count (-v)."""
    if verbosity == 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(
        level=level, format="[{levelname}] {message}", style="{", stream=sys.stdout
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Plagiarism Detection Tool")
    parser.add_argument("root_dir", help="Root directory containing student folders")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Similarity threshold (default: 0.8)",
    )
    parser.add_argument(
        "--export",
        help="Directory to save intermediate files and results (default: no export)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (use -v for INFO, -vv for DEBUG)",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    setup_logger(args.verbose)

    logging.info("Start data collection ...")
    student_files = collect_source_code(args.root_dir, args.export)

    logging.info("Start plagiarism detection ...")
    detect_plagiarism(student_files, args.threshold, args.export)


if __name__ == "__main__":
    main()
