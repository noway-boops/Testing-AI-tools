import csv
import os
from openai import OpenAI

INPUT_PATH = r"C:\Users\mshan\Downloads\Evals Assignment\reviews_hand_labeled.csv"
OUTPUT_PATH = r"C:\Users\mshan\Downloads\Evals Assignment\reviews evaluated.csv"

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROMPT_TEMPLATE = (
    "Rate the sentiment of the following product review on a scale from 1 to 5, "
    "where 1 is very negative and 5 is very positive. "
    "Respond with ONLY a single digit (1, 2, 3, 4, or 5).\n\n"
    "Title: {title}\n\n"
    "Review: {text}"
)


def get_llm_score(title, text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(title=title, text=text)}],
        max_tokens=1,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def main():
    with open(INPUT_PATH, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []
    for row in rows:
        title = row["review_title"]
        text = row["review_text"]
        hand_label = row["hand_label"].strip()

        llm_score = get_llm_score(title, text)
        match = "TRUE" if llm_score == hand_label else "FALSE"

        results.append({**row, "llm_score": llm_score, "match": match})

    fieldnames = list(results[0].keys())
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    total = len(results)
    matches = sum(1 for r in results if r["match"] == "TRUE")
    mismatches = total - matches
    accuracy = (matches / total * 100) if total > 0 else 0

    print(f"Total reviews:  {total}")
    print(f"Matches:        {matches}")
    print(f"Mismatches:     {mismatches}")
    print(f"Accuracy:       {accuracy:.1f}%")


if __name__ == "__main__":
    main()
