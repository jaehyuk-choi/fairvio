# query_pipeline.py

import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from llama_client import get_llama_response

INDEX_PATH = "data/legal_index.faiss"
CHUNKS_PATH = "data/chunks.json"

# Load FAISS index and chunk metadata
def load_index_and_chunks():
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks

# Search similar chunks using FAISS
def search_similar_chunks(query, model, index, chunks, k=3):
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), k)
    return [chunks[i] for i in I[0]]

def main():
    print("📥 Loading FAISS index and chunks...")
    index, chunks = load_index_and_chunks()
    model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L3-v2", cache_folder="/tmp/hf_cache")


    while True:
        query = input("\n💬 Enter your legal question (type 'exit' to quit):\n> ")
        if query.lower() == "exit":
            break

        print("🔎 Searching for relevant legal documents...")
        relevant_chunks = search_similar_chunks(query, model, index, chunks)

        print("\n📄 Top Matching Chunks:")
        for i, chunk in enumerate(relevant_chunks):
            print(f"\n--- Chunk {i+1} ---\n{chunk.strip()}\n")

        print("🧠 Generating answer using LLaMA...")
        answer = get_llama_response(relevant_chunks, query)

        print("\n💬 Answer:")
        print(answer)

if __name__ == "__main__":
    main()
