
"""
Generates clear, concise justifications for triage decisions.
Ensures all decisions are traceable and understandable.
"""


class JustificationEngine:
    
    TEMPLATES = {
        'replied_faq': "Replied: Clear FAQ found in {area}.",
        'replied_procedure': "Replied: Step-by-step guide available.",
        'replied_general': "Replied: Addressed based on {area} documentation.",
        
        'escalated_high_risk': "Escalated: High-risk issue ({risk}). Specialist review needed.",
        'escalated_billing': "Escalated: Billing issue requires specialist.",
        'escalated_no_docs': "Escalated: No relevant documentation found.",
        'escalated_low_confidence': "Escalated: Insufficient documentation match.",
        'escalated_multi': "Escalated: Multiple complex questions require review.",
        'escalated_oob': "Escalated: Out of scope or requires external coordination.",
        
        'invalid_injection': "Invalid: Request outside scope of support.",
        'invalid_empty': "Invalid: Empty or too short to process.",
        'invalid_oob': "Invalid: Not relevant to {company}.",
    }
    
    def generate(self, 
                 decision,
                 reason,
                 product_area="General",
                 risk_level=None,
                 confidence=75.0,
                 company='Support',
                 question_count=1):
        """
        Generate a clear justification for the decision.
        Only includes confidence for replies, not escalations.
        """
        
        template_key = f"{decision.lower()}_{reason.lower()}"
        template = self.TEMPLATES.get(template_key, 
                                     self.TEMPLATES.get(f"{decision.lower()}_general", 
                                                       f"{decision}: {reason}"))
        
        justification = template.format(
            area=product_area,
            risk=risk_level or 'sensitive matter',
            company=company
        )
        
        if decision.lower() == 'replied':
            justification += f" Confidence: {int(confidence)}%"
        
        if question_count > 1:
            justification += f" ({question_count} questions)"
        
        if len(justification) > 180:
            justification = justification[:177] + "..."
        
        return justification