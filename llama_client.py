# llama_client.py

import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load HF token from .env file
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize client
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.1", 
    token=HF_TOKEN
)

# Format the prompt for the LLM
def generate_prompt(context_docs, question):
    context = "\n\n".join(context_docs)
    prompt = f"""
You are a helpful immigration lawyer assistant. Based on the documents below, answer the user's question clearly and concisely.

Documents:
{context}

Question:
{question}

Answer in English:"""
    return prompt

# Call the model
def get_llama_response(context_docs, user_query):
    prompt = generate_prompt(context_docs, user_query)
    response = client.text_generation(prompt=prompt, max_new_tokens=300)
    return response.strip()
