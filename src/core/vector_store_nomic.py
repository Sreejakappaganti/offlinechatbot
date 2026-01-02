"""
Vector Store using Nomic Embeddings via Ollama
Uses nomic-embed-text:v1.5 model (768-dimensional embeddings)
"""
import os
import pickle
from typing import List, Dict
import numpy as np
import faiss
import requests

import config


class NomicVectorStore:
    """FAISS-based vector store with Nomic embeddings via Ollama"""
    
    def __init__(self, model_name: str = "nomic-embed-text:v1.5"):
        print(f"Initializing Nomic Vector Store with model: {model_name}")
        
        self.model_name = model_name
        self.ollama_host = os.getenv('OLLAMA_HOST', config.OLLAMA_HOST)
        self.dimension = 768  # Nomic embed text produces 768-dimensional embeddings
        self.top_k = config.RETRIEVAL_TOP_K
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        
        # Check if Ollama and model are available
        self._check_model_availability()
        
        print(f"[OK] Nomic embeddings ready. Dimension: {self.dimension}")
    
    def _check_model_availability(self):
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                if self.model_name not in model_names:
                    print(f"[WARNING] Model '{self.model_name}' not found in Ollama")
                    print(f"Available models: {model_names}")
                    print(f"Run: ollama pull {self.model_name}")
                else:
                    print(f"[OK] Model '{self.model_name}' is available")
        except Exception as e:
            print(f"[WARNING] Could not connect to Ollama: {e}")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text using Ollama API"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                embedding = response.json()['embedding']
                return np.array(embedding, dtype='float32')
            else:
                print(f"[ERROR] Embedding API error: {response.status_code}")
                return np.zeros(self.dimension, dtype='float32')
                
        except Exception as e:
            print(f"[ERROR] Failed to get embedding: {e}")
            return np.zeros(self.dimension, dtype='float32')
    
    def _get_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for multiple texts"""
        embeddings = []
        total = len(texts)
        
        for i, text in enumerate(texts):
            if i % 10 == 0:
                print(f"  Embedding progress: {i}/{total}")
            
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        
        return np.array(embeddings, dtype='float32')
    
    def add_documents(self, chunks: List[str], source: str = "unknown"):
        """Add documents to vector store"""
        if not chunks:
            return
        
        print(f"Vectorizing {len(chunks)} chunks from '{source}'...")
        
        # Get embeddings from Ollama
        vectors = self._get_embeddings_batch(chunks)
        
        # Ensure correct dimensions
        if vectors.shape[1] != self.dimension:
            print(f"[WARNING] Embedding dimension mismatch: expected {self.dimension}, got {vectors.shape[1]}")
            # Pad or truncate if needed
            if vectors.shape[1] < self.dimension:
                padding = np.zeros((vectors.shape[0], self.dimension - vectors.shape[1]), dtype='float32')
                vectors = np.hstack([vectors, padding])
            else:
                vectors = vectors[:, :self.dimension]
        
        # Add to FAISS index
        self.index.add(vectors)
        
        # Store metadata
        for i, chunk in enumerate(chunks):
            self.metadata.append({
                'text': chunk,
                'source': source,
                'chunk_id': i
            })
        
        print(f"[OK] Added {len(chunks)} chunks. Total vectors: {self.index.ntotal}")
    
    def search(self, query: str, k: int = None) -> List[Dict]:
        """Search for relevant chunks"""
        if k is None:
            k = self.top_k
        
        if self.index.ntotal == 0:
            return []
        
        k = min(k, self.index.ntotal)
        
        # Get query embedding
        query_vector = self._get_embedding(query)
        query_vector = query_vector.reshape(1, -1)
        
        # Search in FAISS
        distances, indices = self.index.search(query_vector, k)
        
        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['score'] = float(distances[0][i])
                results.append(result)
        
        return results
    
    def save(self, index_path: str = None, metadata_path: str = None):
        """Save vector store to disk"""
        if index_path is None:
            index_path = str(config.FAISS_INDEX_PATH)
        if metadata_path is None:
            metadata_path = str(config.FAISS_METADATA_PATH)
        
        print(f"Saving vector store...")
        print(f"  Index: {index_path}")
        print(f"  Metadata: {metadata_path}")
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save metadata
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        print(f"[OK] Vector store saved ({self.index.ntotal} vectors)")
    
    def load(self, index_path: str = None, metadata_path: str = None):
        """Load vector store from disk"""
        if index_path is None:
            index_path = str(config.FAISS_INDEX_PATH)
        if metadata_path is None:
            metadata_path = str(config.FAISS_METADATA_PATH)
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            print("[WARNING] Vector store files not found")
            return False
        
        print(f"Loading vector store...")
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        
        print(f"[OK] Vector store loaded: {self.index.ntotal} vectors")
        return True
    
    def clear(self):
        """Clear all data from vector store"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        print("[OK] Vector store cleared")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dimension,
            'total_chunks': len(self.metadata),
            'sources': list(set(m['source'] for m in self.metadata))
        }
