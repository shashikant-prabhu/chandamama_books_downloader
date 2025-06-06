"""
Crawls chandamama.in starting from the story page, collects links
containing englishview.php (which serve PDF files), and downloads
them. PDFs are stored in <output>/YEAR/filename.pdf.

This script respects a simple breadth-first crawl limited to the
chandamama.in domain.
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from collections import deque

BASE_URL = "https://www.chandamama.in/story/"


def crawl_and_download(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
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
            resp = session.get(url, timeout=10)
        except Exception as exc:
            print(f"Failed to fetch {url}: {exc}")
            continue
        if resp.status_code != 200:
            print(f"Skip {url}: status {resp.status_code}")
            continue
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            link = urljoin(url, a['href'])
            parsed = urlparse(link)
            if parsed.netloc != base_netloc:
                continue
            if 'englishview.php' in parsed.path and 'file=' in parsed.query:
                pdf_links.add(link)
            elif link not in visited:
                queue.append(link)

    for link in sorted(pdf_links):
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        pdf_path = params.get('file', [None])[0]
        year = params.get('year', [None])[0]
        if not pdf_path or not year:
            continue
        filename = os.path.basename(pdf_path)
        year_dir = os.path.join(output_dir, year)
        os.makedirs(year_dir, exist_ok=True)
        pdf_url = urljoin(link, pdf_path)
        try:
            r = session.get(pdf_url, stream=True, timeout=10)
            if r.status_code == 200:
                out_file = os.path.join(year_dir, filename)
                with open(out_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Downloaded {out_file}")
            else:
                print(f"Failed to download {pdf_url}: status {r.status_code}")
        except Exception as exc:
            print(f"Error downloading {pdf_url}: {exc}")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) < 1:
        print("Usage: python download_chandamama_books.py <output-directory>")
        return 1
    output_dir = argv[0]
    crawl_and_download(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
