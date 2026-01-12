"""Debug vector store contents"""
import pickle
from pathlib import Path

vector_store_path = Path("data/vector_store/metadata.pkl")

if vector_store_path.exists():
    metadata = pickle.load(open(vector_store_path, 'rb'))
    print(f"Total chunks in vector store: {len(metadata)}\n")
    print("="*80)
    
    for i, m in enumerate(metadata):
        print(f"\nChunk {i+1}:")
        print(f"  Source: {m['source']}")
        print(f"  Chunk ID: {m['chunk_id']}")
        print(f"  Text length: {len(m['text'])} characters")
        print(f"  Preview: {m['text'][:200]}...")
        print("-"*80)
else:
    print("Vector store not found!")
