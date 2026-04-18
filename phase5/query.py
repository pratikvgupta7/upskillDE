from qdrant_client import QdrantClient
from questionary import prompt
from sentence_transformers import SentenceTransformer
from openai import OpenAI

COLLECTION_NAME = "taxi_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5  # number of chunks to retrieve
openai_client = OpenAI() 

# connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# load same embedding model used during ingestion
model = SentenceTransformer(EMBEDDING_MODEL)

def search(query: str, top_k: int = TOP_K):
    """Embed query and find most similar chunks."""
    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True
    ).points

    return results

def build_context(results) -> str:
    """Build context string from search results."""
    context_parts = []
    for i, result in enumerate(results):
        source = result.payload["source"]
        text = result.payload["text"]
        score = result.score
        context_parts.append(
            f"[Source {i+1}: {source} (similarity: {score:.3f})]\n{text}"
        )
    return "\n\n---\n\n".join(context_parts)

def ask(question: str) -> str:
    print(f"\nQuestion: {question}")
    print("Searching for relevant context...")

    results = search(question)
    context = build_context(results)

    print(f"Retrieved {len(results)} chunks")
    print(f"Top result: {results[0].payload['source']} "
          f"(score: {results[0].score:.3f})")

    prompt = f"""You are a helpful data analyst assistant with expertise in NYC taxi data.
Answer the question based on the context provided below.
If the answer is not in the context, say so clearly.

Context:
{context}

Question: {question}

Answer:"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[
            {"role": "system", "content": "You are a helpful data analyst assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def main():
    questions = [
        "What does RatecodeID mean?",
        "What data quality issues were found in the taxi dataset?",
        "What is the difference between payment type 0 and payment type 1?",
        "What is the average fare amount in the dataset?",
        "How does the Flink interval join work?"
    ]

    for question in questions:
        answer = ask(question)
        print(f"\nAnswer: {answer}")
        print("\n" + "="*60)
    # debug — see what chunks were actually retrieved
    question = "How does the Flink interval join work?"
    results = search(question)
    for r in results:
        print(f"Score: {r.score:.3f} | Source: {r.payload['source']}")
        print(f"Text preview: {r.payload['text'][:100]}")
        print("---")        

if __name__ == "__main__":
    main()