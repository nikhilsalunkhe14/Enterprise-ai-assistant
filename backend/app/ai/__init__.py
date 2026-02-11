"""
AI Components for RAG Architecture
"""

from app.ai.embedding_engine import embedding_engine
from app.ai.vector_store import vector_store

# Initialize AI components
def initialize_ai_components():
    """Initialize AI components (called at app startup)"""
    print("Initializing AI components...")
    
    # Check if embedding engine is ready
    if embedding_engine.is_ready():
        print("✅ Embedding engine ready")
    else:
        print("❌ Embedding engine failed to initialize")
        return False
    
    # Check if vector store is ready
    if vector_store.is_ready():
        stats = vector_store.get_stats()
        print(f"✅ Vector store ready with {stats['document_count']} documents")
    else:
        print("❌ Vector store failed to initialize")
        return False
    
    print("🚀 AI components initialized successfully!")
    return True

# Export components
__all__ = ['embedding_engine', 'vector_store', 'initialize_ai_components']
