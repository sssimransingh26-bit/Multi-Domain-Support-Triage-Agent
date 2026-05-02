
"""
Shared utility functions for the triage agent.
Prevents code duplication across modules.
"""

import re
from typing import List


def has_keyword(text, keywords):
    """
    Check if any keyword exists in text using word boundaries.
    Prevents false matches like 'fraud' matching inside 'defraud'.
    """
    if not text or not keywords:
        return False
    
    text_lower = text.lower()
    for keyword in keywords:
        if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
            return True
    return False


def get_matched_keywords(text, keywords):
    """
    Get list of keywords that matched in text.
    Useful for tracking which signals triggered a decision.
    """
    if not text or not keywords:
        return []
    
    text_lower = text.lower()
    matched = []
    for keyword in keywords:
        if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
            matched.append(keyword)
    return matched


def split_sentences(text):
    """
    Split text into sentences.
    Handles periods, question marks, exclamation marks, and newlines.
    """
    if not text:
        return []
    
    sentences = re.split(r'[.?!\n]+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def is_all_caps_urgent(text):
    """
    Check if text has urgent ALL CAPS sections.
    Indicates elevated urgency level.
    """
    if not text:
        return False
    
    words = text.split()
    if len(words) < 3:
        return False
    
    caps_words = sum(1 for w in words if w.isupper() and len(w) > 1)
    return caps_words / len(words) >= 0.3


def calculate_text_length_score(text):
    """
    Calculate if text is adequate length.
    Returns 0 for very short text, 1 for reasonable length.
    FIXED: Less strict threshold
    """
    if not text:
        return 0.0
    
    # Remove newlines and extra whitespace, then check actual content length
    cleaned = ' '.join(text.split())
    
    # Very short threshold - only reject if less than 10 characters after cleanup
    if len(cleaned) < 10:
        return 0.0
    
    return min(1.0, len(cleaned) / 100.0)