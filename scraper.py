import trafilatura


def scrape_content(url, output_format: str = "markdown"):
    """
    Downloads HTML and extracts clean text.
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        content = trafilatura.extract(downloaded, output_format=output_format)
        return content
    return None
