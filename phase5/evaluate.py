from query import search, ask

# ground truth — question, expected answer keywords, expected source
EVAL_SET = [
    {
        "question": "What does RatecodeID mean?",
        "expected_keywords": ["rate", "JFK", "Newark", "standard"],
        "expected_source": "data_dictionary_trip_records_yellow.pdf"
    },
    {
        "question": "What is payment type 0?",
        "expected_keywords": ["flex", "dynamic", "fare"],
        "expected_source": "dbt_models.md"
    },
    {
        "question": "What data quality issues were found?",
        "expected_keywords": ["fare", "timestamp", "payment"],
        "expected_source": "phase1_readme.md"
    },
    {
        "question": "What is the average fare amount?",
        "expected_keywords": ["21.66"],
        "expected_source": "dbt_models.md"
    },
    {
        "question": "How does the Flink interval join work?",
        "expected_keywords": ["interval", "2 hour", "state", "unbounded"],
        "expected_source": "phase3_readme.md"
    },
    {
        "question": "What is the daily revenue range?",
        "expected_keywords": ["742", "4,946", "revenue"],
        "expected_source": "dbt_models.md"
    },
    {
        "question": "What is tip percentage for credit card trips?",
        "expected_keywords": ["21", "credit", "tip"],
        "expected_source": "dbt_models.md"
    },
    {
        "question": "What is partition affinity in Kafka?",
        "expected_keywords": ["partition", "key", "trip_id", "same"],
        "expected_source": "phase3_readme.md"
    },
    {
        "question": "How many clean rows are in the dataset?",
        "expected_keywords": ["7,054,099", "7054099"],
        "expected_source": "phase1_readme.md"
    },
    {
        "question": "What are the dbt mart models?",
        "expected_keywords": ["daily_revenue", "payment_summary"],
        "expected_source": "dbt_models.md"
    }
]

def evaluate_retrieval(eval_set):
    """
    Measure retrieval quality — did we get the right source in top 5?
    Does not call the LLM — just measures search quality.
    """
    print("=== Retrieval Evaluation ===\n")

    correct_source = 0
    total = len(eval_set)

    for item in eval_set:
        question = item["question"]
        expected_source = item["expected_source"]

        results = search(question)
        retrieved_sources = [r.payload["source"] for r in results]
        top_source = retrieved_sources[0]
        top_score = results[0].score

        source_found = expected_source in retrieved_sources
        if source_found:
            correct_source += 1

        status = "✓" if source_found else "✗"
        print(f"{status} Q: {question[:50]}")
        print(f"  Expected: {expected_source}")
        print(f"  Top result: {top_source} (score: {top_score:.3f})")
        if not source_found:
            print(f"  Retrieved: {retrieved_sources}")
        print()

    recall_at_5 = correct_source / total * 100
    print(f"=== Results ===")
    print(f"Recall@5: {correct_source}/{total} = {recall_at_5:.1f}%")
    print(f"(Did the correct source appear anywhere in top 5 results?)")
    return recall_at_5

def evaluate_answers(eval_set):
    """
    Measure answer quality — do answers contain expected keywords?
    Calls the LLM — costs a small amount.
    """
    print("\n=== Answer Quality Evaluation ===\n")

    correct_answers = 0
    total = len(eval_set)

    for item in eval_set:
        question = item["question"]
        expected_keywords = item["expected_keywords"]

        answer = ask(question)
        answer_lower = answer.lower()

        keywords_found = [
            kw for kw in expected_keywords
            if kw.lower() in answer_lower
        ]
        all_found = len(keywords_found) == len(expected_keywords)

        if all_found:
            correct_answers += 1

        status = "✓" if all_found else "✗"
        print(f"{status} Q: {question[:50]}")
        print(f"  Expected keywords: {expected_keywords}")
        print(f"  Found: {keywords_found}")
        if not all_found:
            missing = [kw for kw in expected_keywords if kw.lower() not in answer_lower]
            print(f"  Missing: {missing}")
            print(f"  Answer: {answer[:150]}...")
        print()

    answer_accuracy = correct_answers / total * 100
    print(f"=== Results ===")
    print(f"Answer accuracy: {correct_answers}/{total} = {answer_accuracy:.1f}%")
    print(f"(Did answers contain all expected keywords?)")
    return answer_accuracy

if __name__ == "__main__":
    # run retrieval eval first — free, no LLM calls
    recall = evaluate_retrieval(EVAL_SET)

    print("\n" + "="*60 + "\n")

    # run answer eval — costs a small amount
    accuracy = evaluate_answers(EVAL_SET)

    print("\n" + "="*60)
    print(f"\nFinal scores:")
    print(f"  Retrieval Recall@5: {recall:.1f}%")
    print(f"  Answer Accuracy:    {accuracy:.1f}%")