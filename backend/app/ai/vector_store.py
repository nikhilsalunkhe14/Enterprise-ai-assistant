import json
import os
import faiss
import numpy as np
from typing import List, Dict, Tuple
from app.ai.embedding_engine import embedding_engine
from app.core.logger import logger
import threading

class VectorStore:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(VectorStore, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.index = None
            self.documents = []
            self.metadata = []
            self.initialized = False
            self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
            self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize the vector store with IT standards data"""
        try:
            logger.info("Initializing vector store...")
            
            # Wait for embedding engine to be ready
            max_wait = 30  # seconds
            wait_time = 0
            while not embedding_engine.is_ready() and wait_time < max_wait:
                logger.info("Waiting for embedding engine...")
                import time
                time.sleep(1)
                wait_time += 1
            
            if not embedding_engine.is_ready():
                raise RuntimeError("Embedding engine failed to initialize")
            
            # Load and process documents
            self._load_standards_data()
            
            # Create FAISS index
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            
            if self.documents:
                # Generate embeddings for all documents
                logger.info("Generating embeddings for documents...")
                embeddings = embedding_engine.generate_batch_embeddings(self.documents)
                embeddings_array = np.array(embeddings, dtype=np.float32)
                
                # Add to FAISS index
                self.index.add(embeddings_array)
                logger.info(f"Vector store initialized with {len(self.documents)} documents")
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.initialized = False
    
    def _load_standards_data(self):
        """Load and chunk IT standards data"""
        standards_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "standards"
        )
        
        standard_files = [
            "sdlc.json", "agile.json", "devops.json", 
            "itil.json", "iso.json", "pmbok.json"
        ]
        
        for filename in standard_files:
            file_path = os.path.join(standards_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract and chunk different sections
                self._chunk_standard_data(data, filename.replace('.json', ''))
                
            except FileNotFoundError:
                print(f"Warning: {filename} not found")
            except json.JSONDecodeError as e:
                print(f"Error parsing {filename}: {e}")
    
    def _chunk_standard_data(self, data: Dict, standard_name: str):
        """Chunk standard data into searchable text pieces"""
        
        # Chunk title and description
        if data.get("title"):
            text = f"{data['title']}: {data.get('description', '')}"
            self.documents.append(text)
            self.metadata.append({
                "standard": standard_name,
                "type": "description",
                "title": data["title"]
            })
        
        # Chunk key practices
        for i, practice in enumerate(data.get("key_practices", [])):
            text = f"{standard_name} key practice: {practice}"
            self.documents.append(text)
            self.metadata.append({
                "standard": standard_name,
                "type": "key_practice",
                "index": i,
                "content": practice
            })
        
        # Chunk deliverables
        for i, deliverable in enumerate(data.get("deliverables", [])):
            text = f"{standard_name} deliverable: {deliverable}"
            self.documents.append(text)
            self.metadata.append({
                "standard": standard_name,
                "type": "deliverable",
                "index": i,
                "content": deliverable
            })
        
        # Chunk best practices
        for i, practice in enumerate(data.get("best_practices", [])):
            text = f"{standard_name} best practice: {practice}"
            self.documents.append(text)
            self.metadata.append({
                "standard": standard_name,
                "type": "best_practice",
                "index": i,
                "content": practice
            })
        
        # Chunk common risks
        for i, risk in enumerate(data.get("common_risks", [])):
            text = f"{standard_name} risk: {risk}"
            self.documents.append(text)
            self.metadata.append({
                "standard": standard_name,
                "type": "risk",
                "index": i,
                "content": risk
            })
    
    def search_similar(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for similar documents using FAISS"""
        if not self.initialized or self.index is None:
            return []
        
        try:
            # Generate query embedding
            query_embedding = embedding_engine.generate_embedding(query)
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_array, top_k)
            
            # Prepare results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    result = {
                        "document": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "similarity_score": float(1 / (1 + distance)),  # Convert distance to similarity
                        "rank": i + 1
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error searching similar documents: {e}")
            return []
    
    def is_ready(self) -> bool:
        """Check if the vector store is ready"""
        return self.initialized and self.index is not None
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            "initialized": self.initialized,
            "document_count": len(self.documents),
            "embedding_dimension": self.embedding_dim,
            "index_type": "FAISS IndexFlatL2"
        }

# Global instance
vector_store = VectorStore()
