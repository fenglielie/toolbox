#!/usr/bin/env python3

import datetime
import feedparser
import json
import urllib.parse
import urllib.request
import re
import os
import logging
import argparse
from typing import List, Dict, Any


def clean_text(text: str) -> str:
    """Clean up extra spaces, newlines, and remove special characters from text."""
    text = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    return re.sub(r'[\/:*?"<>|]', "_", text)  # Replace unsupported filename characters


def fetch_papers_from_arxiv_api(
    search_query: str, max_results: int, sort_by: str, sort_order: str, verbose: bool
) -> List[Dict[str, Any]]:
    """
    Retrieve research papers from the arXiv API with full query customization.

    Args:
        search_query (str): Custom arXiv query string.
        max_results (int): Maximum number of results to return.
        sort_by (str): Sorting parameter.
        sort_order (str): Sorting order.
        verbose (bool): Whether to display detailed debug information.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing paper information.
    """
    base_url = "http://export.arxiv.org/api/query"
    query_params = {
        "search_query": search_query,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    encoded_url = f"{base_url}?{urllib.parse.urlencode(query_params)}"

    if verbose:
        logging.debug(f"Generated API URL: {encoded_url}")

    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
        request = urllib.request.Request(encoded_url, headers=headers)

        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode("utf-8")
    except Exception as e:
        logging.error(f"Network error: {str(e)}")
        return []

    feed = feedparser.parse(response_data)
    if feed.bozo:
        logging.error(f"Feed parsing error: {feed.bozo_exception}")
        return []

    papers = []
    for entry in feed.entries:
        authors = getattr(entry, "authors", [])
        tags = getattr(entry, "tags", [])

        first_author = clean_text(authors[0].name.split()[-1]) if authors else "Unknown"

        paper = {
            "title": clean_text(getattr(entry, "title", "Untitled")),
            "authors": (
                ", ".join(clean_text(author.name) for author in authors)
                if authors
                else "Unknown authors"
            ),
            "first_author": first_author,
            "year": getattr(entry, "published", "")[:4],
            "summary": clean_text(getattr(entry, "summary", "")),
            "published": getattr(entry, "published", "")[:10],
            "link": getattr(entry, "link", "#"),
            "pdf_link": getattr(entry, "id", "").replace(
                "http://arxiv.org/abs/", "http://arxiv.org/pdf/"
            )
            + ".pdf",
            "tags": [tag.term for tag in tags] if tags else [],
            "comment": clean_text(getattr(entry, "arxiv_comment", "")),
        }
        papers.append(paper)

    if verbose:
        logging.debug(f"Fetched {len(papers)} papers from arXiv")

    return papers


def download_pdfs(
    papers: List[Dict[str, Any]],
    save_num: int,
    save_dir: str = "arxiv_pdfs",
    verbose: bool = False,
):
    """Download PDFs of selected papers and rename them accordingly."""

    if save_num > 0:
        os.makedirs(save_dir, exist_ok=True)

    save_num = min(save_num, 5, len(papers))  # Ensure we do not exceed available papers

    for paper in papers[:save_num]:
        pdf_url = paper["pdf_link"]
        filename = f"{paper['first_author']} - {paper['year']} - {paper['title']}.pdf"
        filepath = os.path.join(save_dir, filename)

        if os.path.exists(filepath):
            logging.info(f"File already exists: {filename}")
            continue

        try:
            logging.info(f"Downloading: {pdf_url}")
            if verbose:
                logging.debug(f"Saving to: {filepath}")

            urllib.request.urlretrieve(pdf_url, filepath)
            logging.info(f"Saved as: {filepath}")
        except Exception as e:
            logging.error(f"Download failed: {pdf_url}, Error: {str(e)}")


def save_to_json(data: List[Dict[str, Any]], filename: str, verbose: bool) -> None:
    """Save data as a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Successfully saved {len(data)} papers to {filename}")
    except Exception as e:
        logging.error(f"Error saving file: {str(e)}")


def generate_email_body(
    search_query: str, sort_by: str, sort_order: str, papers: List[Dict[str, Any]]
) -> str:
    """Generate a more visually appealing email body with plain text format."""

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    email_body = f"""\
Subject: [ArXiv {current_date}] {len(papers)} New Papers Found for "{search_query}"

Dear Researcher,

We have found the following {len(papers)} research papers based on your query.

Search Query: {search_query}
Sort By: {sort_by}
Sort Order: {sort_order}
Total Papers Found: {len(papers)}

==================================================

"""

    for i, paper in enumerate(papers, 1):
        email_body += f"""\
Paper {i}: {paper["title"]}
Published: {paper["published"]}
Authors: {paper["authors"]}

Summary: {paper["summary"][:500]}...
Link to Paper: {paper["link"]}
Download PDF: {paper["pdf_link"]}

--------------------------------------------------

"""

    email_body += """\
Best regards,
Your Automated Research Assistant
"""

    return email_body


def main():
    parser = argparse.ArgumentParser(description="Fetch and download papers from arXiv")

    parser.add_argument(
        "search_query", help="Custom arXiv search query (e.g., 'ti:deep learning')"
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=10,
        help="Number of papers to fetch (default: 10)",
    )
    parser.add_argument(
        "--sort_by",
        type=str,
        default="lastUpdatedDate",
        choices=["relevance", "submittedDate", "lastUpdatedDate"],
        help="Sorting method (default: lastUpdatedDate)",
    )
    parser.add_argument(
        "--sort_order",
        type=str,
        default="descending",
        choices=["ascending", "descending"],
        help="Sorting order (default: descending)",
    )

    parser.add_argument(
        "-d", "--dir", type=str, default="arxiv_pdfs", help="Directory to save PDFs"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="arxiv_papers.json",
        help="Output JSON file name",
    )
    parser.add_argument(
        "--download",
        type=int,
        default=0,
        help="Number of PDFs to download (default: 0)",
    )
    parser.add_argument(
        "--email",
        type=str,
        default="arxiv_email.txt",
        help="Output email body file name",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable detailed debugging output"
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    papers = fetch_papers_from_arxiv_api(
        args.search_query, args.num, args.sort_by, args.sort_order, args.verbose
    )

    if papers:
        save_to_json(papers, args.output, args.verbose)

        download_pdfs(papers, args.download, args.dir, args.verbose)

        # 生成邮件正文
        email_body = generate_email_body(
            args.search_query, args.sort_by, args.sort_order, papers
        )

        # 保存邮件正文到文件
        with open(args.email, "w", encoding="utf-8") as f:
            f.write(email_body)

        logging.info(f"Email body saved to {args.email}")

    else:
        logging.warning("No papers found. Check the query or network connection.")


if __name__ == "__main__":
    main()
