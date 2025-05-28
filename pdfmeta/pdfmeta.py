import re
import logging
import argparse
import requests
from pathlib import Path
from PyPDF2 import PdfReader


def setup_logging(verbose=False):
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def extract_doi_from_pdf(pdf_path: Path) -> str | None:
    try:
        reader = PdfReader(pdf_path)
        text = "".join(page.extract_text() or "" for page in reader.pages[:2])
        logging.info(f"Extracted text from {pdf_path.name}")
        match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", text, re.I)
        if match:
            return match.group(0)
    except Exception as e:
        logging.error(f"Failed to read {pdf_path.name}: {e}")
    return None


def query_crossref_metadata(doi: str) -> tuple[list, int | None, str]:
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()["message"]
            authors = data.get("author", [])
            year = data.get("issued", {}).get("date-parts", [[None]])[0][0]
            title = data.get("title", ["UnknownTitle"])[0]
            logging.info(f"Queried metadata for DOI {doi}")
            return authors, year, title
    except Exception as e:
        logging.error(f"CrossRef query failed for DOI {doi}: {e}")
    return [], None, "UnknownTitle"


def download_bibtex_entry(doi: str) -> str | None:
    headers = {"Accept": "application/x-bibtex"}
    url = f"https://doi.org/{doi}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            logging.info(f"Retrieved BibTeX entry for DOI {doi}")
            return response.text
    except Exception as e:
        logging.error(f"BibTeX download failed for DOI {doi}: {e}")
    return None


def format_filename(authors: list, year: int | None, title: str) -> str:
    if not authors:
        author_str = "UnknownAuthor"
    else:
        if len(authors) == 1:
            author_str = authors[0].get("family", "Unknown")
        elif len(authors) == 2:
            author_str = f"{authors[0].get('family', 'Unknown')} and {authors[1].get('family', 'Unknown')}"
        else:
            author_str = f"{authors[0].get('family', 'Unknown')} et al."
    year_str = str(year) if year else "UnknownYear"
    title_str = re.sub(r'[\\/*?:"<>|]', "", title)[:100]
    return f"{author_str} - {year_str} - {title_str}.pdf"


def rename_pdf_with_format(pdf_path: Path, bibtex_path: Path | None = None):
    doi = extract_doi_from_pdf(pdf_path)
    if not doi:
        logging.warning(f"No DOI found in {pdf_path.name}")
        return

    authors, year, title = query_crossref_metadata(doi)

    if not authors or year is None or not title:
        logging.warning(f"Metadata incomplete for {pdf_path.name}, skipping rename")
        return

    new_name = format_filename(authors, year, title)
    new_path = pdf_path.parent / new_name
    try:
        pdf_path.rename(new_path)
        logging.info(f"Renamed: {pdf_path.name} -> {new_path.name}")
    except Exception as e:
        logging.error(f"Rename failed for {pdf_path.name}: {e}")
        return

    if bibtex_path:
        bibtex_entry = download_bibtex_entry(doi)
        if bibtex_entry:
            try:
                with open(bibtex_path, "a", encoding="utf-8") as f:
                    f.write(bibtex_entry.strip() + "\n\n")
                logging.info(f"BibTeX written to {bibtex_path}")
            except Exception as e:
                logging.error(f"Failed to write BibTeX to {bibtex_path}: {e}")


def batch_rename_pdfs_with_format(folder_path: str, bibtex_path: str | None = None):
    folder = Path(folder_path)
    bibtex_file = Path(bibtex_path) if bibtex_path else None
    if not folder.is_dir():
        logging.error(f"Folder not found: {folder}")
        return
    for pdf_file in folder.glob("*.pdf"):
        rename_pdf_with_format(pdf_file, bibtex_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Auto rename PDFs using CrossRef metadata, and optionally write BibTeX entries."
    )
    parser.add_argument("directory", help="Directory containing PDF files")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--bibtex", help="Path to output .bib file (append mode)")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    batch_rename_pdfs_with_format(args.directory, args.bibtex)
