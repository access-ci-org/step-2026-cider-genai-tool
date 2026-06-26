import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from cider_genai.auditor.prompt import get_prompt
from cider_genai.collector.fetch_cider import fetch_cider_resources
from cider_genai.auditor.models import AuditReport

_ = load_dotenv()


def audit(cider_resource_id: str, resource_file_path: str):
    client = OpenAI(
        base_url="https://llm.jetstream-cloud.org/api",
        api_key=os.getenv("LLM_API_KEY")
    )

    print("Fetching CiDeR records...")
    cider_resource_record = fetch_cider_resources(
        info_resource_id=cider_resource_id)

    print("Generating prompt...")
    prompt = get_prompt(cider_resource_record=cider_resource_record,
                        resource_file_path=resource_file_path)

    auditor_rule = json.dumps(AuditReport.model_json_schema())

    print("Generating suggestions...")
    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": f"You must output valid JSON matching this schema: {auditor_rule}"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return response.choices[0].message.content


def main():
    RESOURCE_ID = "deltaai.ncsa.access-ci.org"

    response = audit(RESOURCE_ID, "deltaai_scraped_content.md")

    result_json = json.loads(response)
    file_name = "suggestions_deltaai.json"
    with open(file_name, "w") as fp:
        json.dump(result_json, fp, indent=4)

    print(f"Suggestions saved to {file_name}")


if __name__ == "__main__":
    main()
