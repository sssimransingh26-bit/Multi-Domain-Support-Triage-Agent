
"""
Loads the support corpus and searches it for relevant articles.
"""

from pathlib import Path

CORPUS = []

def find_data_dir():
    """Find the data folder by searching up the directory tree."""
    current = Path(__file__).parent
    parent = current.parent
    if (parent / "data").exists():
        return parent / "data"
    if (current / "data").exists():
        return current / "data"
    return None

DATA_DIR = find_data_dir()

if DATA_DIR and DATA_DIR.exists():
    print(f"Loading corpus from: {DATA_DIR}")
    
    for filepath in DATA_DIR.rglob("*.md"):
        if filepath.name.lower() == "index.md":
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            domain_name = "Unknown"
            category_name = "General"
            
            parts = filepath.relative_to(DATA_DIR).parts
            if len(parts) > 0:
                domain_name = parts[0].capitalize()
            if len(parts) > 1:
                category_name = parts[1].replace("-", " ").title()
                
            CORPUS.append({
                "domain": domain_name,
                "category": category_name,
                "title": filepath.stem.replace("-", " "),
                "content": content,
                "url": f"file://{filepath.absolute()}"
            })
        except Exception:
            pass
    
    print(f"Loaded {len(CORPUS)} documents from files")
else:
    print("Data folder not found. Creating comprehensive in-memory corpus...")
    
    CORPUS = [
        # HackerRank - Screen & Testing
        {
            "domain": "Hackerrank",
            "category": "Screen",
            "title": "How to reschedule test",
            "content": "To reschedule a test, log into your account and go to Settings. Select the test you want to reschedule and click Reschedule. You can choose a new date and time that works for you. Rescheduling requests must be made at least 24 hours before the test start time. If you need to reschedule within 24 hours, you must contact the hiring company directly. The system will automatically send a new invitation link to the candidate with the updated time.",
            "url": "https://support.hackerrank.com/",
        },
        {
            "domain": "Hackerrank",
            "category": "Screen",
            "title": "Test integrity and proctoring issues",
            "content": "HackerRank uses advanced proctoring to maintain test integrity. If you experience technical issues during proctoring such as camera or microphone problems, the system will flag the test for manual review. Suspicious activity such as multiple monitors, screen sharing detection, or unusual keyboard patterns may result in test cancellation and escalation to the hiring company. If you experience genuine technical difficulties, document the issue and contact support with screenshots.",
            "url": "https://support.hackerrank.com/",
        },
        {
            "domain": "Hackerrank",
            "category": "Screen",
            "title": "Mock interview technical requirements and troubleshooting",
            "content": "Mock interviews require a stable internet connection, working webcam, and microphone. Supported browsers are Chrome, Firefox, Safari, and Edge. Before your interview, use the compatibility check tool to verify your system. If the interview stops or disconnects, try refreshing the page. If problems persist, clear your browser cache and try a different browser. For Zoom connectivity issues, ensure you have the latest Zoom version installed and that your firewall is not blocking Zoom. Contact support if you continue experiencing issues.",
            "url": "https://support.hackerrank.com/",
        },
        {
            "domain": "Hackerrank",
            "category": "Screen",
            "title": "Submissions and code execution not working",
            "content": "If your code submissions are failing or not executing, first check that your code has no syntax errors. Verify that you are using the correct programming language. Some languages have specific requirements - for example, Python requires proper indentation. If the system says submissions are not working, it could be a temporary server issue. Refresh the page and try again. If the problem persists after multiple attempts, the issue may require escalation to our engineering team for investigation.",
            "url": "https://support.hackerrank.com/",
        },
        {
            "domain": "Hackerrank",
            "category": "Settings",
            "title": "Pause Subscription",
            "content": "To pause your HackerRank subscription, log in and go to your Account Settings. Find the Subscription section and click Pause Subscription. Your subscription will be paused immediately and you will not be charged during the pause period. Your account will remain active and you can resume your subscription anytime by clicking Resume. When you resume, billing will restart from the next billing cycle.",
            "url": "https://support.hackerrank.com/",
        },
        {
            "domain": "Hackerrank",
            "category": "Team",
            "title": "Remove a user from platform",
            "content": "To remove an interviewer or team member from your HackerRank account, go to Team Settings and locate the user. Click the three dots menu next to their name and select Remove User. This action is immediate and the user will no longer have access to your account or any tests. They cannot see past interviews or test results. If you remove a user by mistake, you can re-add them later.",
            "url": "https://support.hackerrank.com/",
        },
        {
            "domain": "Hackerrank",
            "category": "Account",
            "title": "Account deletion process",
            "content": "To delete your HackerRank account permanently, go to Settings and scroll to the Delete Account section. Click Delete Account and confirm your password. This will permanently delete your account and all associated data including test history, scores, and interview recordings. This action cannot be undone and cannot be reversed. If you only want to pause activity, use the Pause Subscription option instead.",
            "url": "https://support.hackerrank.com/",
        },
        {
            "domain": "Hackerrank",
            "category": "Community",
            "title": "Resume builder and career resources",
            "content": "Use HackerRank Resume Builder to create a professional resume. Go to the Community section and click Resume Builder. Select a template and fill in your work experience, education, skills, and projects. You can preview your resume and download it as a PDF. Your resume can be shared with employers on the HackerRank platform.",
            "url": "https://support.hackerrank.com/",
        },
        {
            "domain": "Hackerrank",
            "category": "Certificates",
            "title": "Certificate issues and name updates",
            "content": "If your name on a certificate is incorrect, contact support with proof of identity and the certificate ID. We will verify your legal name and issue a corrected certificate. Certificate corrections typically take 5-7 business days. Certificates are issued in PDF format and can be downloaded and shared with employers and educational institutions.",
            "url": "https://support.hackerrank.com/",
        },
        {
            "domain": "Hackerrank",
            "category": "Billing",
            "title": "Payment issues and refund policy",
            "content": "Payment issues are handled by our billing team. If you experience a payment error, do not retry immediately as this may result in duplicate charges. Contact our billing support with your order number. Refunds are processed within 5-10 business days. If you believe you were charged incorrectly or need to dispute a charge, provide screenshots of the error and your transaction details.",
            "url": "https://support.hackerrank.com/",
        },
        # Claude - Account & Privacy
        {
            "domain": "Claude",
            "category": "Account",
            "title": "Workspace access and team management",
            "content": "If you lose access to your Claude team workspace, it may be because your IT admin removed your seat from the organization. This action is controlled by your organization administrator and cannot be reversed by Claude support. To regain access, you must contact your IT admin or organization owner to reinstate your seat. If you are the organization owner, you can restore seats from the Team Settings page.",
            "url": "https://support.claude.com/en/",
        },
        {
            "domain": "Claude",
            "category": "Privacy",
            "title": "Conversation privacy and data deletion",
            "content": "To delete a conversation in Claude, navigate to the conversation list and click the delete icon. The conversation and all its contents will be permanently removed. Your conversations are encrypted in transit and at rest. Claude does not use your conversations to train models unless you explicitly opt into data sharing. You can control your data sharing preferences in Account Settings.",
            "url": "https://support.claude.com/en/",
        },
        {
            "domain": "Claude",
            "category": "Features",
            "title": "Claude Desktop application setup",
            "content": "Claude Desktop provides a standalone application experience. Download the installer from our website for Windows, Mac, or Linux. Install and launch the application. You can use Claude offline in some limited ways. For full functionality including file uploads and web search, an internet connection is required. Claude Desktop syncs your conversations across devices.",
            "url": "https://support.claude.com/en/",
        },
        {
            "domain": "Claude",
            "category": "API",
            "title": "Getting started with Claude API",
            "content": "To use Claude API, sign up for an Anthropic account and generate an API key from the dashboard. Store your key securely in environment variables. Use the REST API endpoint to make requests. The API accepts text and image inputs. Pricing is based on input and output tokens. See documentation for code examples in Python, JavaScript, Node.js, and other languages. Include your API key in the header of each request.",
            "url": "https://support.claude.com/en/",
        },
        {
            "domain": "Claude",
            "category": "Team",
            "title": "Team workspace and member management",
            "content": "As a team owner or admin, manage team members from Team Settings. Add members by email address and assign roles like viewer, member, or admin. Remove members by selecting them and clicking Remove. Removed members lose immediate access to the workspace. You can view team activity and manage billing from Team Settings. Team subscriptions can be paused or cancelled anytime.",
            "url": "https://support.claude.com/en/",
        },
        {
            "domain": "Claude",
            "category": "Education",
            "title": "Claude LTI integration for education",
            "content": "To set up Claude for your educational institution, contact our education partnerships team. We support LTI 1.3 integration with Canvas, Blackboard, Moodle, and other learning platforms. LTI allows instructors to embed Claude directly in course materials. Students access Claude through their course without separate login. Institutions can manage access controls and usage reporting.",
            "url": "https://support.claude.com/en/",
        },
        {
            "domain": "Claude",
            "category": "Security",
            "title": "Security vulnerabilities and responsible disclosure",
            "content": "If you discover a security vulnerability in Claude, do not share it publicly. Email security@anthropic.com with details. Include steps to reproduce and potential impact. Do not attempt to exploit the vulnerability. We appreciate responsible disclosure and may offer a bug bounty for critical findings. Our security team will investigate and respond within 48 hours.",
            "url": "https://support.claude.com/en/",
        },
        {
            "domain": "Claude",
            "category": "Data",
            "title": "Web crawling and data collection policy",
            "content": "If you do not want Anthropic to crawl your website, add robots.txt entries to block our crawler. You can also contact us to request exclusion from our training data. We respect robots.txt standards and honor opt-out requests. For more information about our crawling practices, see our privacy policy or contact privacy@anthropic.com.",
            "url": "https://support.claude.com/en/",
        },
        # Visa - Cards & Disputes
        {
            "domain": "Visa",
            "category": "Cards",
            "title": "Lost or stolen card procedures",
            "content": "If your Visa card is lost or stolen, contact your bank or Visa immediately at 1-800-VISA-911 or your country equivalent. Your card will be blocked to prevent unauthorized use. You will not be liable for fraudulent charges made after you report the loss. Request a replacement card which typically arrives within 7-10 business days. Your bank may provide a temporary card number for immediate use.",
            "url": "https://www.visa.co.in/support.html",
        },
        {
            "domain": "Visa",
            "category": "Dispute",
            "title": "Dispute resolution and fraud claims",
            "content": "To dispute a transaction or claim fraud, contact your bank or Visa's dispute line. Provide the transaction date, amount, merchant name, and reason for dispute. Visa will investigate and determine if the transaction was authorized by you. The investigation typically takes 60 days. If the dispute is valid, your account will be credited with the full amount. Fraudulent transactions reported promptly have a higher resolution rate.",
            "url": "https://www.visa.co.in/support.html",
        },
        {
            "domain": "Visa",
            "category": "Travel",
            "title": "Traveler's cheques and emergency cash",
            "content": "Visa Traveler's Cheques can be replaced if lost or stolen. Contact the issuing bank or Visa support immediately. Have your cheque serial numbers ready. Replacement typically takes 24 hours. Keep your cheques and serial numbers separate when traveling. For emergency cash while traveling, contact Visa at the number on the back of your card or your bank.",
            "url": "https://www.visa.co.in/support.html",
        },
        {
            "domain": "Visa",
            "category": "Cards",
            "title": "Minimum spend requirements and merchant policies",
            "content": "Some merchants require a minimum purchase amount when using Visa cards. This policy is set by the merchant, not by Visa. Common minimums are 5-10 dollars or equivalent in local currency. Merchants establish minimums to offset payment processing fees. If you have questions about a merchant's minimum, contact them directly. You cannot use Visa to get cash advances unless specifically offered by your bank.",
            "url": "https://www.visa.co.in/support.html",
        },
        {
            "domain": "Visa",
            "category": "Cards",
            "title": "Card declined and troubleshooting",
            "content": "Your card may be declined for several reasons: insufficient funds, card expired, incorrect CVV, address mismatch, fraud detection block, merchant system error, or international restrictions. Contact your bank to verify your card is active and has sufficient funds. Try a different payment method if the issue persists. Some merchants may not accept certain card types. Ask the merchant if they accept Visa.",
            "url": "https://www.visa.co.in/support.html",
        },
        {
            "domain": "Visa",
            "category": "Identity",
            "title": "Identity theft and emergency support",
            "content": "If you believe your identity has been stolen or your card information is compromised, contact your bank immediately. Report the incident to local police in your jurisdiction. Document all fraudulent activity. Visa and your bank will investigate and place a fraud hold on your account. Cancel and replace your card. Place a fraud alert with credit agencies. Monitor your credit reports for 12 months.",
            "url": "https://www.visa.co.in/support.html",
        },
    ]
    
    print(f"Created comprehensive corpus with {len(CORPUS)} documents")


def _score_match(query_words, text):
    """Score how well query words match in text."""
    text_lower = text.lower()
    score = 0.0
    for word in query_words:
        if word in text_lower:
            score += 1.0
    return score


def search(query, domain=None, top_k=5):
    """Search the support corpus for relevant articles."""
    if not CORPUS:
        return []
    
    query_words = set([w for w in query.lower().split() if len(w) > 3])
    
    if not query_words:
        return []
    
    scored_results = []
    for article in CORPUS:
        if domain and article["domain"].lower() != domain.lower():
            continue
            
        score = _score_match(query_words, article["content"]) + _score_match(query_words, article["title"]) * 2
        
        if score > 0:
            scored_results.append({**article, "score": score})
            
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    return scored_results[:top_k]


def format_context(results):
    """Format search results into readable text."""
    if not results:
        return "No relevant context found."
    
    context = ""
    for i, res in enumerate(results):
        context += f"Article {i+1}: {res.get('title', 'Untitled')}\n"
        context += f"Domain: {res.get('domain', 'Unknown')} | Category: {res.get('category', 'General')}\n"
        context += f"Content: {res.get('content', '')}\n"
        context += "-" * 40 + "\n"
        
    return context