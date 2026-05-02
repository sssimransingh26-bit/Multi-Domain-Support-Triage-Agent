# code/multi_question_handler.py
"""
Detects and handles tickets with multiple questions.
Reuses risk detection from domain_router to avoid duplication.
"""

import re
from typing import List, Tuple
from dataclasses import dataclass
from utils import split_sentences, has_keyword
from domain_router import CompanyRouter


@dataclass
class Question:
    text: str
    question_type: str
    risk_level: str
    is_primary: bool = False
    index: int = 0


class MultiQuestionHandler:
    
    URGENT_KEYWORDS = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'right now']
    COMPLAINT_KEYWORDS = ['issue', 'problem', 'broken', 'not working', 'error', 'bug', 'crash']
    REQUEST_KEYWORDS = ['can you', 'could you', 'please', 'help', 'need', 'want']
    
    def __init__(self):
        self.router = CompanyRouter()
    
    def detect_multiple_questions(self, issue):
        """
        Split ticket into individual questions.
        Returns list sorted by priority (high risk first).
        """
        if not issue:
            return []
        
        sentences = split_sentences(issue)
        
        questions = []
        for idx, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            
            q_type = self._classify_sentence(sentence)
            risk_level, _ = self.router.detect_risk_level(sentence)
            is_primary = (idx == 0)
            
            questions.append(Question(
                text=sentence.strip(),
                question_type=q_type,
                risk_level=risk_level.value,
                is_primary=is_primary,
                index=idx
            ))
        
        questions.sort(key=lambda q: (
            q.risk_level != 'high',
            q.risk_level != 'medium',
            not q.is_primary,
            q.index
        ))
        
        return questions
    
    def _classify_sentence(self, sentence):
        """Classify what type of sentence this is."""
        if not sentence:
            return 'question'
        
        if has_keyword(sentence, self.URGENT_KEYWORDS):
            return 'urgent'
        elif has_keyword(sentence, self.COMPLAINT_KEYWORDS):
            return 'complaint'
        elif has_keyword(sentence, self.REQUEST_KEYWORDS):
            return 'request'
        else:
            return 'question'
    
    def merge_decision(self, questions):
        """
        Determine overall routing based on multiple questions.
        High risk question takes priority.
        Returns tuple of (status, routing_reason).
        """
        if not questions:
            return 'escalated', 'Empty ticket'
        
        primary = questions[0]
        
        if primary.risk_level == 'high':
            return 'escalated', f"High-risk: {primary.text[:50]}"
        
        reason = f"Primary: {primary.text[:60]}"
        if len(questions) > 1:
            reason += f" (plus {len(questions)-1} more)"
        
        return 'replied', reason