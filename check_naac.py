"""Check what's in Naac_appLetter.pdf chunk"""
import sys
from pathlib import Path
import pickle

# Direct load without initializing the whole vector store
metadata_path = Path("data/vector_store/metadata.pkl")
metadata = pickle.load(open(metadata_path, 'rb'))

# Find Naac_appLetter.pdf chunks
print("Searching for Naac_appLetter.pdf chunks...")
print("=" * 80)

for i, meta in enumerate(metadata):
    if 'Naac_appLetter' in meta['source']:
        print(f"\n### Chunk {i} ###")
        print(f"Source: {meta['source']}")
        print(f"Chunk ID: {meta['chunk_id']}")
        print(f"Text length: {len(meta['text'])} characters")
        print("\nFull text:")
        print("=" * 80)
        print(meta['text'])
        print("=" * 80)
        print(f"\nContains 'Shakila': {'Shakila' in meta['text']}")
        print(f"Contains 'Subashini': {'Subashini' in meta['text']}")
        print(f"Contains 'SUBASHINI': {'SUBASHINI' in meta['text']}")
        print(f"Contains 'J.K.': {'J.K.' in meta['text']}")
        print("\n")
