# Fairvio

**Fairvio** is a multilingual, multimodal legal assistant that helps immigrant and marginalized workers access legal information, report labor violations, and connect with legal aid — all through voice calls, web chat, and structured report submissions.

This project integrates Retrieval-Augmented Generation (RAG) with phone-based input, document-grounded question answering, and case reporting automation. It's built with accessibility in mind, targeting users with limited English proficiency, no smartphones, or no familiarity with the legal system.

---

## 🌟 Features

- 📞 **Voice Assistant**: Users can call in and interact with the system in multiple languages via Twilio.
- 💬 **Web Chatbot** (in development): A React-based multilingual interface for typed interaction.
- 📝 **Direct Report Submission**: Structured form for submitting legal violation reports.
- 🔍 **RAG Pipeline**: Legal queries are answered based on retrieved chunks from official legal documents.
- 📄 **PDF Report Generation**: Automatically compiles structured violation reports for legal aid organizations.
- 👩‍⚖️ **Lawyer Matching**: Matches users with legal professionals based on case type and location.

---

## 🏗️ Tech Stack

- **Backend**: Python, Flask
- **LLM**: Mistral-7B (via Hugging Face Inference API)
- **Vector DB**: FAISS
- **Embedding**: SentenceTransformers
- **Voice**: Twilio Programmable Voice & STT
- **Frontend**: React (chatbot), Streamlit (prototype interface)
- **PDF Generation**: ReportLab
- **Orchestration**: LangChain

---

## 📁 Repository Structure

| File/Folder | Description |
|-------------|-------------|
| `call_bot.py` | Handles Twilio call routing and speech processing |
| `query_pipeline.py` | Core logic for embedding, retrieval, and LLM response |
| `llama_client.py` | Wrapper for calling Mistral-7B via Hugging Face |
| `streamlit_app.py` | Streamlit app for testing queries manually |
| `build_index.py` | Embeds and indexes legal documents into FAISS |
| `requirements.txt` | Python dependencies |
| `data/` | Folder for PDF legal documents |
| `node_modules/` | Frontend packages |
| `.env` | Environment variables (API keys, etc.) |

