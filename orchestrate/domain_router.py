"""
Handles company detection and risk assessment.
Risk detection is centralized here to prevent duplication.
"""

import re
from typing import Tuple, List
from enum import Enum
from utils import has_keyword, get_matched_keywords


class RiskLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CompanyRouter:
    
    COMPANY_KEYWORDS = {
        'HackerRank': [
            'hackerrank', 'hacker rank', 'coding test', 'coding challenge',
            'screen test', 'proctoring', 'interview', 'hiring', 'recruiter',
            'candidate', 'assessment', 'skillup', 'chakra', 'test integrity'
        ],
        'Claude': [
            'claude', 'anthropic', 'artifact', 'pro plan', 'max plan',
            'claude.ai', 'claude code', 'console.anthropic', 'api key',
            'conversation', 'chat', 'workspace', 'team'
        ],
        'Visa': [
            'visa card', 'visa debit', 'visa credit', '3-d secure',
            'verified by visa', 'lost card', 'stolen card', 'atm locator',
            'visa concierge', 'card declined', 'merchant'
        ]
    }
    
    RISK_KEYWORDS = {
        'fraud': ['fraud', 'stolen', 'unauthorized', 'hacked', 'identity theft', 'scam'],
        'security': ['security', 'vulnerability', 'breach', 'exploit', 'compromised', 'leak'],
        'billing': ['refund', 'payment', 'bill', 'charge', 'subscription', 'overcharged', 'double charged'],
        'legal': ['legal', 'lawsuit', 'attorney', 'compliance', 'regulatory', 'sue'],
        'access': ['access denied', 'locked', 'removed', 'deleted', 'restore', 'suspended', 'banned'],
        'abuse': ['abuse', 'harassment', 'discrimination', 'inappropriate']
    }
    
    def infer_company(self, issue, subject, company):
        """
        Infer company from keywords if not provided.
        Returns tuple of (company_name, confidence_0_to_100).
        Confidence is based on keyword matches found.
        """
        if company and company.strip().lower() not in ('none', '', 'null', 'nan'):
            return company.strip(), 100.0
        
        combined_text = (issue + ' ' + subject).lower()
        scores = {}
        
        for company_name, keywords in self.COMPANY_KEYWORDS.items():
            matched = get_matched_keywords(combined_text, keywords)
            scores[company_name] = len(matched)
        
        total_matches = sum(scores.values())
        if total_matches == 0:
            return "unknown", 0.0
        
        best_company = max(scores, key=scores.get)
        max_score = scores[best_company]
        
        confidence = (max_score / max(len(self.COMPANY_KEYWORDS[best_company]), 1)) * 100
        confidence = min(100, max(0, confidence))
        
        return best_company, confidence
    
    def detect_risk_level(self, text):
        """
        Detect risk level of the ticket.
        High risk includes fraud, security, billing, and legal issues.
        Returns tuple of (risk_level, matched_risk_types).
        """
        if not text:
            return RiskLevel.LOW, []
        
        matched_risks = []
        
        for risk_type, keywords in self.RISK_KEYWORDS.items():
            if has_keyword(text, keywords):
                matched_risks.append(risk_type)
        
        if 'fraud' in matched_risks or 'security' in matched_risks:
            return RiskLevel.HIGH, matched_risks
        elif 'billing' in matched_risks or 'legal' in matched_risks:
            return RiskLevel.HIGH, matched_risks
        elif 'access' in matched_risks or 'abuse' in matched_risks:
            return RiskLevel.MEDIUM, matched_risks
        else:
            return RiskLevel.LOW, matched_risks
    
    def get_inferred_domain(self, issue, subject, company):
        """
        Get the domain name for corpus search.
        Returns None if company cannot be determined.
        """
        inferred, _ = self.infer_company(issue, subject, company)
        if inferred and inferred != "unknown":
            return inferred
        return None