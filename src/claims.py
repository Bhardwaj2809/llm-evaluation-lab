import json
from llm import generate_response


def create_claim_prompt(answer):

    return f"""
You are a factual claim extraction system.

Extract the individual factual claims made by the answer below.

ANSWER:
{answer}

Rules:

1. Extract factual claims only.
2. Do not extract opinions.
3. Do not add facts that are not present in the answer.
4. Do not correct the answer.
5. Preserve the meaning of the original answer.
6. Split long statements into separate claims when appropriate.
7. Each claim should be understandable on its own.

Return ONLY valid JSON.

Use exactly this format:

{{
    "claims": [
        "claim 1",
        "claim 2",
        "claim 3"
    ]
}}
"""


def extract_claims(answer):

    prompt = create_claim_prompt(answer)

    raw_result = generate_response(prompt)

    try:

        # Find JSON object even if model adds extra text
        start = raw_result.find("{")
        end = raw_result.rfind("}")

        if start == -1 or end == -1:
            print("Could not find JSON in claim extractor output.")
            print(raw_result)
            return []

        json_text = raw_result[start:end + 1]

        result = json.loads(json_text)

        if "claims" not in result:
            return []

        if not isinstance(result["claims"], list):
            return []

        return result["claims"]

    except Exception:

        print("Could not parse claim extraction result.")
        print(raw_result)

        return []


if __name__ == "__main__":

    answer = """
    Amazon S3 is an object storage service.
    S3 stores data in a hierarchical namespace.
    S3 can be accessed using SSH.
    S3 is commonly used for backups.
    """

    claims = extract_claims(answer)

    print("\nExtracted Claims:")
    print("=" * 50)

    for index, claim in enumerate(
        claims,
        start=1
    ):

        print(
            f"{index}. {claim}"
        )