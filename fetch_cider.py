import requests
from typing import Optional
import json
import trafilatura
from trafilatura.spider import focused_crawler
import time

BASE_URL = "https://operations-api.access-ci.org"


def fetch_cider_resources(info_resource_id: Optional[str] = None, organization_id: Optional[str] = None):
    """
    Fetch resource details
    """

    endpoint = "/wh2/integration_badges/v1/resources_full/"
    url = BASE_URL + endpoint

    params = {}
    if info_resource_id:
        params["info_resourceid"] = info_resource_id
    if organization_id:
        params["organization_id"] = organization_id

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        return results

    except Exception as e:
        print(e)
        return []


def filter_resource_info(resources):
    """
    Filter resource information and keep only the keys defined by REQUIRED_KEYS
    """

    REQUIRED_KEYS = ["cider_resource_id", "info_resourceid", "organization_id", "organization_name", "organization_url",
                     "user_guide_url", "cider_view_url", "cider_data_url"]

    data = []

    for resource in resources:
        info = {}
        for key in REQUIRED_KEYS:
            if key in resource:
                info[key] = resource[key]
            elif key == "cider_view_url":
                info[key] = f"https://cider.access-ci.org/public/resources/RDR_{str(resource['cider_resource_id']).zfill(6)}"
            elif key == "cider_data_url":
                info[
                    key] = f"https://operations-api.access-ci.org/wh2/cider/v1/cider_resource_id/{str(resource['cider_resource_id'])}"
            else:
                info[key] = None

        data.append(info)

    return data


def scrape_content(url, output_format: str = "markdown"):
    """
    Downloads HTML and extracts clean text.
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        content = trafilatura.extract(downloaded, output_format=output_format)
        return content
    return None


def crawl_and_scrape(seed_url, max_pages: int = 10):
    """
    Crawls the domain starting from seed_url, gather links, and scrapes their content.
    """

    VISITED_LOG_FILE = "visited_urls.txt"
    OUTPUT_DATA_FILE = "scraped_content.txt"

    print(f"Crawling webpages, starting from {seed_url}")

    to_visit, known_links = focused_crawler(
        seed_url, max_seen_urls=max_pages)
    to_visit = set(to_visit)

    print(f"Found {len(to_visit)} pages to scrape. Starting extraction...")

    with open(VISITED_LOG_FILE, 'w', encoding="utf-8") as log_file, open(OUTPUT_DATA_FILE, 'w', encoding="utf-8") as output_file:
        for current_url in to_visit:
            print(f"Scraping content form {current_url}")

            content = scrape_content(current_url)

            if content:
                output_file.write(f"\n\n# URL: {current_url}\n\n{content}")
                log_file.write(f"{current_url}\n")
            else:
                log_file.write(f"{current_url} - No readable content extracted (Skipped)\n")
                print(f"  -> Skipping (No readable content extracted)")

            time.sleep(1)

    print(f"Scraping completed! Data saved to {OUTPUT_DATA_FILE}")


def main():
    resources = fetch_cider_resources(
        info_resource_id="jetstream2-gpu.indiana.access-ci.org"
    )

    if not resources:
        print("No resources found.")
        return

    filtered_resources = filter_resource_info(resources)
    resource_info = filtered_resources[0]

    seed_url = resource_info.get("user_guide_url")

    if seed_url:
        # Check if URL is active
        response = requests.get(
            seed_url, headers={"User-Agent": "Mozzila/5.0"}, timeout=5)
        if response.status_code == 200:
            crawl_and_scrape(seed_url, max_pages=20)
        else:
            print(
                f"Warning: User Guide URL {seed_url} is broken or unreachable (HTTP {response.status_code})")
    else:
        print("Warning: No User Guide URL found")

    # Save resources in JSON
    # with open("filtered_resources.json", 'w') as fp:
    #     json.dump(filtered_resources, fp, indent=4)


if __name__ == "__main__":
    main()
