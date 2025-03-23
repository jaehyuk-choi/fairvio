import pdfplumber
import json
import faiss
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

PDF_PATH = "data/immigration_law.pdf"
INDEX_PATH = "data/legal_index.faiss"
CHUNKS_PATH = "data/chunks.json"

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def split_text(text, chunk_size=300, chunk_overlap=30):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

def embed_chunks(chunks, model):
    return model.encode(chunks)

def save_faiss_index(embeddings, index_path):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    faiss.write_index(index, index_path)

def save_chunks(chunks, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

def main():
    print("📄 Reading PDF...")
    text = extract_text_from_pdf(PDF_PATH)

    print("✂️ Splitting into chunks...")
    chunks = split_text(text)
    print(f"📐 Total chunks: {len(chunks)}")

    print("🔍 Generating embeddings...")
    model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L3-v2", cache_folder="/tmp/hf_cache")
    embeddings = embed_chunks(chunks, model)

    print("💾 Saving FAISS index...")
    save_faiss_index(embeddings, INDEX_PATH)

    print("📝 Saving chunks metadata...")
    save_chunks(chunks, CHUNKS_PATH)

    print("✅ Done.")

if __name__ == "__main__":
    main()
