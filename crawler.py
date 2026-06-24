import requests
from bs4 import BeautifulSoup
from urllib.parse import urldefrag, urljoin
from collections import deque
import time


def crawl_seed(seed_url: str, exclude_patterns: list | None = None, max_pages: int = 50):
    """
    Crawls a single seed URL and returns all the gathered links related to the documentation
    """
    seed_url = seed_url if seed_url.endswith('/') else seed_url + '/'
    exclude_patterns = exclude_patterns or []

    queue = deque([seed_url])
    visited_urls = set()
    to_scrape_urls = set()

    print(f"Starting crawling at {seed_url}")

    while queue and len(visited_urls) < max_pages:
        current_url = queue.popleft()
        current_url = current_url.rstrip('/')

        if any([pattern in current_url for pattern in exclude_patterns]):
            print(f"Skipping {current_url}")
            continue

        if current_url in visited_urls:
            continue

        # Same webpage with /index.html in URL
        if current_url.endswith("index.html") and current_url.split('/index.html')[0] in visited_urls:
            continue

        visited_urls.add(current_url)

        try:
            res = requests.get(current_url, headers={
                               "User-Agent": "Mozilla/5.0"}, timeout=5)

            if res.status_code != 200:
                res.raise_for_status()

            if 'text/html' not in res.headers.get('Content-Type', ''):
                raise Exception(
                    f"Expected 'text/html' as Content-Type, but got {res.headers.get('Content-Type')}")

            soup = BeautifulSoup(res.text, "html.parser")

            # Check for duplicate webpage through Canonical link
            canonical_tag = soup.find('link', rel="canonical")
            if canonical_tag and canonical_tag.get('href'):
                true_url = canonical_tag['href']
                true_url = true_url.rstrip('/')
                if true_url in to_scrape_urls:
                    continue

            to_scrape_urls.add(current_url)

            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(res.url, link['href'])

                # Remove jump links within the same document to prevent scraping of same document
                clean_url, _ = urldefrag(absolute_url)
                clean_url = clean_url.rstrip('/')

                if clean_url.startswith(seed_url) and clean_url not in queue and clean_url not in visited_urls:
                    queue.append(clean_url)

        except Exception as e:
            print(f"Failed to crawl {current_url}: {e}")

        time.sleep(1)

    return to_scrape_urls


if __name__ == "__main__":
    print(crawl_seed("https://www.psc.edu/resources/bridges-2/user-guide/"))
