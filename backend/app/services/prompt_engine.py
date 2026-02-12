import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional, Tuple
from backend.app.database import db_manager
from backend.app.ai.llm_service import LLMService
from backend.app.tools.tool_service import ToolService
from backend.app.core.logger import logger




class PromptEngine:
    def __init__(self):
        self.llm = LLMService()
        self.tools = ToolService()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.stage_keywords = {
            "planning": ["plan", "planning", "strategy", "roadmap", "initiation", "charter", "scope", "requirements"],
            "execution": ["execute", "execution", "implement", "develop", "build", "create", "deliver", "produce"],
            "monitoring": ["monitor", "monitoring", "track", "measure", "control", "review", "report", "status"],
            "risk": ["risk", "risks", "risk management", "mitigation", "threat", "vulnerability", "assessment"],
            "documentation": ["document", "documentation", "report", "manual", "guide", "specification", "wiki"]
        }

    def load_standard_data(self, domain: str) -> Optional[Dict]:
        """Load standard data for a specific domain"""
        file_path = os.path.join(self.standards_dir, f"{domain}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def detect_domain_with_reasoning(self, query: str) -> Tuple[Optional[str], List[str]]:
        """Detect domain from user query - flexible approach for any domain"""
        query_lower = query.lower()
        domain_scores = {}
        domain_matches = {}
        
        # First try to match predefined domains
        for domain, keywords in self.domain_keywords.items():
            matched_keywords = [keyword for keyword in keywords if keyword in query_lower]
            if matched_keywords:
                domain_scores[domain] = len(matched_keywords)
                domain_matches[domain] = matched_keywords
        
        # If no predefined domain matches, extract domain from query
        if not domain_scores:
            # Extract potential domain from query using common patterns
            words = query_lower.split()
            
            # Look for domain indicators
            domain_indicators = [
                "project", "system", "application", "software", "platform", 
                "service", "process", "framework", "methodology", "solution"
            ]
            
            # Find words that could be domains
            potential_domains = []
            for i, word in enumerate(words):
                if any(indicator in word for indicator in domain_indicators):
                    # Take surrounding words as context
                    context_start = max(0, i-2)
                    context_end = min(len(words), i+3)
                    context = " ".join(words[context_start:context_end])
                    potential_domains.append(context)
            
            if potential_domains:
                # Use the first potential domain as a fallback
                detected_domain = potential_domains[0].title()
                return detected_domain, [detected_domain]
            else:
                # Last resort: use the main subject of the query
                # Remove common words and extract key terms
                stop_words = {"help", "me", "with", "for", "a", "an", "the", "how", "to", "what", "when", "where", "why"}
                key_terms = [word for word in words if word not in stop_words and len(word) > 2]
                
                if key_terms:
                    detected_domain = " ".join(key_terms[:2]).title()  # Use first 2 key terms
                    return detected_domain, key_terms[:2]
        
        if domain_scores:
            best_domain = max(domain_scores.items(), key=lambda x: x[1])[0]
            return best_domain, domain_matches[best_domain]
        
        return None, []

    def detect_stage_with_reasoning(self, query: str) -> Tuple[Optional[str], List[str]]:
        """Detect stage from user query and return stage with matched keywords"""
        query_lower = query.lower()
        stage_scores = {}
        stage_matches = {}
        
        for stage, keywords in self.stage_keywords.items():
            matched_keywords = [keyword for keyword in keywords if keyword in query_lower]
            if matched_keywords:
                stage_scores[stage] = len(matched_keywords)
                stage_matches[stage] = matched_keywords
        
        if not stage_scores:
            return None, []
        
        best_stage = max(stage_scores.items(), key=lambda x: x[1])[0]
        return best_stage, stage_matches[best_stage]

    def calculate_confidence_score(self, domain_matches: int, stage_matches: int) -> int:
        """Calculate confidence score based on keyword matches"""
        base_score = (domain_matches * 20) + (stage_matches * 15)
        # Reduce confidence slightly if no stage detected
        if stage_matches == 0:
            base_score = int(base_score * 0.8)
        return min(100, base_score)

    def generate_professional_prompt(self, domain: str, stage: str, standard_data: Optional[Dict]) -> str:
        """Generate a professional structured prompt - works for any domain"""
        if standard_data:
            title = standard_data.get("title", domain)
            key_practices = standard_data.get("key_practices", [])
            roles = standard_data.get("roles_involved", [])
            deliverables = standard_data.get("deliverables", [])
            best_practices = standard_data.get("best_practices", [])
            primary_role = roles[0] if roles else "Project Manager"
        else:
            # Fallback for unknown domains
            title = domain
            key_practices = ["Requirements gathering", "Planning and design", "Implementation", "Testing and validation", "Deployment and monitoring"]
            roles = ["Project Manager", "Team Lead", "Stakeholder", "Subject Matter Expert", "Quality Assurance"]
            deliverables = ["Project Plan", "Requirements Document", "Design Specifications", "Implementation Report", "Final Deliverable"]
            best_practices = ["Clear communication", "Stakeholder engagement", "Quality assurance", "Risk management"]
            primary_role = "Project Manager"
        
        stage_text = stage if stage != "general" else "comprehensive"
        
        prompt = f"As a {primary_role}, develop a structured {stage_text} strategy for {title}.\n\n"
        
        prompt += "**Objectives:**\n"
        prompt += f"- Establish clear {stage_text} objectives for {title}\n"
        if key_practices:
            prompt += f"- Implement key practices: {', '.join(key_practices[:3])}\n"
        
        prompt += "\n**Key Activities:**\n"
        if key_practices:
            for i, practice in enumerate(key_practices[:5], 1):
                prompt += f"{i}. {practice}\n"
        
        prompt += "\n**Roles & Responsibilities:**\n"
        if roles:
            for i, role in enumerate(roles[:4], 1):
                prompt += f"{i}. {role}: Define specific responsibilities and contributions\n"
        
        prompt += "\n**Deliverables:**\n"
        if deliverables:
            for i, deliverable in enumerate(deliverables[:4], 1):
                prompt += f"{i}. {deliverable}\n"
        
        prompt += "\n**Risk Considerations:**\n"
        if best_practices:
            prompt += f"- Follow best practices: {best_practices[0]}\n"
            if len(best_practices) > 1:
                prompt += f"- Ensure compliance with: {best_practices[1]}\n"
        
        prompt += "\nThis strategy should be actionable, measurable, and aligned with industry standards and organizational objectives."
        
        return prompt
    
    def _generate_rag_response(self, user_query: str, retrieved_context: List[str], retrieved_chunks: List[Dict]) -> str:
        """Generate structured response based on retrieved context"""
        # Extract unique standards from retrieved chunks
        standards_mentioned = list(set(chunk['metadata']['standard'] for chunk in retrieved_chunks if 'standard' in chunk['metadata']))
        
        # Extract key practices and deliverables from context
        key_practices = []
        deliverables = []
        risks = []
        
        for chunk in retrieved_chunks:
            metadata = chunk['metadata']
            if metadata.get('type') == 'key_practice' and 'content' in metadata:
                key_practices.append(metadata['content'])
            elif metadata.get('type') == 'deliverable' and 'content' in metadata:
                deliverables.append(metadata['content'])
            elif metadata.get('type') == 'risk' and 'content' in metadata:
                risks.append(metadata['content'])
        
        # Build structured response
        response = f"Based on your query about '{user_query}', here's a comprehensive IT project delivery guidance:\n\n"
        
        # Standards referenced
        if standards_mentioned:
            response += f"**Standards Referenced:** {', '.join(standards_mentioned).upper()}\n\n"
        
        # Planning and Strategy
        response += "**Planning & Strategy:**\n"
        response += f"- Develop a structured approach based on {', '.join(standards_mentioned)} best practices\n"
        response += "- Define clear objectives, scope, and success criteria\n"
        response += "- Establish timeline with realistic milestones\n\n"
        
        # Key Activities
        if key_practices:
            response += "**Key Activities:**\n"
            for i, practice in enumerate(key_practices[:5], 1):
                response += f"{i}. {practice}\n"
            response += "\n"
        
        # Roles and Responsibilities
        response += "**Roles & Responsibilities:**\n"
        response += "- Project Manager: Overall coordination and stakeholder management\n"
        response += "- Technical Lead: Implementation and technical decisions\n"
        response += "- Quality Assurance: Testing and compliance verification\n"
        response += "- Team Members: Execution and delivery of tasks\n\n"
        
        # Deliverables
        if deliverables:
            response += "**Expected Deliverables:**\n"
            for i, deliverable in enumerate(deliverables[:4], 1):
                response += f"{i}. {deliverable}\n"
            response += "\n"
        
        # Risk Management
        response += "**Risk Management:**\n"
        if risks:
            response += "- Address potential risks: " + "; ".join(risks[:3]) + "\n"
        response += "- Implement regular monitoring and quality checks\n"
        response += "- Maintain clear communication channels\n"
        response += "- Document all decisions and changes\n\n"
        
        # Success Metrics
        response += "**Success Metrics:**\n"
        response += "- Timely completion within budget constraints\n"
        response += "- Quality standards compliance\n"
        response += "- Stakeholder satisfaction\n"
        response += "- Documentation completeness\n\n"
        
        response += "This guidance is based on industry best practices and should be adapted to your specific organizational context."
        
        return response
    
    def _calculate_rag_confidence(self, retrieved_chunks: List[Dict]) -> int:
        """Calculate confidence score based on retrieval quality"""
        if not retrieved_chunks:
            return 0
        
        # Base confidence from similarity scores
        avg_similarity = sum(chunk.get('similarity_score', 0) for chunk in retrieved_chunks) / len(retrieved_chunks)
        base_confidence = int(avg_similarity * 100)
        
        # Boost confidence if we have good coverage of different content types
        content_types = set(chunk['metadata'].get('type', 'unknown') for chunk in retrieved_chunks)
        if len(content_types) >= 3:  # Multiple types of content retrieved
            base_confidence = min(100, base_confidence + 15)
        elif len(content_types) >= 2:
            base_confidence = min(100, base_confidence + 8)
        
        # Ensure minimum confidence for successful retrieval
        return max(base_confidence, 25)

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

            # Tool Decision Logic
            tool_output = None

            # Tool Trigger Logic
            if "risk score" in user_query.lower():
                tool_output = self.tools.calculate_risk_score(4, 5)

            elif "timeline" in user_query.lower():
                tool_output = self.tools.estimate_timeline("medium", 5)

            elif "generate project document" in user_query.lower():
                tool_output = self.tools.generate_project_document("AI Project")

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
                "tool_output": tool_output,
                "confidence_score": confidence_score,
                "model_used": "Groq LLaMA3 + FAISS RAG + Tool Agent"
            }

        except Exception as e:
            print(f"Error in RAG + LLM prompt generation: {e}")

            return {
                "user_query": user_query,
                "retrieved_context": [],
                "llm_response": "Error generating response.",
                "tool_output": None,
                "confidence_score": 0,
                "model_used": "Groq LLaMA3 + FAISS RAG + Tool Agent"
            }
    
    async def generate_prompt_async(self, user_query: str, session_id: str) -> Dict:
        """Async wrapper for generate_prompt using ThreadPoolExecutor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.generate_prompt,
            user_query,
            session_id
        )