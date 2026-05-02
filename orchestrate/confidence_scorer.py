"""
Calculates confidence scores for triage decisions.
Uses weighted formula based on retrieval quality.
"""

from typing import Tuple


class ConfidenceScorer:
    
    HIGH_CONFIDENCE_THRESHOLD = 80.0
    MEDIUM_CONFIDENCE_THRESHOLD = 50.0
    LOW_CONFIDENCE_THRESHOLD = 30.0
    
    def calculate_confidence(self,
                            retrieval_score=0,
                            match_exactness=0,
                            policy_clarity=50,
                            ambiguity_level=0,
                            question_count=1,
                            risk_level="low"):
        """
        Calculate confidence with weighted formula.
        
        Inputs are computed as follows:
        - retrieval_score: number of docs found / 5 * 100
        - match_exactness: keyword overlap with top doc * 100
        - policy_clarity: doc length / 1000 * 100
        - ambiguity_level: question count * 20
        
        Returns tuple of (confidence_score, reasoning).
        """
        
        weights = {
            'retrieval': 0.35,
            'exactness': 0.30,
            'clarity': 0.25,
            'ambiguity': 0.10
        }
        
        if risk_level == 'high':
            weights['retrieval'] = 0.45
            weights['exactness'] = 0.30
            weights['clarity'] = 0.15
            weights['ambiguity'] = 0.10
        
        ambiguity_score = 100 - ambiguity_level
        
        confidence = (
            retrieval_score * weights['retrieval'] +
            match_exactness * weights['exactness'] +
            policy_clarity * weights['clarity'] +
            ambiguity_score * weights['ambiguity']
        )
        
        if question_count > 1:
            confidence *= 0.85
        
        if retrieval_score < 40:
            confidence *= 0.6
        
        if retrieval_score == 0:
            confidence = 0
        
        confidence = max(0, min(100, confidence))
        
        reasoning = self._generate_reasoning(confidence, retrieval_score, 
                                            match_exactness, policy_clarity)
        
        return confidence, reasoning
    
    def _generate_reasoning(self, confidence, retrieval, exactness, clarity):
        """Generate brief explanation of confidence score."""
        
        if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            if exactness > 90:
                return "Exact match found"
            elif retrieval > 85:
                return "Clear documentation available"
            else:
                return "Strong policy guidance"
        
        elif confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            if retrieval > 60 and exactness < 70:
                return "Similar documentation found"
            elif clarity < 60:
                return "Policy somewhat unclear"
            else:
                return "Moderate match with documentation"
        
        else:
            if retrieval < 40:
                return "Limited documentation"
            elif clarity < 40:
                return "Policy not well documented"
            else:
                return "High ambiguity"
    
    def should_escalate_due_to_low_confidence(self, confidence, risk_level):
        """
        Determine if confidence level warrants escalation.
        Higher threshold for high-risk cases.
        """
        
        if risk_level == 'high' and confidence < 60:
            return True
        
        if risk_level == 'medium' and confidence < 40:
            return True
        
        if confidence < self.LOW_CONFIDENCE_THRESHOLD:
            return True
        
        return False
    
    def compute_retrieval_score(self, docs, query_keywords_count):
        """
        Calculate retrieval score from search results.
        More docs found = higher score.
        Formula: (num_docs / 5) * 100, capped at 100
        """
        if not docs or query_keywords_count == 0:
            return 0.0
        
        num_docs = len(docs)
        doc_score = (num_docs / 5.0) * 100
        
        return min(100, doc_score)
    
    def compute_match_exactness(self, query_keywords, top_doc_content):
        """
        Calculate how well query matches the top document.
        Based on keyword overlap.
        Formula: (keywords found in doc / total query keywords) * 100
        """
        if not query_keywords or not top_doc_content:
            return 0.0
        
        from utils import has_keyword
        
        matched = 0
        for keyword in query_keywords:
            if keyword and len(keyword) > 2:
                if has_keyword(top_doc_content, [keyword]):
                    matched += 1
        
        if len(query_keywords) == 0:
            return 0.0
        
        exactness = (matched / len(query_keywords)) * 100
        return min(100, exactness)
    
    def compute_policy_clarity(self, doc_content):
        """
        Calculate how comprehensive the documentation is.
        Longer docs indicate better policy clarity.
        Formula: min(doc_length / 1000, 100)
        """
        if not doc_content:
            return 0.0
        
        doc_length = len(doc_content)
        clarity = min((doc_length / 1000.0) * 100, 100.0)
        
        return clarity
    
    def compute_ambiguity(self, question_count, possible_intents=1):
        """
        Calculate ambiguity from question count.
        More questions = more ambiguity.
        Formula: (question_count + possible_intents - 1) * 20, capped at 100
        """
        ambiguity = (question_count + possible_intents - 1) * 20
        return min(100, ambiguity)