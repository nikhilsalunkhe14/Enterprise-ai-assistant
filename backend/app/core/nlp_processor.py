import spacy
import nltk
from typing import Dict, List, Any
from app.core.logger import logger

class NLPProcessor:
    """NLP processing for enhanced text understanding and SDLC analysis"""
    
    def __init__(self):
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.warning("spaCy model not found, using basic processing")
            self.nlp = None
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading NLTK stopwords...")
            nltk.download('stopwords')
    
    def analyze_sdlc_phase(self, text: str) -> Dict[str, Any]:
        """Analyze text to detect SDLC phase and extract key information"""
        result = {
            "sdlc_phase": self._detect_sdlc_phase(text),
            "key_entities": self._extract_entities(text),
            "technical_terms": self._extract_technical_terms(text),
            "sentiment": self._analyze_sentiment(text),
            "complexity_score": self._calculate_complexity(text)
        }
        return result
    
    def _detect_sdlc_phase(self, text: str) -> str:
        """Detect which SDLC phase the text refers to"""
        text_lower = text.lower()
        
        phase_keywords = {
            "planning": ["plan", "requirement", "specification", "user story", "feature", "scope", "timeline"],
            "design": ["design", "architecture", "database", "api", "schema", "interface", "prototype"],
            "development": ["code", "implement", "develop", "program", "function", "class", "module"],
            "testing": ["test", "unit test", "integration", "qa", "quality", "bug", "debug"],
            "deployment": ["deploy", "release", "production", "ci/cd", "infrastructure", "server"],
            "maintenance": ["maintain", "update", "fix", "optimize", "monitor", "performance"]
        }
        
        phase_scores = {}
        for phase, keywords in phase_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            phase_scores[phase] = score
        
        return max(phase_scores, key=phase_scores.get) if phase_scores else "general"
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "TECHNOLOGY"]]
        return list(set(entities))
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms and keywords"""
        technical_keywords = [
            "api", "database", "framework", "library", "algorithm", "model",
            "deployment", "testing", "security", "performance", "scalability",
            "microservices", "cloud", "docker", "kubernetes", "react", "vue",
            "python", "javascript", "typescript", "sql", "nosql", "mongodb"
        ]
        
        text_lower = text.lower()
        found_terms = [term for term in technical_keywords if term in text_lower]
        return list(set(found_terms))
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of the text"""
        # Simple sentiment analysis using NLTK
        from nltk.sentiment import SentimentIntensityAnalyzer
        
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(text)
        
        if scores['compound'] >= 0.05:
            return "positive"
        elif scores['compound'] <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        if not self.nlp:
            return 0.5
        
        doc = self.nlp(text)
        
        # Factors: sentence length, word length, punctuation density
        avg_sentence_length = sum(len(sent) for sent in doc.sents) / len(doc.sents)
        avg_word_length = sum(len(token.text) for token in doc) / len(doc)
        
        # Normalize to 0-1 scale
        complexity = (avg_sentence_length / 20 + avg_word_length / 10) / 2
        return min(complexity, 1.0)
    
    def enhance_query(self, text: str) -> str:
        """Enhance query with NLP insights"""
        analysis = self.analyze_sdlc_phase(text)
        
        enhanced = f"""
Query Analysis:
- SDLC Phase: {analysis['sdlc_phase']}
- Technical Terms: {', '.join(analysis['technical_terms'])}
- Complexity: {analysis['complexity_score']:.2f}

Original Query: {text}
"""
        return enhanced
