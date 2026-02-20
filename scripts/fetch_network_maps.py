#! /usr/bin/env python3

# /// script
# dependencies = [
#   "requests<3",
#   "beautifulsoup4<5",
# ]
# ///

import sys
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

PAGE_URL = 'https://www.dvb.de/de-de/liniennetz/liniennetzplaene/'
BASE_URL = 'https://www.dvb.de'

# Matches the standard full Liniennetzplan (not city center excerpts)
STANDARD_JPG_PATTERN = re.compile(r'dvb_lnp_\d+_st_\d+_jpg\.jpg', re.IGNORECASE)
STANDARD_PDF_PATTERN = re.compile(r'dvb_lnp_\d+_st_\d+_pdf\.pdf', re.IGNORECASE)


def find_network_map_urls():
    """Scrape the DVB Liniennetzplan page for current standard plan URLs."""
    print(f"Fetching DVB Liniennetzplan page from {PAGE_URL}...", file=sys.stderr)

    response = requests.get(PAGE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    jpg_url = None
    pdf_url = None

    for link in soup.find_all('a', href=True):
        href = link['href']
        if not jpg_url and STANDARD_JPG_PATTERN.search(href):
            jpg_url = urljoin(BASE_URL, href)
        if not pdf_url and STANDARD_PDF_PATTERN.search(href):
            pdf_url = urljoin(BASE_URL, href)
        if jpg_url and pdf_url:
            break

    if not jpg_url:
        print("Error: Could not find standard Liniennetzplan JPG link", file=sys.stderr)
        sys.exit(1)

    if not pdf_url:
        print("Error: Could not find standard Liniennetzplan PDF link", file=sys.stderr)
        sys.exit(1)

    return jpg_url, pdf_url


def download_file(url, dest_path):
    """Download a file from URL to dest_path."""
    print(f"Downloading {url}...", file=sys.stderr)
    response = requests.get(url)
    response.raise_for_status()

    with open(dest_path, 'wb') as f:
        f.write(response.content)

    size_kb = len(response.content) / 1024
    print(f"  Saved to {dest_path} ({size_kb:.0f} KB)", file=sys.stderr)


def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)

    jpg_url, pdf_url = find_network_map_urls()

    download_file(jpg_url, os.path.join(data_dir, 'liniennetzplan.jpg'))
    download_file(pdf_url, os.path.join(data_dir, 'liniennetzplan.pdf'))

    print("\nDone! Generated:", file=sys.stderr)
    print("  - liniennetzplan.jpg", file=sys.stderr)
    print("  - liniennetzplan.pdf", file=sys.stderr)


if __name__ == "__main__":
    main()
