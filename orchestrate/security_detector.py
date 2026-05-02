
"""
Detects adversarial or malicious content in tickets.
Identifies prompt injection and jailbreak attempts.
"""

import re
from typing import Tuple, List
from utils import has_keyword


class SecurityDetector:
    
    INJECTION_KEYWORDS = [
        'delete', 'drop', 'execute', 'rm -rf', 'sql injection', 'eval',
        'exec', 'bash', 'shell', 'command', 'give me the code',
        'show me', 'display', 'bypass', 'override'
    ]
    
    SUSPICIOUS_PATTERNS = [
        r'(give|show|display)\s+(me|the)\s+(code|password|key)',
        r'(execute|run)\s+(this|that)\s+(command|code)',
        r'(delete|drop)\s+(all|everything|the)',
        r'(bypass|override)\s+(security|rule|filter)',
    ]
    
    def detect_injection(self, issue):
        """
        Detect if ticket contains injection or jailbreak attempts.
        Returns tuple of (is_malicious, reason).
        """
        if not issue:
            return False, ""
        
        if has_keyword(issue, self.INJECTION_KEYWORDS):
            return True, "Potential injection attempt detected"
        
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, issue.lower(), re.IGNORECASE):
                return True, "Suspicious pattern detected"
        
        return False, ""
    
    def flag_suspicious_content(self, issue):
        """Return list of suspicious elements found."""
        flags = []
        
        is_malicious, reason = self.detect_injection(issue)
        if is_malicious:
            flags.append(reason)
        
        return flags