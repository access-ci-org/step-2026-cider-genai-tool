import requests
from typing import Optional

BASE_URL = "https://operations-api.access-ci.org"


def fetch_cider_resources(info_resource_id: Optional[str] = None):
    """
    Fetch resource details from the CiDeR database
    """

    # Specific resource - "/wh2/cider/v1/info_resourceid/{resource_id}/?format=json"
    # Grouped resources - "/wh2/cider/v1/access-active-detail/info_groupid/{group_id}/"

    endpoint = f"/wh2/cider/v1/info_resourceid/{info_resource_id}/?format=json"
    url = BASE_URL + endpoint

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", {})

        return results

    except Exception as e:
        print(e)
        return {}
