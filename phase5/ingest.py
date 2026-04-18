import os
import re
from pathlib import Path
from typing import List, Dict
import tiktoken
import PyPDF2

DOCS_DIR = Path(__file__).parent / "docs"
CHUNK_SIZE = 500      # tokens per chunk
CHUNK_OVERLAP = 50    # tokens overlap between chunks

# use cl100k_base tokenizer — same as OpenAI embeddings
tokenizer = tiktoken.get_encoding("cl100k_base")

def load_documents() -> List[Dict]:
    """Load all markdown, text and PDF files from docs folder."""
    documents = []
    for file_path in DOCS_DIR.glob("**/*"):
        if file_path.suffix in [".md", ".txt"]:
            text = file_path.read_text(encoding="utf-8")
            documents.append({
                "source": file_path.name,
                "text": text
            })
            print(f"Loaded: {file_path.name} ({len(text)} chars)")

        elif file_path.suffix == ".pdf":
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            documents.append({
                "source": file_path.name,
                "text": text
            })
            print(f"Loaded PDF: {file_path.name} ({len(text)} chars)")

    return documents

def chunk_document(doc: Dict) -> List[Dict]:
    """Split a document into overlapping chunks."""
    text = doc["text"]
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0

    while start < len(tokens):
        end = start + CHUNK_SIZE
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens)

        chunks.append({
            "source": doc["source"],
            "chunk_index": len(chunks),
            "text": chunk_text,
            "token_count": len(chunk_tokens)
        })

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks

def main():
    print("=== Loading documents ===")
    documents = load_documents()
    print(f"\nLoaded {len(documents)} documents")

    print("\n=== Chunking documents ===")
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"{doc['source']}: {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Average tokens per chunk: {sum(c['token_count'] for c in all_chunks) // len(all_chunks)}")

    # preview first chunk
    print("\n=== First chunk preview ===")
    print(f"Source: {all_chunks[0]['source']}")
    print(f"Tokens: {all_chunks[0]['token_count']}")
    print(f"Text: {all_chunks[0]['text'][:200]}...")

    return all_chunks

if __name__ == "__main__":
    chunks = main()