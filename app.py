"""
Flask Application for Offline AI Chatbot with RAG
Using Gemma 2B via Ollama
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from typing import Dict, List
import requests
from dotenv import load_dotenv

from src.core import config
from src.core.vector_store_nomic import NomicVectorStore as VectorStore
from src.core.document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

# Initialize Flask app with correct template and static folders
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')
CORS(app)  # Enable CORS for frontend

# Initialize components
print("Initializing Offline AI Chatbot...")
print("="*60)

# Initialize vector store
vector_store = VectorStore()

# Try to load existing vector store
if config.FAISS_INDEX_PATH.exists():
    print("Loading existing vector store...")
    vector_store.load()
else:
    print("No existing vector store found. Please run ingestion first.")

print("="*60)


class OllamaClient:
    """Client for interacting with Ollama LLM"""
    
    def __init__(self, host: str = None, model: str = None):
        self.host = host or os.getenv('OLLAMA_HOST', config.OLLAMA_HOST)
        self.model = model or os.getenv('LLM_MODEL', config.LLM_MODEL)
    
    def generate(self, prompt: str, temperature: float = None, max_tokens: int = None) -> str:
        """
        Generate response from Ollama
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        temperature = temperature or config.LLM_TEMPERATURE
        max_tokens = max_tokens or config.LLM_MAX_TOKENS
        
        url = f"{self.host}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_k": 50,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)."
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model might be taking too long to respond."
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def check_health(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            
            # Check if our model is available
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            
            # Check for exact match or partial match (e.g., gemma:2b)
            model_available = any(self.model in name for name in model_names)
            
            return model_available
            
        except Exception as e:
            print(f"Health check failed: {e}")
            return False


# Initialize Ollama client
ollama_client = OllamaClient()


def perform_rag(query: str) -> Dict:
    """
    Perform RAG: Retrieve relevant documents and generate answer
    
    Args:
        query: User query
        
    Returns:
        Dictionary with answer and metadata
    """
    # Step 1: Retrieve relevant documents
    if vector_store.index.ntotal == 0:
        return {
            'answer': "No documents have been indexed yet. Please add documents first.",
            'sources': [],
            'error': 'no_documents'
        }
    
    retrieved_docs = vector_store.search(query, k=config.RETRIEVAL_TOP_K)
    
    if not retrieved_docs:
        return {
            'answer': "I don't have enough information in the uploaded documents to answer this question. Please upload relevant documents first.",
            'sources': [],
            'error': 'no_results'
        }
    
    # Step 2: Prepare context from retrieved documents
    context_parts = []
    for idx, doc in enumerate(retrieved_docs, 1):
        context_parts.append(f"--- Document Excerpt {idx} ---")
        context_parts.append(f"Source: {doc['source']}")
        context_parts.append(f"Content: {doc['text']}")
        context_parts.append("")
    
    context = "\n".join(context_parts)
    
    # Debug: Log retrieved context
    print(f"\n[RAG Debug] Query: {query}")
    print(f"[RAG Debug] Retrieved {len(retrieved_docs)} chunks:")
    for idx, doc in enumerate(retrieved_docs, 1):
        print(f"  {idx}. {doc['source']} (score: {doc['score']:.3f}) - {doc['text'][:100]}...")
    
    # Step 3: Create prompt with context
    prompt = config.get_rag_prompt(query, context)
    
    # Debug: Log the full prompt
    print(f"\n[RAG Debug] Full prompt being sent to LLM:")
    print("="*60)
    print(prompt)
    print("="*60)
    
    # Step 4: Generate answer using Ollama
    answer = ollama_client.generate(prompt)
    
    # Step 5: Prepare response
    sources = [
        {
            'source': doc['source'],
            'chunk_id': doc['chunk_id'],
            'score': doc['score'],
            'text': doc['text'][:200] + '...' if len(doc['text']) > 200 else doc['text']
        }
        for doc in retrieved_docs
    ]
    
    return {
        'answer': answer,
        'sources': sources,
        'query': query
    }


@app.route('/')
def index():
    """Serve the chatbot UI"""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    ollama_status = ollama_client.check_health()
    
    return jsonify({
        'status': 'healthy' if ollama_status else 'degraded',
        'ollama': 'running' if ollama_status else 'not running',
        'model': ollama_client.model,
        'vector_store': {
            'total_vectors': vector_store.index.ntotal,
            'total_chunks': len(vector_store.metadata)
        }
    })


@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for RAG-based question answering
    
    Request JSON:
        {
            "query": "Your question here"
        }
    
    Response JSON:
        {
            "answer": "Generated answer",
            "sources": [...],
            "query": "Original query"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing query parameter'
            }), 400
        
        query = data['query'].strip()
        
        if not query:
            return jsonify({
                'error': 'Query cannot be empty'
            }), 400
        
        # Check if Ollama is running
        if not ollama_client.check_health():
            return jsonify({
                'error': 'Ollama is not running or model is not available',
                'message': f'Please ensure Ollama is running and model "{ollama_client.model}" is installed'
            }), 503
        
        # Perform RAG
        result = perform_rag(query)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/stats', methods=['GET'])
def stats():
    """Get vector store statistics"""
    return jsonify(vector_store.get_stats())


@app.route('/ingest', methods=['POST'])
def ingest():
    """
    Ingest documents - REPLACES all previous documents with newly uploaded ones
    """
    try:
        processor = DocumentProcessor()
        results = {}
        errors = []
        
        # Check if files were uploaded
        if 'files' in request.files:
            files = request.files.getlist('files')
            
            if not files or files[0].filename == '':
                return jsonify({
                    'error': 'No files selected'
                }), 400
            
            print(f"\n[Upload] Processing {len(files)} file(s)...")
            print("[Upload] ⚠ Clearing ALL previous documents and vector store...")
            
            # CLEAR VECTOR STORE - Start fresh with new upload
            global vector_store
            vector_store = VectorStore()  # Reinitialize empty vector store
            
            # Process uploaded files
            for file in files:
                if file and file.filename:
                    try:
                        # Save file temporarily
                        filename = file.filename
                        filepath = os.path.join(config.DOCUMENTS_DIR, filename)
                        print(f"[Upload] Saving {filename} to {filepath}")
                        file.save(filepath)
                        
                        # Process the file
                        print(f"[Upload] Processing {filename}...")
                        chunks = processor.process_document(filepath)
                        
                        if chunks:
                            results[filename] = chunks
                            print(f"[Upload] [OK] Extracted {len(chunks)} chunks from {filename}")
                        else:
                            errors.append(f"{filename}: No text could be extracted")
                            print(f"[Upload] [ERROR] No text extracted from {filename}")
                    except Exception as e:
                        errors.append(f"{filename}: {str(e)}")
                        print(f"[Upload] [ERROR] Error processing {filename}: {e}")
        else:
            # Process all documents in the documents directory
            print(f"[Upload] Processing documents from directory...")
            results = processor.process_directory(str(config.DOCUMENTS_DIR))
        
        if not results:
            error_msg = "No documents found or processed"
            if errors:
                error_msg += f". Errors: {'; '.join(errors)}"
            
            return jsonify({
                'error': error_msg,
                'details': errors,
                'message': 'Please upload valid PDF, Word, PowerPoint, or TXT files'
            }), 400  # Changed from 404 to 400
        
        # Add to vector store
        total_chunks = 0
        for filename, chunks in results.items():
            vector_store.add_documents(chunks, source=filename)
            total_chunks += len(chunks)
        
        # Save vector store
        vector_store.save()
        
        response_data = {
            'status': 'success',
            'documents_processed': len(results),
            'total_chunks': total_chunks,
            'files': list(results.keys())
        }
        
        if errors:
            response_data['warnings'] = errors
        
        print(f"[Upload] [OK] Success: {len(results)} files, {total_chunks} chunks")
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            'error': 'Ingestion failed',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    # Check Ollama health on startup
    print("\nChecking Ollama status...")
    if ollama_client.check_health():
        print(f"[OK] Ollama is running with model: {ollama_client.model}")
    else:
        print(f"[ERROR] Warning: Ollama is not running or model '{ollama_client.model}' is not available")
        print(f"\nTo fix:")
        print(f"  1. Start Ollama: ollama serve")
        print(f"  2. Pull model: ollama pull {ollama_client.model}")
    
    print("\n" + "="*60)
    print(f"Starting Flask server on {config.FLASK_HOST}:{config.FLASK_PORT}")
    print("="*60 + "\n")
    
    # Run Flask app
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
