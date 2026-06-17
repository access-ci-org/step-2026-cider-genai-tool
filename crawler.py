import requests
from bs4 import BeautifulSoup
from urllib.parse import urldefrag, urljoin
from collections import deque
import time


def get_all_document_links(seed_url, max_pages=50):
    """
    Fetch all the links available in the document
    """

    # Check for resolved link
    response = requests.get(
        seed_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
    if response.status_code != 200:
        print(
            f"Warning: URL {seed_url} is broken or unreachable (HTTP {response.status_code})")
        return []

    seed_url = response.url

    queue = deque([seed_url])
    visited_urls = set()
    to_scrape_urls = set()

    print(f"Starting crawling at {seed_url}")

    while queue and len(visited_urls) < max_pages:
        current_url = queue.popleft()
        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        try:
            res = requests.get(current_url, headers={
                               "User-Agent": "Mozilla/5.0"}, timeout=5)

            if res.status_code != 200:
                res.raise_for_status()

            if 'text/html' not in res.headers.get('Content-Type'):
                raise Exception(
                    f"Expected 'text/html' as Content-Type, but got {res.headers.get('Content-Type')}")

            soup = BeautifulSoup(res.text, "html.parser")

            # Check for duplicate webpage through Canonical link
            canonical_tag = soup.find('link', rel="canonical")
            if canonical_tag and canonical_tag.get('href'):
                true_url = canonical_tag['href']
                if true_url in to_scrape_urls:
                    continue

            to_scrape_urls.add(current_url)

            for link in soup.find_all('a'):
                absolute_url = urljoin(current_url, link['href'])
                clean_url, _ = urldefrag(absolute_url)
                if clean_url.startswith(seed_url) and clean_url not in queue and clean_url not in visited_urls:
                    queue.append(clean_url)

        except Exception as e:
            print(f"Failed to crawl {current_url}: {e}")

        time.sleep(1)

    return to_scrape_urls
