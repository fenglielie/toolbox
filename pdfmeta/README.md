# PDF Rename with CrossRef Metadata

This Python script automatically renames PDF files in a specified directory using metadata fetched from the [CrossRef API](https://api.crossref.org/).

Optionally, it can also append BibTeX entries to a `.bib` file.

## Features

- Extracts DOI from the first two pages of each PDF.
- Queries CrossRef for author, year, and title.
- Renames PDFs in the format:
  **`Author - Year - Title.pdf`**
- Handles multiple authors (`et al.`) or two-author cases (`A and B`).
- Optionally appends BibTeX entries to a `.bib` file.
- Skips renaming if metadata is incomplete.
- Logs progress with optional verbose mode.

## Requirements

- `requests`
- `PyPDF2`

Install dependencies with:

```bash
pip install requests PyPDF2
```

## Usage

```bash
./pdfmeta.py /path/to/pdfs [--verbose] [--bibtex output.bib]
```

Arguments

- `directory` — path to folder containing `.pdf` files.
- `--verbose` — show detailed logs.
- `--bibtex output.bib` — append BibTeX entries to `output.bib`.

## Example

```bash
./pdfmeta.py ./papers --verbose --bibtex myrefs.bib
```

This will rename all `.pdf` files in `./papers` and append BibTeX entries to `myrefs.bib`.
