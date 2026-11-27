import json


HUMAN_FILE = "dataset/human_claim_evaluations.json"
CLAIM_FILE = "results/claim_evaluations.json"


def load_json(filename):

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    human_data = load_json(
        HUMAN_FILE
    )

    claim_data = load_json(
        CLAIM_FILE
    )

    print("\n")
    print("=" * 60)
    print(
        " HUMAN vs CLAIM-LEVEL LLM JUDGE"
    )
    print("=" * 60)

    # Flatten LLM claims while preserving
    # question_id and claim_id
    llm_claims = []

    for item in claim_data:

        question_id = item[
            "question_id"
        ]

        for claim in item["claims"]:

            llm_claims.append(
                {
                    "question_id": question_id,
                    "claim_id": claim[
                        "claim_id"
                    ],
                    "claim": claim[
                        "claim"
                    ],
                    "classification": claim[
                        "classification"
                    ]
                }
            )

    # Compare only first 15 human-labelled claims
    comparisons = []

    for human in human_data:

        question_id = human.get(
            "question_id",
            None
        )

        claim_id = human[
            "claim_id"
        ]

        # Find matching LLM claim
        match = None

        for llm in llm_claims:

            if (
                question_id is not None
                and
                llm["question_id"] == question_id
                and
                llm["claim_id"] == claim_id
            ):

                match = llm
                break

            elif (
                question_id is None
                and
                len(comparisons) < 15
            ):

                match = llm
                break

        if match is not None:

            comparisons.append(
                (
                    human,
                    match
                )
            )

    total = 0
    matches = 0

    print(
        "\nClaim comparison:"
    )

    print("-" * 60)

    for human, llm in comparisons:

        human_classification = (
            human["classification"]
        )

        llm_classification = (
            llm["classification"]
        )

        total += 1

        if (
            human_classification
            ==
            llm_classification
        ):

            matches += 1

            symbol = "✓"

        else:

            symbol = "✗"

        print(
            f"\nClaim "
            f"{human['claim_id']} "
            f"{symbol}"
        )

        print(
            f"Human: "
            f"{human_classification}"
        )

        print(
            f"LLM:   "
            f"{llm_classification}"
        )

        print(
            f"Text:  "
            f"{llm['claim']}"
        )

    print("\n")

    print("=" * 60)
    print("AGREEMENT RESULTS")
    print("=" * 60)

    if total == 0:

        print(
            "\nNo matching claims found."
        )

        return

    agreement = (
        matches /
        total
    ) * 100

    print(
        f"\nTotal claims compared: "
        f"{total}"
    )

    print(
        f"Matching classifications: "
        f"{matches}"
    )

    print(
        f"Different classifications: "
        f"{total - matches}"
    )

    print(
        f"\nClaim-level agreement: "
        f"{agreement:.1f}%"
    )


if __name__ == "__main__":
    main()