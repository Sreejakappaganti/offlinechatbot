"""
Configuration for Offline AI Chatbot
Optimized for 8GB RAM or less
"""
import os
from pathlib import Path

# Base directory - go up to project root (2 levels up from src/core/)
BASE_DIR = Path(__file__).parent.parent.parent

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
FAISS_METADATA_BM25_PATH = VECTOR_STORE_DIR / "bm25_index.pkl"  # For hybrid search
RETRIEVAL_TOP_K = 15  # Retrieve top 15 chunks for maximum context
RETRIEVAL_RERANK = True  # Re-rank results for better accuracy

# Document Processing Configuration  
CHUNK_SIZE = 1000  # Larger chunks preserve more context
CHUNK_OVERLAP = 200  # Large overlap ensures no information loss
OCR_LANGUAGE = "eng"  # Tesseract language
OCR_ENHANCEMENT = True  # Enable image preprocessing for OCR

# LLM Configuration (Gemma 2B via Ollama)
LLM_MODEL = "gemma:2b"  # Gemma 2B quantized (Q4)
OLLAMA_HOST = "http://localhost:11434"
LLM_TEMPERATURE = 0.7  # Higher for more natural responses
LLM_MAX_TOKENS = 1024  # More tokens for complete answers
LLM_CONTEXT_WINDOW = 2048

# Flask Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = False

# System Prompt for RAG
SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided document context.

INSTRUCTIONS:
1. Answer questions using information from the provided context
2. Extract and provide all relevant details from the documents
3. If information is present in the context, provide it completely
4. Include names, dates, educational details, and other specific information when available
5. Only say information is missing if it's truly not in the context
6. Be thorough and extract all relevant data from the provided text"""

def get_rag_prompt(query: str, context: str) -> str:
    """Generate simple, direct RAG prompt that small models can follow"""
    return f"""Use the information below to answer the question.

INFORMATION:
{context}

QUESTION: {query}

ANSWER using only the information above:"""
