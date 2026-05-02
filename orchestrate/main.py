# code/main.py (COMPLETE CORRECTED VERSION)
"""
Multi-Domain Support Triage Agent with debugging
"""

import argparse
import csv
import sys
import time
from pathlib import Path

from retrieval import search, CORPUS
from domain_router import CompanyRouter, RiskLevel
from multi_question_handler import MultiQuestionHandler
from confidence_scorer import ConfidenceScorer
from justification_engine import JustificationEngine
from sentiment_analyzer import SentimentAnalyzer, Sentiment
from security_detector import SecurityDetector
from utils import split_sentences, calculate_text_length_score, has_keyword

try:
    from rich.console import Console
    from rich.progress import Progress
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def process_ticket(issue, subject, company, debug=False):
    """
    Process a single support ticket through the triage pipeline.
    """
    
    router = CompanyRouter()
    mq_handler = MultiQuestionHandler()
    confidence_scorer = ConfidenceScorer()
    justification_engine = JustificationEngine()
    sentiment_analyzer = SentimentAnalyzer()
    security_detector = SecurityDetector()
    
    # Validate text - only reject truly empty tickets
    if not issue or len(issue.strip()) < 10:
        return {
            'issue': issue,
            'subject': subject,
            'company': company,
            'status': 'replied',
            'product_area': 'General',
            'request_type': 'invalid',
            'response': 'Your request is too short or empty. Please provide more details.',
            'justification': 'Invalid: Empty or too short to process.',
            'confidence_score': 0.0,
            'sentiment': 'neutral',
            'urgency_level': 0,
            'risk_category': 'low',
            'multiple_questions': False,
        }
    
    # Security check
    is_malicious, mal_reason = security_detector.detect_injection(issue)
    if is_malicious:
        return {
            'issue': issue[:300],
            'subject': subject[:100] if subject else '',
            'company': company,
            'status': 'replied',
            'product_area': 'General',
            'request_type': 'invalid',
            'response': 'This request is outside the scope of our support services. Please submit a genuine support question.',
            'justification': justification_engine.generate('invalid', 'injection'),
            'confidence_score': 0.0,
            'sentiment': 'neutral',
            'urgency_level': 0,
            'risk_category': 'low',
            'multiple_questions': False,
        }
    
    # Infer company
    inferred_company, company_confidence = router.infer_company(issue, subject, company)
    if not inferred_company or inferred_company == "unknown":
        inferred_company = company if company and company.lower() != 'none' else 'unknown'
    
    if debug:
        print(f"  Company: {inferred_company} (confidence: {company_confidence:.0f}%)")
    
    # Sentiment analysis
    sentiment, urgency = sentiment_analyzer.analyze(issue)
    escalate_for_sentiment = sentiment_analyzer.should_escalate_for_sentiment(sentiment, urgency)
    
    # Risk detection
    risk_level, risk_keywords = router.detect_risk_level(issue)
    
    if debug and risk_level == RiskLevel.HIGH:
        print(f"  HIGH RISK DETECTED: {risk_keywords}")
    
    # Multiple questions
    questions = mq_handler.detect_multiple_questions(issue)
    
    # Retrieve documentation
    query = f"{subject} {issue}" if subject else issue
    docs = search(query, inferred_company, top_k=5)
    
    if debug:
        print(f"  Query: {query[:60]}")
        print(f"  Documents found: {len(docs)}")
        if docs:
            print(f"  Top doc: {docs[0]['title']} (score: {docs[0].get('score', 0)})")
    
    # Compute confidence inputs
    if docs:
        retrieval_score = (len(docs) / 5.0) * 100.0
    else:
        retrieval_score = 0.0
    
    # Match exactness
    match_exactness = 0.0
    if docs:
        doc_content = docs[0].get('content', '').lower()
        doc_title = docs[0].get('title', '').lower()
        query_lower = query.lower()
        
        query_words = [w for w in query_lower.split() if len(w) > 3]
        
        if query_words:
            matches = 0
            for word in query_words:
                if word in doc_content or word in doc_title:
                    matches += 1
            match_exactness = (matches / len(query_words)) * 100.0
        else:
            match_exactness = 50.0
    
    # Policy clarity
    policy_clarity = 0.0
    if docs:
        doc_length = len(docs[0].get('content', ''))
        if doc_length > 0:
            policy_clarity = min((doc_length / 1000.0) * 100.0, 100.0)
        else:
            policy_clarity = 20.0
    
    # Ambiguity
    ambiguity = 0.0
    if len(questions) > 1:
        ambiguity = len(questions) * 20.0
    else:
        ambiguity = 10.0
    
    ambiguity = min(ambiguity, 100.0)
    
    # Calculate confidence
    confidence = 0.0
    
    if retrieval_score > 0:
        weights = {
            'retrieval': 0.35,
            'exactness': 0.30,
            'clarity': 0.25,
            'ambiguity': 0.10
        }
        
        if risk_level == RiskLevel.HIGH:
            weights['retrieval'] = 0.45
            weights['exactness'] = 0.30
            weights['clarity'] = 0.15
            weights['ambiguity'] = 0.10
        
        ambiguity_score = 100.0 - ambiguity
        
        confidence = (
            retrieval_score * weights['retrieval'] +
            match_exactness * weights['exactness'] +
            policy_clarity * weights['clarity'] +
            ambiguity_score * weights['ambiguity']
        )
        
        if len(questions) > 1:
            confidence *= 0.85
        
        if retrieval_score < 40:
            confidence *= 0.6
    
    confidence = max(0.0, min(100.0, confidence))
    
    if debug:
        print(f"  Retrieval: {retrieval_score:.1f}, Exactness: {match_exactness:.1f}, Clarity: {policy_clarity:.1f}")
        print(f"  Final confidence: {confidence:.1f}%")
    
    # Determine escalation
    should_escalate = False
    escalation_reason = None
    
    if risk_level == RiskLevel.HIGH:
        should_escalate = True
        escalation_reason = 'high_risk'
    elif retrieval_score == 0 and risk_level != RiskLevel.LOW:
        should_escalate = True
        escalation_reason = 'no_docs'
    elif confidence < 30:
        should_escalate = True
        escalation_reason = 'low_confidence'
    elif escalate_for_sentiment:
        should_escalate = True
        escalation_reason = 'sentiment'
    
    status = 'escalated' if should_escalate else 'replied'
    
    # Product area
    product_area = docs[0]['category'] if docs else 'General'
    
    # Request type
    request_type = 'product_issue'
    if has_keyword(issue, ['bug', 'broken', 'not working', 'error', 'crash']):
        request_type = 'bug'
    elif has_keyword(issue, ['feature', 'add', 'implement', 'suggestion']):
        request_type = 'feature_request'
    
    # Response generation
    if status == 'escalated':
        if risk_level == RiskLevel.HIGH:
            response = f"Thank you for contacting {inferred_company} support. Due to the sensitive nature of your request, we are escalating to our specialist team for immediate assistance."
        elif escalation_reason == 'no_docs':
            response = f"We appreciate your inquiry. A {inferred_company} support specialist will review your ticket and provide a detailed response."
        else:
            response = "Thank you for reaching out. Our support team will review your request and get back to you shortly."
    else:
        if docs:
            response = f"Based on {inferred_company} support documentation: {docs[0].get('content', '')[:250]}. For more details, see {docs[0].get('url', '')}"
        else:
            response = f"We are here to help. Please refer to our {inferred_company} support documentation or contact our team for assistance."
    
    # Justification
    if status == 'escalated':
        if escalation_reason == 'high_risk':
            reason = 'high_risk'
        elif escalation_reason == 'low_confidence':
            reason = 'low_confidence'
        elif escalation_reason == 'no_docs':
            reason = 'no_docs'
        else:
            reason = 'general'
        justification = justification_engine.generate(
            'escalated', reason, product_area,
            risk_level=risk_level.value if risk_level != RiskLevel.LOW else None,
            company=inferred_company or 'Support',
            question_count=len(questions)
        )
    else:
        reason = 'faq' if docs else 'general'
        justification = justification_engine.generate(
            'replied', reason, product_area,
            confidence=confidence,
            company=inferred_company or 'Support',
            question_count=len(questions)
        )
    
    return {
        'issue': issue[:300],
        'subject': subject[:100] if subject else '',
        'company': inferred_company or 'unknown',
        'status': status,
        'product_area': product_area,
        'request_type': request_type,
        'response': response[:300],
        'justification': justification,
        'confidence_score': round(confidence, 1),
        'sentiment': sentiment.value,
        'urgency_level': urgency,
        'risk_category': risk_level.value,
        'multiple_questions': len(questions) > 1,
    }


def main():
    parser = argparse.ArgumentParser(description="Support Triage Agent")
    parser.add_argument("input_csv", help="Path to support_tickets.csv")
    parser.add_argument("--output", "-o", default=None, help="Output CSV path")
    parser.add_argument("--debug", action="store_true", help="Show debug output")
    args = parser.parse_args()
    
    input_path = Path(args.input_csv)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)
    
    output_path = Path(args.output) if args.output else input_path.parent / "output.csv"
    
    print(f"Corpus loaded: {len(CORPUS)} documents")
    print()
    
    # Read input
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Processing {len(rows)} tickets...")
    print()
    
    # Process tickets
    results = []
    start = time.time()
    
    for i, row in enumerate(rows, 1):
        issue = row.get("Issue", "").strip()
        subject = row.get("Subject", "").strip()
        company = row.get("Company", "").strip()
        
        debug = args.debug or (i <= 3)
        
        if debug:
            print(f"\n[{i}] {subject[:50] if subject else issue[:50]}")
        
        result = process_ticket(issue, subject, company, debug=debug)
        results.append(result)
    
    elapsed = time.time() - start
    
    # Write output
    fieldnames = [
        'issue', 'subject', 'company', 'status', 'product_area', 'request_type',
        'response', 'justification', 'confidence_score', 'sentiment',
        'urgency_level', 'risk_category', 'multiple_questions'
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Summary
    replied = sum(1 for r in results if r['status'] == 'replied')
    escalated = sum(1 for r in results if r['status'] == 'escalated')
    avg_confidence = sum(r['confidence_score'] for r in results) / len(results) if results else 0
    
    print(f"\n\nCompleted in {elapsed:.2f} seconds")
    print(f"Output written to: {output_path}")
    print(f"Total tickets: {len(results)}")
    print(f"Replied: {replied} ({replied*100//len(results)}%)")
    print(f"Escalated: {escalated} ({escalated*100//len(results)}%)")
    print(f"Average confidence: {avg_confidence:.1f}%")


if __name__ == "__main__":
    main()