from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import threading

class EmbeddingEngine:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmbeddingEngine, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.model = None
            self.initialized = False
            self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model (singleton pattern)"""
        try:
            print("Loading sentence transformer model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.initialized = True
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a given text"""
        if not self.initialized or self.model is None:
            raise RuntimeError("Model not loaded properly")
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts at once"""
        if not self.initialized or self.model is None:
            raise RuntimeError("Model not loaded properly")
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            raise RuntimeError(f"Failed to generate batch embeddings: {str(e)}")
    
    def is_ready(self) -> bool:
        """Check if the embedding engine is ready"""
        return self.initialized and self.model is not None

# Global instance
embedding_engine = EmbeddingEngine()
