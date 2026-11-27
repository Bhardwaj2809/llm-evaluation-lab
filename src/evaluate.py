import json
import os
from llm import generate_response


INPUT_FILE = "results/generated_answers.json"
OUTPUT_FILE = "results/evaluations.json"


def create_judge_prompt(
    question: str,
    reference_answer: str,
    generated_answer: str
) -> str:

    return f"""
You are a strict evaluator of AI-generated answers.

Your task is to evaluate the generated answer against the question
and reference answer.

QUESTION:
{question}

REFERENCE ANSWER:
{reference_answer}

GENERATED ANSWER:
{generated_answer}


EVALUATION RULES
================

CORRECTNESS:

5 = Completely correct with no meaningful factual errors.
4 = Mostly correct with only minor factual errors.
3 = Partially correct but contains significant errors.
2 = Mostly incorrect; only a small amount of correct information.
1 = Completely incorrect or does not answer the question.


RELEVANCE:

5 = Directly answers the question.
4 = Mostly answers the question with minor irrelevant information.
3 = Partially answers the question but contains significant irrelevant content.
2 = Mostly irrelevant.
1 = Does not answer the question at all.

IMPORTANT:
Simply mentioning the subject of the question does NOT make an answer
relevant.


COMPLETENESS:

5 = Covers essentially all important information required.
4 = Covers most important information.
3 = Covers some important information but misses significant points.
2 = Provides very little of the required information.
1 = Provides none of the important information.

IMPORTANT:
If the generated answer fails to explain the subject of the question,
completeness should be 1 or 2.


HALLUCINATION:

Set hallucination to TRUE if the generated answer contains:

- factually incorrect claims
- invented information
- unsupported factual claims
- fabricated information
- incorrect claims about AWS services
- unrelated information presented as factual information

Set hallucination to FALSE only when the factual claims are reasonably
supported and there are no meaningful fabricated or false claims.


IMPORTANT EVALUATION PRINCIPLES
==============================

1. Do not reward an answer simply because it is long.

2. Do not reward formatting or number of bullet points.

3. Do not require the generated answer to use the exact wording of the
   reference answer.

4. A generated answer can be correct even if it contains additional
   information that is not present in the reference answer.

5. Evaluate factual accuracy rather than textual similarity.

6. If an answer completely fails to answer the question, give low
   correctness, relevance, and completeness scores.

7. If an answer contains both correct information and factual errors,
   evaluate the overall answer and identify the important errors.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "correctness": 1,
    "relevance": 1,
    "completeness": 1,
    "hallucination": true,
    "reason": "brief explanation of the most important strengths and weaknesses"
}}

The scores MUST be integers from 1 to 5.
Hallucination MUST be either true or false.
"""


def evaluate_answer(
    question,
    reference_answer,
    generated_answer
):

    prompt = create_judge_prompt(
        question,
        reference_answer,
        generated_answer
    )

    return generate_response(prompt)


def parse_evaluation(raw_result):

    try:
        result = json.loads(raw_result)

    except json.JSONDecodeError:
        return None

    required_fields = [
        "correctness",
        "relevance",
        "completeness",
        "hallucination",
        "reason"
    ]

    # Check that every required field exists
    for field in required_fields:

        if field not in result:
            return None

    # Validate correctness
    if not isinstance(result["correctness"], int):
        return None

    if not 1 <= result["correctness"] <= 5:
        return None

    # Validate relevance
    if not isinstance(result["relevance"], int):
        return None

    if not 1 <= result["relevance"] <= 5:
        return None

    # Validate completeness
    if not isinstance(result["completeness"], int):
        return None

    if not 1 <= result["completeness"] <= 5:
        return None

    # Validate hallucination
    if not isinstance(result["hallucination"], bool):
        return None

    # Validate reason
    if not isinstance(result["reason"], str):
        return None

    return result


def main():

    print("Loading generated answers...")

    # Load generated answers
    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    evaluations = []

    print(f"Found {len(data)} generated answers.")

    print("\nStarting evaluation...")
    print("=" * 50)

    # Evaluate ALL questions
    for item in data:

        print(
            f"\nEvaluating question "
            f"{item['id']}/{len(data)}..."
        )

        print(
            f"Question: {item['question']}"
        )

        # Ask the judge LLM
        raw_result = evaluate_answer(
            item["question"],
            item["reference_answer"],
            item["generated_answer"]
        )

        # Validate the LLM output
        result = parse_evaluation(raw_result)

        if result is None:

            print("❌ INVALID JUDGE OUTPUT")
            print("Raw output:")
            print(raw_result)

            print(
                "Skipping this evaluation."
            )

            continue

        # Valid result
        print("✓ Valid evaluation")

        print(
            f"  Correctness: "
            f"{result['correctness']}/5"
        )

        print(
            f"  Relevance: "
            f"{result['relevance']}/5"
        )

        print(
            f"  Completeness: "
            f"{result['completeness']}/5"
        )

        print(
            f"  Hallucination: "
            f"{result['hallucination']}"
        )

        print(
            f"  Reason: "
            f"{result['reason']}"
        )

        # Store evaluation
        evaluations.append(
            {
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "evaluation": result
            }
        )

    # Make sure results directory exists
    os.makedirs(
        "results",
        exist_ok=True
    )

    # Save evaluations
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            evaluations,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n")
    print("=" * 50)
    print("EVALUATION COMPLETE")
    print("=" * 50)

    print(
        f"\nTotal questions: {len(data)}"
    )

    print(
        f"Valid evaluations: {len(evaluations)}"
    )

    print(
        f"Invalid evaluations: "
        f"{len(data) - len(evaluations)}"
    )

    print(
        f"\nResults saved to:"
        f"\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()