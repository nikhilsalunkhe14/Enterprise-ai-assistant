import json
import os
from typing import Dict, List, Optional, Tuple
from app.database import db_manager
from app.ai.llm_service import LLMService

class PromptEngine:
    def __init__(self):
        self.llm = LLMService()
        
        self.stage_keywords = {
            "planning": ["plan", "planning", "strategy", "roadmap", "initiation", "charter", "scope", "requirements"],
            "execution": ["execute", "execution", "implement", "develop", "build", "create", "deliver", "produce"],
            "monitoring": ["monitor", "monitoring", "track", "measure", "control", "review", "report", "status"],
            "risk": ["risk", "risks", "risk management", "mitigation", "threat", "vulnerability", "assessment"],
            "documentation": ["document", "documentation", "report", "manual", "guide", "specification", "wiki"]
        }

    def load_standard_data(self, domain: str) -> Optional[Dict]:
        """Load standard data for a specific domain"""
        standards_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "standards"
        )
        file_path = os.path.join(standards_dir, f"{domain}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def generate_prompt(self, user_query: str, session_id: str) -> Dict:
        """Generate structured response using RAG + Groq LLM"""

        try:
            # Step 1: Retrieve relevant context from FAISS
            from app.ai import vector_store
            retrieved_chunks = vector_store.search_similar(user_query, top_k=3)

            retrieved_context = [
                chunk['metadata']['content'] if 'content' in chunk['metadata']
                else chunk['document']
                for chunk in retrieved_chunks
            ]

            context_text = "\n\n".join(retrieved_context)

            # Step 2: Define system prompt
            system_prompt = """
You are an AI IT Project Delivery Assistant.
Use the provided IT standards context to generate structured, professional guidance.

Always respond in this structured format:
- Overview
- Planning
- Execution
- Risk Management
- Deliverables
- Success Metrics
"""

            # Step 3: Create user prompt
            user_prompt = f"""
User Query:
{user_query}

Relevant IT Standards Context:
{context_text}

Generate a professional structured response.
"""

            # Step 4: Call Groq LLM
            llm_response = self.llm.generate_response(system_prompt, user_prompt)

            # Step 5: Confidence calculation (optional basic version)
            confidence_score = 85 if retrieved_context else 40

            # Step 6: Save to DB
            db_manager.save_conversation(
                session_id=session_id,
                user_query=user_query,
                detected_domain="RAG + LLM",
                detected_stage="context-aware",
                confidence_score=confidence_score
            )

            return {
                "user_query": user_query,
                "retrieved_context": retrieved_context,
                "llm_response": llm_response,
                "confidence_score": confidence_score,
                "model_used": "Groq LLaMA3 + FAISS RAG"
            }

        except Exception as e:
            print(f"Error in RAG + LLM prompt generation: {e}")

            return {
                "user_query": user_query,
                "retrieved_context": [],
                "llm_response": "Error generating response.",
                "confidence_score": 0,
                "model_used": "Groq LLaMA3 + FAISS RAG"
            }
