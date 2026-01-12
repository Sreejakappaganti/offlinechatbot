"""Test retrieval for specific queries"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.vector_store_nomic import NomicVectorStore as VectorStore
from src.core import config

# Initialize vector store
vs = VectorStore()

# Load existing data
if config.FAISS_INDEX_PATH.exists():
    print("Loading vector store...")
    vs.load()
else:
    print("No vector store found!")
    sys.exit(1)

print(f"Total vectors: {vs.index.ntotal}\n")

# Test queries
test_queries = [
    "who is Dr. J.K.Subashini",
    "who is Shakila",
    "summarize the document",
    "give me all the dates"
]

for query in test_queries:
    print("=" * 80)
    print(f"Query: {query}")
    print("=" * 80)
    
    results = vs.search(query, k=3)
    print(f"Retrieved {len(results)} chunks:\n")
    
    for i, doc in enumerate(results, 1):
        print(f"{i}. Source: {doc['source']}")
        print(f"   Score: {doc['score']:.3f}")
        print(f"   Text (first 300 chars): {doc['text'][:300]}...")
        print(f"   Contains 'Shakila': {'Shakila' in doc['text']}")
        print(f"   Contains 'Subashini': {'Subashini' in doc['text']}")
        print()
    print()
