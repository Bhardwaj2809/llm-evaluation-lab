import json
import os

from llm import generate_response
from claims import extract_claims


INPUT_FILE = "results/generated_answers.json"
OUTPUT_FILE = "results/claim_evaluations.json"


def create_verification_prompt(
    question,
    reference_answer,
    claim
):

    return f"""
You are an expert factuality evaluator.

Evaluate the CLAIM against the REFERENCE ANSWER.

Your task is to determine whether the claim is:

CORRECT
INCORRECT
or
UNSUPPORTED


QUESTION:
{question}


REFERENCE ANSWER:
{reference_answer}


CLAIM:
{claim}


========================
CLASSIFICATION RULES
========================

CORRECT:

Choose CORRECT when the reference answer supports the meaning
of the claim.

The wording does NOT need to be identical.

You may recognize reasonable paraphrases and equivalent wording.

Example:

Reference:
"Amazon S3 is an object storage service."

Claim:
"Amazon S3 is a cloud object storage service."

Classification:
CORRECT


INCORRECT:

Choose INCORRECT only when the reference answer directly
contradicts the claim or clearly establishes that the claim
is false.

Do NOT call something INCORRECT merely because the reference
does not mention it.

Example:

Reference:
"S3 stores data as objects."

Claim:
"S3 stores data in relational database tables."

Classification:
INCORRECT


UNSUPPORTED:

Choose UNSUPPORTED when the reference does not provide enough
information to determine whether the claim is true or false.

Example:

Reference:
"Amazon S3 is an object storage service."

Claim:
"S3 is commonly used for backups."

Classification:
UNSUPPORTED


========================
VERY IMPORTANT
========================

1. Judge the MEANING, not exact wording.

2. Reasonable paraphrases should be CORRECT.

3. Synonyms should be treated as equivalent.

4. Do NOT require the reference to contain the exact same words.

5. Do NOT use outside knowledge to mark a claim CORRECT.

6. Do NOT use outside knowledge to mark a claim INCORRECT.

7. If the claim is plausible but the reference does not establish
   it, choose UNSUPPORTED.

8. If the reference clearly contradicts the claim, choose INCORRECT.

9. If the reference supports the claim semantically, choose CORRECT.

10. The question provides context, but the REFERENCE ANSWER is
    the primary evidence.


========================
DECISION PROCESS
========================

Ask yourself:

Step 1:
Does the reference support the meaning of the claim?

YES → CORRECT

Step 2:
If not, does the reference contradict the claim?

YES → INCORRECT

Step 3:
If neither is true:

→ UNSUPPORTED


========================
OUTPUT
========================

Return ONLY valid JSON.

Use exactly:

{{
    "classification": "CORRECT",
    "evidence": "short evidence from the reference answer",
    "reason": "brief explanation"
}}

The classification MUST be exactly:

CORRECT
INCORRECT
UNSUPPORTED
"""


def verify_claim(
    question,
    reference_answer,
    claim
):

    prompt = create_verification_prompt(
        question,
        reference_answer,
        claim
    )

    raw_result = generate_response(prompt)

    try:

        # Find JSON object inside model output
        start = raw_result.find("{")
        end = raw_result.rfind("}")

        if start == -1 or end == -1:

            print("Invalid JSON from judge:")
            print(raw_result)

            return None

        json_text = raw_result[
            start:end + 1
        ]

        result = json.loads(
            json_text
        )

        required_fields = [
            "classification",
            "evidence",
            "reason"
        ]

        for field in required_fields:

            if field not in result:
                return None

        if result["classification"] not in [
            "CORRECT",
            "INCORRECT",
            "UNSUPPORTED"
        ]:

            return None

        return result

    except Exception:

        print(
            "Could not parse judge response:"
        )

        print(raw_result)

        return None


def main():

    print("Loading generated answers...")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    all_results = []

    total_claims = 0
    total_correct = 0
    total_incorrect = 0
    total_unsupported = 0
    total_invalid = 0

    print(
        f"Found {len(data)} generated answers."
    )

    print(
        "\nStarting evidence-grounded "
        "claim evaluation..."
    )

    print("=" * 60)

    for item in data:

        question_id = item["id"]

        print(
            f"\nQuestion "
            f"{question_id}/{len(data)}:"
        )

        print(
            item["question"]
        )

        # Extract claims
        claims = extract_claims(
            item["generated_answer"]
        )

        print(
            f"Extracted "
            f"{len(claims)} claims."
        )

        claim_results = []

        for claim_number, claim in enumerate(
            claims,
            start=1
        ):

            print(
                f"\n  Claim {claim_number}:"
            )

            print(
                f"  {claim}"
            )

            result = verify_claim(
                item["question"],
                item["reference_answer"],
                claim
            )

            # Invalid response
            if result is None:

                print(
                    "  ❌ INVALID"
                )

                total_invalid += 1

                claim_results.append(
                    {
                        "claim_id": claim_number,
                        "claim": claim,
                        "classification": "INVALID",
                        "evidence": "",
                        "reason": (
                            "Judge returned "
                            "invalid JSON."
                        )
                    }
                )

                continue

            classification = result[
                "classification"
            ]

            print(
                f"  Classification: "
                f"{classification}"
            )

            print(
                f"  Evidence: "
                f"{result['evidence']}"
            )

            print(
                f"  Reason: "
                f"{result['reason']}"
            )

            claim_results.append(
                {
                    "claim_id": claim_number,
                    "claim": claim,
                    "classification": classification,
                    "evidence": result["evidence"],
                    "reason": result["reason"]
                }
            )

            total_claims += 1

            if classification == "CORRECT":

                total_correct += 1

            elif classification == "INCORRECT":

                total_incorrect += 1

            elif classification == "UNSUPPORTED":

                total_unsupported += 1

        all_results.append(
            {
                "question_id": question_id,
                "category": item["category"],
                "question": item["question"],
                "claims": claim_results
            }
        )

    # Save results
    os.makedirs(
        "results",
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n")

    print("=" * 60)
    print(
        "EVIDENCE-GROUNDED "
        "EVALUATION COMPLETE"
    )
    print("=" * 60)

    print(
        f"\nValid claims: "
        f"{total_claims}"
    )

    print(
        f"Correct: "
        f"{total_correct}"
    )

    print(
        f"Incorrect: "
        f"{total_incorrect}"
    )

    print(
        f"Unsupported: "
        f"{total_unsupported}"
    )

    print(
        f"Invalid judge responses: "
        f"{total_invalid}"
    )

    if total_claims > 0:

        factuality = (
            total_correct /
            total_claims
        ) * 100

        incorrect_rate = (
            total_incorrect /
            total_claims
        ) * 100

        unsupported_rate = (
            total_unsupported /
            total_claims
        ) * 100

        print(
            f"\nClaim factuality: "
            f"{factuality:.1f}%"
        )

        print(
            f"Incorrect claim rate: "
            f"{incorrect_rate:.1f}%"
        )

        print(
            f"Unsupported claim rate: "
            f"{unsupported_rate:.1f}%"
        )

    print(
        f"\nResults saved to:"
        f"\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()