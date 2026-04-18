from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from ingest import main as load_chunks
import uuid

COLLECTION_NAME = "taxi_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # local model, free, fast
VECTOR_SIZE = 384  # dimension of all-MiniLM-L6-v2 embeddings

# connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# load embedding model locally — no API key needed
print(f"Loading embedding model: {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)

def create_collection():
    """Create Qdrant collection if it does not exist."""
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists — deleting and recreating")
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )
    print(f"Created collection '{COLLECTION_NAME}'")

def embed_and_store(chunks):
    """Embed all chunks and store in Qdrant."""
    print(f"\nEmbedding {len(chunks)} chunks...")

    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    print(f"Storing {len(chunks)} vectors in Qdrant...")
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append(PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "token_count": chunk["token_count"]
            }
        ))

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"Stored {len(points)} vectors successfully")

def main():
    chunks = load_chunks()
    create_collection()
    embed_and_store(chunks)

    # verify
    info = client.get_collection(COLLECTION_NAME)
    print(f"\n=== Collection info ===")
    print(f"Points stored: {info.points_count}")
    print(f"Vector size: {info.config.params.vectors.size}")

if __name__ == "__main__":
    main()