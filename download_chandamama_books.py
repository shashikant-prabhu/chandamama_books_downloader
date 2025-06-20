"""
Crawls chandamama.in starting from the story page, collects links
containing ``englishview.php`` (which serve PDF files), and downloads
them.

Provide a year to limit which files are fetched. Downloads are placed
in ``<output_root>/chandamama_books_<year>/``.

This script respects a simple breadth-first crawl limited to the
chandamama.in domain.
"""

import os
import sys
import logging
from collections import deque
from urllib.parse import parse_qs, urljoin, urlparse
from typing import Iterable, List
import argparse

logger = logging.getLogger(__name__)

import requests
from bs4 import BeautifulSoup

TIMEOUT = 120  # seconds
EST_SPEED_BYTES = 1024 * 1024  # 1MB/s used for rough time estimate

BASE_URL = "https://www.chandamama.in/story/"


def collect_pdf_links(year: str) -> List[str]:
    """Return a sorted list of Chandamama English PDF links for *year*."""
    session = requests.Session()
    visited = set()
    queue = deque([BASE_URL])
    pdf_links = set()

    base_netloc = urlparse(BASE_URL).netloc

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        try:
            resp = session.get(url, timeout=TIMEOUT)
        except Exception as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            continue
        if resp.status_code != 200:
            logger.warning("Skip %s: status %s", url, resp.status_code)
            continue
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            link = urljoin(url, a['href'])
            parsed = urlparse(link)
            if parsed.netloc != base_netloc:
                continue
            if '/hindi/' in parsed.path:
                continue
            if '/story/' in parsed.path and f'/story/{year}/' not in parsed.path:
                continue
            if 'englishview.php' in parsed.path and 'file=' in parsed.query:
                params = parse_qs(parsed.query)
                link_year = params.get('year', [None])[0]
                pdf_path = params.get('file', [""])[0]
                if link_year == year and '/english/' in pdf_path:
                    pdf_links.add(link)
            elif link not in visited:
                queue.append(link)

    return sorted(pdf_links)


def download_pdfs(links: Iterable[str], base_dir: str, year: str) -> None:
    """Download all *links* into *base_dir*."""
    output_dir = os.path.join(base_dir, f"chandamama_books_{year}")
    os.makedirs(output_dir, exist_ok=True)
    session = requests.Session()

    for link in links:
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        pdf_path = params.get('file', [None])[0]
        link_year = params.get('year', [None])[0]
        if not pdf_path or link_year != year:
            continue
        filename = os.path.basename(pdf_path)
        pdf_url = urljoin(link, pdf_path)
        try:
            r = session.get(pdf_url, stream=True, timeout=TIMEOUT)
            if r.status_code == 200 and r.headers.get("content-type", "").lower().startswith("application/pdf"):
                size = int(r.headers.get('content-length', 0))
                if size:
                    est_seconds = size / EST_SPEED_BYTES
                    logger.info(
                        "Downloading %s (~%.2f MB, est. %.1fs)",
                        filename,
                        size / 1024 / 1024,
                        est_seconds,
                    )
                else:
                    logger.info("Downloading %s (size unknown)", filename)
                out_file = os.path.join(output_dir, filename)
                with open(out_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.info("Downloaded %s", out_file)
            else:
                logger.warning(
                    "Failed to download %s: status %s", pdf_url, r.status_code
                )
        except Exception as exc:
            logger.error("Error downloading %s: %s", pdf_url, exc)


def crawl_and_download(base_dir: str, year: str) -> None:
    """Collect links for *year* and download them."""
    links = collect_pdf_links(year)
    if not links:
        logger.warning("No PDFs found for %s", year)
        return
    download_pdfs(links, base_dir, year)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Download Chandamama PDFs or list their URLs"
    )
    parser.add_argument("year", help="Year of the issues to download")
    parser.add_argument(
        "base_dir",
        help="Directory where PDFs should be stored (used for download mode)",
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list the PDF URLs instead of downloading",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.list_only:
        links = collect_pdf_links(args.year)
        for link in links:
            print(link)
    else:
        crawl_and_download(args.base_dir, args.year)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
