"""
Analyzes emotional tone and urgency of support tickets.
Used to detect when users need immediate attention.
"""

from enum import Enum
from typing import Tuple
from utils import has_keyword, is_all_caps_urgent


class Sentiment(Enum):
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class SentimentAnalyzer:
    
    ANGRY_KEYWORDS = ['unacceptable', 'disgusted', 'outrageous', 'you must', 
                      'demand', 'ridiculous', 'terrible', 'worst', 'scam']
    FRUSTRATED_KEYWORDS = ['frustrated', 'upset', 'please help', 'asap', 
                          'urgent', 'immediately', 'hurry', 'annoyed']
    POSITIVE_KEYWORDS = ['thanks', 'appreciate', 'great', 'happy', 'excellent', 
                        'love', 'pleased', 'grateful']
    
    def analyze(self, issue):
        """
        Analyze sentiment and urgency level.
        Returns tuple of (sentiment_type, urgency_0_to_10).
        """
        if not issue:
            return Sentiment.NEUTRAL, 0
        
        angry_count = sum(1 for kw in self.ANGRY_KEYWORDS if has_keyword(issue, [kw]))
        frustrated_count = sum(1 for kw in self.FRUSTRATED_KEYWORDS if has_keyword(issue, [kw]))
        positive_count = sum(1 for kw in self.POSITIVE_KEYWORDS if has_keyword(issue, [kw]))
        
        if angry_count > 0:
            sentiment = Sentiment.ANGRY
        elif frustrated_count > 0:
            sentiment = Sentiment.FRUSTRATED
        elif positive_count > frustrated_count:
            sentiment = Sentiment.POSITIVE
        else:
            sentiment = Sentiment.NEUTRAL
        
        urgency = 0
        urgency += angry_count * 3
        urgency += frustrated_count * 2
        urgency += (3 if '!!!' in issue else 0)
        urgency += (2 if '!!' in issue else 0)
        urgency += (1 if '!' in issue else 0)
        urgency += (2 if is_all_caps_urgent(issue) else 0)
        
        return sentiment, min(10, urgency)
    
    def should_escalate_for_sentiment(self, sentiment, urgency):
        """
        Determine if emotional state warrants escalation.
        Only escalates if both angry AND urgent.
        """
        if sentiment == Sentiment.ANGRY and urgency >= 6:
            return True
        return False