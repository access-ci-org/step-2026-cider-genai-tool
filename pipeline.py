import requests
import json
from collections import deque
from typing import Optional
from crawler import crawl_seed
from fetch_cider import fetch_cider_resources
from scraper import scrape_content
import time


def load_config(file_path: str):
    with open(file_path, 'r') as fp:
        config = json.load(fp)

        return config


def crawl(info_resource_id, seed_url: str, crawler_settings: dict = {}):
    """
    Crawl webpages and gather all the relevant links to scrape the content from.
    """

    # If crawler_settings isn't provided, only scrape the given seed URL (e.g, user guide)
    if not crawler_settings:
        links = crawl_seed(seed_url)
        return {
            seed_url: links
        }

    config_seed_urls = crawler_settings.get("seed_urls", [])
    exclude_patterns = crawler_settings.get("exclude_patterns", [])
    max_pages_per_seed = crawler_settings.get("max_pages_per_seed", 50)

    additional_urls = []
    for url in config_seed_urls:
        response = requests.get(
            url, headers={"User-Agent": "Mozzila/5.0"}, timeout=5)

        if response.status_code == 200:
            additional_urls.append(response.url)
        else:
            print(
                f"Warning: User Guide URL {url} is broken or unreachable (HTTP {response.status_code})")
            log_error(
                info_resource_id, f"User Guide URL {url} is broken or unreachable (HTTP {response.status_code}).")

    queue = deque([seed_url, *additional_urls])

    crawled_urls = {}

    while queue:
        url = queue.popleft()
        crawled_urls[url] = crawl_seed(
            url, exclude_patterns=exclude_patterns, max_pages=max_pages_per_seed)

    return crawled_urls


def scrape(info_resource_id, to_visit_urls):
    """
    Gather links given URL, and scrapes their content.
    """

    VISITED_LOG_FILE = f"{info_resource_id.split('.')[0]}_visited_urls.txt"
    OUTPUT_DATA_FILE = f"{info_resource_id.split('.')[0]}_scraped_content.md"

    print(f"Found {len(to_visit_urls)} pages to scrape. Starting extraction...")

    with open(VISITED_LOG_FILE, 'w', encoding="utf-8") as log_file, open(OUTPUT_DATA_FILE, 'w', encoding="utf-8") as output_file:
        for current_url in to_visit_urls:
            print(f"Scraping content form {current_url}")

            content = scrape_content(current_url)

            if content:
                output_file.write(f"\n\n# URL: {current_url}\n\n{content}")
                log_file.write(f"{current_url}\n")
            else:
                log_file.write(
                    f"{current_url} - No readable content extracted (Skipped)\n")
                print(f"  -> Skipping (No readable content extracted)")

            time.sleep(1)

    print(f"Scraping completed! Data saved to {OUTPUT_DATA_FILE}")


def log_error(info_resource_id, error_message):
    ERROR_LOG_FILE = f"{info_resource_id.split('.')[0]}_error.txt"

    with open(ERROR_LOG_FILE, 'w', encoding="utf-8") as error_file:
        error_file.write(f"{error_message}\n")

    print("Error logged.")


def main():
    INFO_RESOURCE_ID = "granite.ncsa.access-ci.org"
    CONFIG_PATH = "./config.json"

    if CONFIG_PATH:
        config = load_config(CONFIG_PATH)
    else:
        config = {}

    # Fetch CiDeR record
    resource_details = fetch_cider_resources(
        info_resource_id=INFO_RESOURCE_ID
    )

    if not resource_details:
        print("No resources found.")
        log_error(INFO_RESOURCE_ID,
                  f"Resource {INFO_RESOURCE_ID} is not found in CiDeR database.")
        return

    # Save resource details
    with open(f"{INFO_RESOURCE_ID.split('.')[0]}_cider_info.json", 'w') as fp:
        json.dump(resource_details, fp, indent=4)

    cider_type = resource_details.get("cider_type", "")
    cider_resource_info = resource_details[cider_type.lower()]
    seed_url = cider_resource_info.get("user_guide_url", "")

    if seed_url:
        # Check if URL is active
        response = requests.get(
            seed_url, headers={"User-Agent": "Mozzila/5.0"}, timeout=5)

        if response.status_code == 200:
            seed_url = response.url
            crawler_settings = config.get("crawler_settings", {})
            to_visit_urls = crawl(INFO_RESOURCE_ID, seed_url,
                                  crawler_settings=crawler_settings)
            to_visit_urls = [link for link_set in list(
                to_visit_urls.values()) for link in link_set]
            scrape(INFO_RESOURCE_ID, to_visit_urls)

        else:
            print(
                f"Warning: User Guide URL {seed_url} is broken or unreachable (HTTP {response.status_code})")
            log_error(INFO_RESOURCE_ID,
                      f"User Guide URL {seed_url} is broken or unreachable (HTTP {response.status_code}).")
            return

    else:
        print("Warning: No User Guide URL found")
        log_error(INFO_RESOURCE_ID,
                  f"No User Guide URL exist in the CiDeR record.")
        return


if __name__ == "__main__":
    main()
