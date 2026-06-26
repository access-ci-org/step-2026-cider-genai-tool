import json
from cider_genai.auditor.models import ComputeDetails, GeneralInfo


def get_prompt(cider_resource_record: dict, resource_file_path: str):
    cider_resource_json = json.dumps(cider_resource_record, indent=2)

    with open(resource_file_path, 'r', encoding="utf-8") as fp:
        resource_content = fp.read()

    general_info_rules = json.dumps(
        GeneralInfo.model_json_schema()["properties"], indent=2)
    compute_details_rules = json.dumps(
        ComputeDetails.model_json_schema()["properties"], indent=2)

    prompt = f"""
You are a cyber-infrastructure specialist/auditor responsible for keeping the repository up-to-date. You are provided with the existing resource information in the database and the scraped content from the user guide documentation of the resources maintained by the Resource Providers (RPs). Your job is to go through both current database record and the latest resource documentation, compare them, and suggest modifications to update the repository to keep it up-to-date.

You should only audit the specific fields as defined by the rules. Here are the allowed fields and their descriptions:

--- General Info ---
{general_info_rules}

--- Compute Details ---
{compute_details_rules}

Instructions:
1. Read the Scraped Documentation and collect details.
2. Look ONLY for the allowed fields listed above.
3. Read the provided current database record.
3. If the documentation contradicts the database record, or if the database is missing a value that exists in the documentation, create a Suggestion.
4. If a field is not explicitly mentioned in the documentation, do not guess. Leave it alone.
5. Provide your final response in strict JSON format matching the requested schema.

--- Current Database Record ---
{cider_resource_json}

--- Scraped Documentation ---
{resource_content}

"""

    return prompt
