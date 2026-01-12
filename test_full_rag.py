"""Test full RAG pipeline with actual LLM generation"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.vector_store_nomic import NomicVectorStore as VectorStore
from src.core import config
import requests

# Initialize and load vector store
print("Loading vector store...")
vs = VectorStore()
vs.load()

print(f"Total vectors: {vs.index.ntotal}\n")

# Test queries
test_queries = [
    "who is Dr. J.K.Subashini",
    "who is Shakila", 
    "summarize the document",
]

def generate_answer(prompt):
    """Call Ollama to generate answer"""
    try:
        response = requests.post(
            f"{config.OLLAMA_HOST}/api/generate",
            json={
                "model": config.LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": config.LLM_TEMPERATURE,
                    "num_predict": config.LLM_MAX_TOKENS,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "num_ctx": config.LLM_CONTEXT_WINDOW
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            return f"Error: {response.status_code}"
            
    except Exception as e:
        return f"Error: {e}"

for query in test_queries:
    print("=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)
    
    # Retrieve
    results = vs.search(query, k=3)
    print(f"\nRetrieved {len(results)} chunks")
    
    # Build context
    context_parts = []
    for idx, doc in enumerate(results, 1):
        context_parts.append(f"From {doc['source']}:\n{doc['text']}")
    context = "\n\n".join(context_parts)
    
    print(f"\nContext length: {len(context)} characters")
    
    # Create prompt
    prompt = config.get_rag_prompt(query, context)
    
    print("\nPrompt (first 500 chars):")
    print(prompt[:500])
    print("\n[Calling LLM...]")
    
    # Generate
    answer = generate_answer(prompt)
    
    print("\nANSWER:")
    print("-" * 80)
    print(answer)
    print("-" * 80)
    print("\n")
