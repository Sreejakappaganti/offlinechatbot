# Offline AI Chatbot

A local RAG (Retrieval-Augmented Generation) chatbot using Ollama and Nomic embeddings.

## Project Structure

```
OfflineAiBot/
│
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── .gitignore             # Git ignore rules
│
├── src/                   # Source code
│   ├── core/              # Core modules
│   │   ├── config.py              # Configuration settings
│   │   ├── vector_store_nomic.py  # Vector store with Nomic embeddings
│   │   └── document_processor.py  # Document processing logic
│   │
│   └── utils/             # Utility scripts
│       └── ingest.py              # Document ingestion script
│
├── app/                   # Web application assets
│   ├── static/            # CSS, JS, images
│   └── templates/         # HTML templates
│       └── index.html
│
├── data/                  # Data directory
│   ├── documents/         # Place your documents here (PDF, DOCX, PPTX, TXT)
│   └── vector_store/      # Generated vector store index
│
├── scripts/               # Setup and utility scripts
│   ├── setup.bat          # Windows setup script
│   └── setup.sh           # Linux/Mac setup script
│
├── models/                # Downloaded models directory
└── envi/                  # Virtual environment (if using)
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Ollama
Make sure Ollama is installed and running:
```bash
ollama pull gemma2:2b
ollama pull nomic-embed-text:v1.5
```

### 3. Add Documents
Place your documents (PDF, DOCX, PPTX, TXT) in the `data/documents/` folder.

### 4. Ingest Documents
```bash
python src/utils/ingest.py
```

### 5. Run the Application
```bash
python app.py
```

Then open your browser to `http://localhost:5000`

## Configuration

Edit `src/core/config.py` to customize:
- LLM model
- Embedding model
- Vector store settings
- Document processing options

## Environment Variables

Create a `.env` file in the root directory:
```
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=gemma2:2b
EMBEDDING_MODEL=nomic-embed-text:v1.5
```

## Features

- 📄 Support for multiple document formats (PDF, DOCX, PPTX, TXT)
- 🔍 RAG-based document retrieval
- 💬 Interactive chat interface
- 🚀 Fully offline operation
- 🎯 Nomic embeddings for better semantic search

## Requirements

- Python 3.8+
- Ollama running locally
- 8GB+ RAM recommended
