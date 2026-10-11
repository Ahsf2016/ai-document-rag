import json
import time
import os

from groq import Groq
from dotenv import load_dotenv

from app.retrieval.retriever import retrieve_chunks
from app.generation.llm import generate_answer


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


DATASET_PATH = "app/evaluation/dataset.json"

DOCUMENT_ID = "2ff66a64-2ffe-4162-935a-7af6803abfb0"


def load_dataset() -> list[dict]:
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def is_answer_correct(
    actual_answer: str,
    keywords: list[str],
    match: str = "all"
) -> bool:

    actual = actual_answer.lower()

    matches = [
        keyword.lower() in actual
        for keyword in keywords
    ]

    if match == "any":
        return any(matches)

    return all(matches)


def is_retrieval_relevant(
    retrieved_chunks: list[dict],
    keywords: list[str],
    match: str = "all"
) -> bool:

    retrieved_text = " ".join(
        chunk["text"]
        for chunk in retrieved_chunks
    ).lower()

    matches = [
        keyword.lower() in retrieved_text
        for keyword in keywords
    ]

    if match == "any":
        return any(matches)

    return all(matches)


def is_answer_grounded(
    question: str,
    actual_answer: str,
    retrieved_chunks: list[dict],
) -> bool:

    if not retrieved_chunks:
        return False

    context = "\n\n".join(
        chunk["text"]
        for chunk in retrieved_chunks
    )

    prompt = f"""
You are evaluating whether an answer is grounded in retrieved
document context.

Question:
{question}

Retrieved context:
{context}

Answer:
{actual_answer}

Determine whether the answer is fully supported by the retrieved context.

Return ONLY one word:

YES

if every factual claim in the answer is supported by the context.

Return:

NO

if the answer contains a factual claim that is not supported by the context.

Do not judge whether the answer is correct based on outside knowledge.

Only judge whether it is supported by the retrieved context.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    result = response.choices[0].message.content.strip().upper()

    return result == "YES"


def evaluate(top_k: int = 5):

    dataset = load_dataset()

    results = []

    for item in dataset:

        question = item["question"]
        expected_answer = item["answer"]
        keywords = item["keywords"]
        match = item.get("match", "all")

        # -------------------------
        # Start total timer
        # -------------------------

        total_start_time = time.perf_counter()

        # -------------------------
        # Retrieval
        # -------------------------

        retrieval_start_time = time.perf_counter()

        retrieved_chunks = retrieve_chunks(
            question,
            top_k=top_k,
            document_id=DOCUMENT_ID,
            max_distance=1.6,
        )

        retrieval_end_time = time.perf_counter()

        retrieval_latency = (
            retrieval_end_time - retrieval_start_time
        )

        # -------------------------
        # Generation
        # -------------------------

        generation_start_time = time.perf_counter()

        if not retrieved_chunks:

            answer = (
                "The information is not present "
                "in the uploaded document."
            )

        else:

            context = "\n\n".join(
                chunk["text"]
                for chunk in retrieved_chunks
            )

            answer = generate_answer(
                question,
                context,
            )

        generation_end_time = time.perf_counter()

        generation_latency = (
            generation_end_time - generation_start_time
        )

        # -------------------------
        # Total latency
        # -------------------------

        total_end_time = time.perf_counter()

        total_latency = (
            total_end_time - total_start_time
        )

        # -------------------------
        # Evaluation metrics
        # -------------------------

        retrieval_relevant = is_retrieval_relevant(
            retrieved_chunks,
            keywords,
            match
        )

        grounded = is_answer_grounded(
            question,
            answer,
            retrieved_chunks
        )

        correct = is_answer_correct(
            answer,
            keywords,
            match
        )

        # -------------------------
        # Store results
        # -------------------------

        results.append(
            {
                "question": question,
                "expected_answer": expected_answer,
                "actual_answer": answer,
                "correct": correct,
                "retrieval_relevant": retrieval_relevant,
                "grounded": grounded,
                "top_k": top_k,
                "retrieved_chunks": len(retrieved_chunks),
                "retrieved_text": [
                    chunk["text"]
                    for chunk in retrieved_chunks
                ],
                "retrieval_latency_seconds": round(
                    retrieval_latency,
                    3
                ),
                "generation_latency_seconds": round(
                    generation_latency,
                    3
                ),
                "total_latency_seconds": round(
                    total_latency,
                    3
                ),
            }
        )

    return results


if __name__ == "__main__":

    for top_k in [5]:

        print("\n")
        print("=" * 60)
        print(f"EVALUATION WITH top_k = {top_k}")
        print("=" * 60)

        results = evaluate(top_k=top_k)

        # -------------------------
        # Print individual results
        # -------------------------

        for index, result in enumerate(results, start=1):

            print(f"\nQuestion {index}")
            print("-" * 50)

            print("Question:")
            print(result["question"])

            print("\nExpected:")
            print(result["expected_answer"])

            print("\nActual:")
            print(result["actual_answer"])

            print("\nCorrect:")
            print(result["correct"])

            print("\nRetrieval relevant:")
            print(result["retrieval_relevant"])

            print("\nGrounded:")
            print(result["grounded"])

            print("\nTop K:")
            print(result["top_k"])

            print("\nRetrieved chunks:")
            print(result["retrieved_chunks"])

            print("\nRetrieved text:")

            for chunk in result["retrieved_text"]:

                print("-" * 40)
                print(chunk)

            print("\nRetrieval latency:")
            print(
                f"{result['retrieval_latency_seconds']} seconds"
            )

            print("\nGeneration latency:")
            print(
                f"{result['generation_latency_seconds']} seconds"
            )

            print("\nTotal latency:")
            print(
                f"{result['total_latency_seconds']} seconds"
            )

        # -------------------------
        # Evaluation summary
        # -------------------------

        average_retrieval_latency = sum(
            result["retrieval_latency_seconds"]
            for result in results
        ) / len(results)

        average_generation_latency = sum(
            result["generation_latency_seconds"]
            for result in results
        ) / len(results)

        average_total_latency = sum(
            result["total_latency_seconds"]
            for result in results
        ) / len(results)

        # -------------------------
        # Accuracy
        # -------------------------

        correct_answers = sum(
            result["correct"]
            for result in results
        )

        accuracy = (
            correct_answers / len(results)
        ) * 100

        # -------------------------
        # Retrieval relevance
        # -------------------------

        retrieval_relevant_count = sum(
            result["retrieval_relevant"]
            for result in results
        )

        retrieval_relevance_rate = (
            retrieval_relevant_count / len(results)
        ) * 100

        # -------------------------
        # Grounding
        # -------------------------

        grounded_count = sum(
            result["grounded"]
            for result in results
        )

        grounding_rate = (
            grounded_count / len(results)
        ) * 100

        # -------------------------
        # Print summary
        # -------------------------

        print("\n")
        print("=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)

        print(
            f"Questions evaluated: "
            f"{len(results)}"
        )

        print(
            f"Correct answers: "
            f"{correct_answers}/{len(results)}"
        )

        print(
            f"Accuracy: "
            f"{accuracy:.1f}%"
        )

        print(
            f"Grounding: "
            f"{grounded_count}/{len(results)} "
            f"({grounding_rate:.1f}%)"
        )

        print(
            f"Retrieval relevance: "
            f"{retrieval_relevant_count}/{len(results)} "
            f"({retrieval_relevance_rate:.1f}%)"
        )

        print(
            f"Average retrieval latency: "
            f"{average_retrieval_latency:.3f} seconds"
        )

        print(
            f"Average generation latency: "
            f"{average_generation_latency:.3f} seconds"
        )

        print(
            f"Average total latency: "
            f"{average_total_latency:.3f} seconds"
        )