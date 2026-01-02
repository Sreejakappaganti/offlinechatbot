"""
Configuration for Offline AI Chatbot
Optimized for 8GB RAM or less
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Directory paths
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
MODELS_DIR = BASE_DIR / "models"

# Create directories if they don't exist
for dir_path in [DATA_DIR, DOCUMENTS_DIR, VECTOR_STORE_DIR, MODELS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Embedding Model Configuration (Nomic via Ollama)
EMBEDDING_MODEL = "nomic-embed-text:v1.5"  # 768-dimensional embeddings via Ollama
EMBEDDING_DEVICE = "cpu"  # Use CPU to save GPU RAM
EMBEDDING_MAX_LENGTH = 256  # Reduce max sequence length

# Vector Store Configuration
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "faiss_index.bin"
FAISS_METADATA_PATH = VECTOR_STORE_DIR / "metadata.pkl"
RETRIEVAL_TOP_K = 5  # Retrieve top 5 chunks for better context

# Document Processing Configuration
CHUNK_SIZE = 500  # Max 500 tokens per chunk
CHUNK_OVERLAP = 50  # Small overlap between chunks
OCR_LANGUAGE = "eng"  # Tesseract language

# LLM Configuration (Gemma 2B via Ollama)
LLM_MODEL = "gemma:2b"  # Gemma 2B quantized (Q4)
OLLAMA_HOST = "http://localhost:11434"
LLM_TEMPERATURE = 0.7  # Higher temperature for more responsive generation
LLM_MAX_TOKENS = 512
LLM_CONTEXT_WINDOW = 2048

# Flask Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = False

# System Prompt for RAG
SYSTEM_PROMPT = """You are a precise AI assistant that answers questions STRICTLY based on the provided context from uploaded documents.

CRITICAL RULES:
1. ONLY use information from the Context section below
2. Do NOT use any external knowledge or assumptions
3. If the context doesn't contain the answer, respond with: "I don't have enough information in the uploaded documents to answer this question."
4. Quote or reference specific parts of the context when answering
5. Be concise and factual - no speculation or hallucination
6. If you're uncertain, say so clearly"""

def get_rag_prompt(query: str, context: str) -> str:
    """Generate RAG prompt with query and retrieved context"""
    return f"""You are answering questions using the following document excerpts:

---BEGIN DOCUMENT---
{context}
---END DOCUMENT---

Question: {query}

Answer (using only the document above):"""
