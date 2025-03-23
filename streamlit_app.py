# streamlit_app.py

import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from llama_client import get_llama_response

# Use consistent paths in all files
INDEX_PATH = "data/legal_index.faiss"
CHUNKS_PATH = "data/chunks.json"

# Load index and chunk data
@st.cache_resource
def load_resources():
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    return index, chunks, model

# Search similar chunks from FAISS
def search_chunks(query, model, index, chunks, k=3):
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), k)
    return [chunks[i] for i in I[0]]

# UI
def main():
    st.set_page_config(page_title="Legal Assistant for Immigrants", page_icon="⚖️")
    st.title("⚖️ Immigration Legal Assistant")
    st.markdown("Ask any question related to immigration or labor law.")

    user_query = st.text_input("💬 Enter your legal question here:")

    if user_query:
        st.info("🔍 Searching for relevant legal documents...")
        index, chunks, model = load_resources()
        relevant_chunks = search_chunks(user_query, model, index, chunks)

        with st.expander("📄 Relevant Documents Used"):
            for i, chunk in enumerate(relevant_chunks):
                st.markdown(f"**Document {i+1}:**\n```\n{chunk.strip()}\n```")

        st.info("🧠 Generating legal answer...")
        answer = get_llama_response(relevant_chunks, user_query)

        st.success("✅ Answer:")
        st.markdown(f"**{answer}**")

if __name__ == "__main__":
    main()

# import streamlit as st

# st.write('Hello world!')