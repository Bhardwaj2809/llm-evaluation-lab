import json
import os
from llm import generate_response


INPUT_FILE = "dataset/questions.json"
OUTPUT_FILE = "results/generated_answers.json"


def load_questions():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_answers():
    questions = load_questions()

    results = []

    for item in questions:
        print(f"Generating answer for question {item['id']}...")

        answer = generate_response(item["question"])

        results.append({
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "reference_answer": item["reference_answer"],
            "generated_answer": answer
        })

    os.makedirs("results", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    print("\nGeneration complete.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_answers()