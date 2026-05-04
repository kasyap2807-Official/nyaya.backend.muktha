import os
import json
import logging
import time
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any, Tuple
from functools import wraps
from enum import Enum
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, Field
from dotenv import load_dotenv
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)
from cachetools import TTLCache
import re

load_dotenv()

MISTRAL_API_KEY       = os.getenv("MISTRAL_API_KEY", "").strip()
MISTRAL_MODEL         = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
MAX_TOKENS            = int(os.getenv("MAX_TOKENS", "4000"))
TEMPERATURE           = float(os.getenv("TEMPERATURE", "0.2"))
HOST                  = os.getenv("HOST", "0.0.0.0")
PORT                  = int(os.getenv("PORT", "8000"))
DEFAULT_JURISDICTION  = os.getenv("DEFAULT_JURISDICTION", "India")
ALLOW_USER_API_KEY    = os.getenv("ALLOW_USER_API_KEY", "true").lower() == "true"
MAX_SCENARIO_LENGTH   = int(os.getenv("MAX_SCENARIO_LENGTH", "5000"))
CACHE_TTL             = int(os.getenv("CACHE_TTL", "3600"))
MAX_RETRIES           = int(os.getenv("MAX_RETRIES", "3"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
ENABLE_CACHE          = os.getenv("ENABLE_CACHE", "true").lower() == "true"
FILTER_PROFANITY      = os.getenv("FILTER_PROFANITY", "true").lower() == "true"
REDACT_PII            = os.getenv("REDACT_PII", "true").lower() == "true"
VALIDATION_STRICTNESS = os.getenv("VALIDATION_STRICTNESS", "medium")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("nyayaai.analysis")

try:
    from mistralai import Mistral
    log.info("Using mistralai >= 1.x import path")
except ImportError:
    try:
        from mistralai.client import Mistral
        log.info("Using mistralai.client import path")
    except ImportError:
        from mistralai.client import MistralClient as Mistral
        log.info("Using legacy MistralClient import")


class QueryClassifier:
    LEGAL_KEYWORDS = [
        'murder', 'kill', 'death', 'homicide', 'assault', 'battery', 'robbery',
        'theft', 'burglary', 'dacoity', 'extortion', 'fraud', 'cheating',
        'forgery', 'counterfeit', 'rape', 'sexual assault', 'harassment', 'stalking',
        'kidnap', 'abduction', 'dowry', 'domestic violence', 'cruelty', 'attempt to murder',
        'dowry death', 'eve teasing', 'molestation', 'outraging modesty', 'voyeurism',
        'cyber stalking', 'online harassment', 'identity theft', 'phishing', 'hacking',
        'fir', 'complaint', 'police', 'case', 'court', 'judge', 'lawyer', 'advocate',
        'legal', 'violation', 'offense', 'crime', 'criminal', 'sentence', 'punishment',
        'fine', 'imprisonment', 'arrest', 'bail', 'custody', 'summons', 'warrant',
        'charge sheet', 'trial', 'hearing', 'appeal', 'petition', 'affidavit',
        'summons', 'notice', 'order', 'judgment', 'decree', 'stay order',
        'contract', 'agreement', 'property', 'ownership', 'title', 'deed', 'rent',
        'lease', 'landlord', 'tenant', 'eviction', 'possession', 'boundary dispute',
        'succession', 'inheritance', 'will', 'testament', 'probate', 'letters of administration',
        'debt', 'loan', 'recovery', 'default', 'bankruptcy', 'insolvency', 'liquidation',
        'specific performance', 'injunction', 'damages', 'compensation', 'tort',
        'divorce', 'maintenance', 'alimony', 'custody', 'child custody', 'visitation rights',
        'guardianship', 'adoption', 'annulment', 'judicial separation', 'restitution of conjugal rights',
        'marriage', 'wedding', 'dowry', 'stridhan', 'family court', 'mediation',
        'hacking', 'phishing', 'cyber', 'online fraud', 'identity theft', 'data breach',
        'privacy violation', 'digital arrest', 'cyber bullying', 'trolling', 'defamation online',
        'credit card fraud', 'bank fraud', 'upi fraud', 'sim swapping', 'otp fraud',
        'fundamental rights', 'constitution', 'article', 'writ', 'petition', 'habeas corpus',
        'mandamus', 'certiorari', 'quo warranto', 'prohibition', 'human rights',
        'legal aid', 'free legal aid', 'right to information', 'rti', 'right to privacy',
        'company', 'corporate', 'director', 'shareholder', 'insolvency', 'bankruptcy',
        'trademark', 'copyright', 'patent', 'intellectual property', 'merger', 'acquisition',
        'partnership dispute', 'llp', 'gst', 'income tax', 'tax evasion', 'service tax',
        'driving license', 'learner license', 'driving licence', 'dl', 'registration certificate',
        'rc', 'insurance', 'motor vehicle', 'traffic challan', 'speeding', 'rash driving',
        'accident', 'hit and run', 'drink driving', 'drunken driving', 'overloading',
        'helmet rule', 'seat belt', 'no entry violation', 'red light jumping',
        'vehicle seizure', 'impound', 'traffic police', 'mvi', 'transport department',
        'aadhar', 'pan card', 'voter id', 'passport', 'visa', 'pancard', 'aadhaar',
        'lost document', 'forget document', 'misplaced', 'missing certificate',
        'birth certificate', 'death certificate', 'marriage certificate', 'domicile',
        'caste certificate', 'income certificate', 'transfer certificate', 'tc',
        'lost', 'forget', 'forgot', 'misplaced', 'missing', 'stolen', 'damaged',
        'destroyed', 'renewal', 'renew', 'apply', 'application', 'process',
        'procedure', 'documentation', 'required documents', 'eligibility',
        'fees', 'fine', 'penalty', 'challan', 'pending', 'due', 'overdue',
        'salary', 'wages', 'employer', 'employee', 'termination', 'retrenchment',
        'layoff', 'fired', 'resignation', 'notice period', 'gratuity', 'pf', 'provident fund',
        'esi', 'bonus', 'overtime', 'leave encashment', 'compensation', 'workplace harassment',
        'sexual harassment at workplace', 'posh act', 'labour law', 'industrial dispute',
        'consumer complaint', 'defective product', 'deficient service', 'false advertising',
        'misleading ad', 'unfair trade practice', 'consumer court', 'consumer forum',
        'replacement', 'refund', 'compensation', 'cheated', 'scam', 'fraudulent',
        'flat', 'apartment', 'builder', 'developer', 'possession delayed', 'occupancy certificate',
        'completion certificate', 'stamp duty', 'registration', 'agreement for sale',
        'sale deed', 'title deed', 'encumbrance', 'mutation', 'khata', 'property tax',
        'bank account', 'savings account', 'fixed deposit', 'loan', 'credit card',
        'emi default', 'npa', 'non-performing asset', 'bank guarantee', 'cheque bounce',
        'stop payment', 'debit card fraud', 'atm fraud', 'net banking fraud',
        'medical negligence', 'hospital negligence', 'doctor negligence', 'wrong treatment',
        'medical error', 'compensation for injury', 'insurance claim', 'health insurance',
        'medi claim', 'cashless treatment', 'denial of claim',
        'problem', 'issue', 'dispute', 'conflict', 'disagreement', 'unfair', 'illegal',
        'wrong', 'cheated', 'scammed', 'victim', 'suffering', 'loss', 'damage',
        'injury', 'hurt', 'wound', 'accuse', 'alleged', 'suspect', 'witness',
        'caught', 'caught by police', 'detained', 'questioned', 'interrogated',
        'want to file case', 'want to complain', 'lodge complaint', 'register case',
        'legal action', 'police action', 'investigation', 'inquiry', 'enquiry',
        'urgent', 'emergency', 'immediate help', 'right now', 'fast', 'quick',
        'help', 'assist', 'guide', 'advise', 'suggest', 'recommend',
        'cash', 'money', 'payment', 'paid', 'paying', 'paid extra', 'overcharged',
        'refund', 'return money', 'recover money', 'money back', 'duplicate payment',
        'wrong transaction', 'reversal', 'chargeback', 'dispute transaction',
    ]

    LEGAL_SHORT_FORMS = {
        'fir': 'First Information Report',
        'ipc': 'Indian Penal Code (now replaced by BNS 2023)',
        'crpc': 'Code of Criminal Procedure (now replaced by BNSS 2023)',
        'bnss': 'Bharatiya Nagarik Suraksha Sanhita',
        'bns': 'Bharatiya Nyaya Sanhita',
        'bsa': 'Bharatiya Sakshya Adhiniyam',
        'rti': 'Right to Information',
        'gst': 'Goods and Services Tax',
        'cyber': 'Cyber crime',
        'divorce': 'Divorce and family law',
        'rent': 'Rental and tenancy laws',
        'property': 'Property laws',
        'contract': 'Contract laws',
        'dl': 'Driving License',
        'rc': 'Registration Certificate',
        'pan': 'Permanent Account Number',
        'aadhaar': 'Aadhaar Identification',
        'upi': 'Unified Payments Interface',
        'posh': 'Prevention of Sexual Harassment',
        'esi': 'Employees State Insurance',
        'pf': 'Provident Fund',
    }

    LEGAL_QUESTION_PATTERNS = [
        r'(what|how|why|when|where|can|is|are|do|does|did|will|would|could|should).*?(law|legal|right|police|court|file|complaint|case|procedure|process)',
        r'(is|are|does).*?(illegal|legal|criminal|punishable|valid|invalid|allowed|prohibited)',
        r'(can|how to).*?(file|register|apply|get|obtain|renew|make|lodge)',
        r'(what to do|what should i|what can i).*?(if|when|after|before)',
        r'(is this|was this).*?(legal|illegal|criminal|offence|crime)',
        r'(punishment|penalty|sentence|fine|jail|imprisonment).*?(for|of)',
        r'(compensation|damages|recovery|refund).*?(for|from)',
        r'(rights|entitlement|eligible|entitled).*?(under|as per|according to)',
        r'(forget|forgot|lost|misplaced|missing|stolen).*?(license|licence|document|card|certificate|money|cash)',
        r'(caught|arrested|detained|questioned).*?(police|customs)',
    ]

    GREETING_PATTERNS = [
        r'^(hi|hello|hey|greetings)[\s\!]*$',
        r'^good (morning|afternoon|evening)[\s\!]*$',
        r'^how are you[\s\?]*$',
        r'^what\'?s up[\s\?]*$',
        r'^nice to meet you',
        r'^i am \w+$',
        r'^my name is \w+$',
        r'^who are you[\s\?]*$',
        r'^what is your name[\s\?]*$',
        r'^tell me about yourself',
        r'^thanks?[\s\!]*$',
        r'^thank you[\s\!]*$',
        r'^bye|goodbye|see you',
        r'^ok|okay$'
    ]

    NON_LEGAL_PATTERNS = [
        r'weather|temperature|rain|sunny|cloudy',
        r'cricket|football|sports|game|match|tournament',
        r'movie|song|music|film|actor|actress|celebrity',
        r'recipe|cooking|food|restaurant|hotel|meal|dinner|lunch',
        r'joke|funny|humor|laugh|comedy',
        r'game|play|fun|entertainment',
        r'love|relationship|boyfriend|girlfriend|dating',
        r'^what is (ai|artificial intelligence|machine learning|chatgpt)',
        r'^how to (cook|bake|make|prepare).*?(food|cake|pizza|burger)',
    ]

    @classmethod
    def is_legal_scenario(cls, text: str) -> Tuple[bool, str]:
        text_lower = text.lower().strip()
        for short_form in cls.LEGAL_SHORT_FORMS.keys():
            if text_lower == short_form or text_lower.startswith(f"{short_form} ") or text_lower.endswith(f" {short_form}"):
                return True, f"legal_abbreviation_{short_form}"
        for pattern in cls.GREETING_PATTERNS:
            if re.match(pattern, text_lower, re.IGNORECASE):
                return False, "greeting_or_introduction"
        for pattern in cls.NON_LEGAL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "non_legal_conversation"
        for pattern in cls.LEGAL_QUESTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, "legal_question_pattern"
        legal_keyword_matches = [kw for kw in cls.LEGAL_KEYWORDS if kw in text_lower]
        if len(legal_keyword_matches) >= 1:
            return True, f"contains_legal_keywords ({len(legal_keyword_matches)} keywords)"
        legal_context_indicators = [
            'i want to', 'i need to', 'how to', 'what to do', 'help me with',
            'i have a problem', 'i am facing', 'is it possible', 'can i'
        ]
        for indicator in legal_context_indicators:
            if indicator in text_lower and len(text) > 20:
                return True, "legal_context_indicator"
        return False, "no_legal_context"

    @classmethod
    def get_non_legal_response(cls, query: str, classification_reason: str) -> dict:
        responses = {
            "greeting_or_introduction": {
                "response": "👋 Hello! I'm NyayaAI, your legal intelligence assistant. I specialize in analyzing legal scenarios under the Bharatiya Nyaya Sanhita (BNS) 2023 and other Indian laws.\n\nPlease describe your legal situation or problem. For example:\n• 'I lost my driving license, how do I get a duplicate?'\n• 'Someone forged my signature on a property document'\n• 'My employer hasn't paid my salary for 3 months'",
                "type": "greeting"
            },
            "non_legal_conversation": {
                "response": "I'm NyayaAI, a legal analysis AI. I'm designed to help with legal issues and problems.\n\nI notice your query isn't about a legal issue. Could you please describe a legal situation you need help with?",
                "type": "clarification"
            },
            "no_legal_context": {
                "response": "I'm a legal analysis assistant. I can help with legal issues like:\n\n• Lost documents\n• Criminal matters\n• Property disputes\n• Consumer complaints\n• Family law issues\n\nPlease describe your specific legal problem or situation.",
                "type": "guidance"
            }
        }
        response_data = responses.get(classification_reason, responses["no_legal_context"])
        return {
            "is_legal_query": False,
            "classification_reason": classification_reason,
            "message": response_data["response"],
            "type": response_data["type"],
            "applicable_laws": [],
            "consequences": [{"type": "None", "description": "This is not a legal query.", "severity": "None", "penalty": "Not applicable"}],
            "recommendations": [{"action": "Describe your legal situation", "priority": "Immediate", "description": "Please provide details about your legal problem."}],
            "severity": "Low",
            "summary": response_data["response"],
            "disclaimer": "I'm here to help with legal issues. Please describe your specific legal problem."
        }


class IndianLaw2023:
    BNS  = "Bharatiya Nyaya Sanhita, 2023"
    BNSS = "Bharatiya Nagarik Suraksha Sanhita, 2023"
    BSA  = "Bharatiya Sakshya Adhiniyam, 2023"

    @classmethod
    def is_relevant_law(cls, scenario: str) -> bool:
        scenario_lower = scenario.lower()
        legal_indicators = ['fir', 'police', 'case', 'court', 'legal', 'offense',
                            'crime', 'criminal', 'sue', 'complaint', 'violation',
                            'law', 'right', 'license', 'licence', 'document', 'lost',
                            'forget', 'forgot', 'problem', 'issue', 'money', 'cash',
                            'caught', 'detained', 'arrested']
        return any(indicator in scenario_lower for indicator in legal_indicators)


if ENABLE_CACHE:
    response_cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)
else:
    response_cache = None


class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = {}

    def can_proceed(self, client_id: str = "default") -> bool:
        now = time.time()
        window_start = now - 60
        if client_id not in self.requests:
            self.requests[client_id] = []
        self.requests[client_id] = [t for t in self.requests[client_id] if t > window_start]
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        self.requests[client_id].append(now)
        return True


rate_limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)

PII_PATTERNS = [
    (re.compile(r'\b\d{10}\b'), '[PHONE_NUMBER]'),
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
    (re.compile(r'\b\d{12}\b'), '[AADHAAR]'),
    (re.compile(r'\b\d{16}\b'), '[CREDIT_CARD]'),
    (re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'), '[PAN]'),
]
PROFANITY_WORDS = ['fuck', 'shit', 'asshole', 'bitch', 'cunt', 'bastard', 'damn', 'piss']

VALID_JURISDICTIONS = ["India", "United States", "United Kingdom", "Australia", "Canada", "European Union", "Singapore", "UAE"]
INDIAN_STATES = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Gujarat", "West Bengal", "Rajasthan", "Kerala", "Telangana"]


class ScenarioRequest(BaseModel):
    scenario: str
    jurisdiction: str = DEFAULT_JURISDICTION
    state: Optional[str] = None
    api_key: str = ""
    conversation_history: Optional[List[Dict[str, str]]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "scenario": "I forgot my driving license somewhere, what should I do?",
                "jurisdiction": "India",
                "state": "Maharashtra",
                "api_key": "",
                "conversation_history": []
            }
        }
        extra = "ignore"

    @field_validator("scenario")
    @classmethod
    def scenario_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Scenario cannot be empty.")
        if len(v) > MAX_SCENARIO_LENGTH:
            raise ValueError(f"Scenario exceeds the {MAX_SCENARIO_LENGTH}-character limit.")
        if REDACT_PII:
            for pattern, replacement in PII_PATTERNS:
                v = pattern.sub(replacement, v)
        if FILTER_PROFANITY:
            for word in PROFANITY_WORDS:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                v = pattern.sub('***', v)
        return v

    @field_validator("jurisdiction")
    @classmethod
    def jurisdiction_valid(cls, v: str) -> str:
        if v not in VALID_JURISDICTIONS:
            raise ValueError(f"Unsupported jurisdiction '{v}'. Choose from: {', '.join(VALID_JURISDICTIONS)}")
        return v

    @field_validator("state")
    @classmethod
    def state_valid(cls, v: Optional[str], info) -> Optional[str]:
        if v and info.data.get("jurisdiction") == "India":
            if v not in INDIAN_STATES:
                log.warning(f"State '{v}' not in supported list, but allowing")
                return v
        return v


LEGAL_SYSTEM_PROMPT = """You are NyayaAI, an expert legal analyst specializing in the NEW 2023 Indian criminal laws.

IMPORTANT INSTRUCTIONS:
1. For queries about lost documents, forgotten items, or legal procedures, provide relevant legal information.
2. Always assume the user is seeking legal guidance unless clearly indicated otherwise.
3. For ambiguous queries, ask clarifying questions politely.
4. Provide specific, actionable legal guidance when possible.

For LEGAL scenarios, use the NEW 2023 laws:
- Bharatiya Nyaya Sanhita (BNS), 2023 - REPLACES IPC
- Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 - REPLACES CrPC
- Bharatiya Sakshya Adhiniyam (BSA), 2023 - REPLACES Evidence Act

Response Format - Return JSON with this structure:
{
  "applicable_laws": [{"name": "...", "section": "...", "description": "...", "jurisdiction": "..."}],
  "consequences": [{"type": "...", "description": "...", "severity": "...", "penalty": "..."}],
  "recommendations": [{"action": "...", "priority": "...", "description": "..."}],
  "severity": "Low | Medium | High | Critical",
  "summary": "Clear, helpful answer to the user's query",
  "disclaimer": "This is legal information, not legal advice."
}"""


def resolve_api_key(user_key: str) -> str:
    if MISTRAL_API_KEY:
        if ALLOW_USER_API_KEY and user_key.strip():
            log.info("Using user-supplied API key")
            return user_key.strip()
        return MISTRAL_API_KEY
    if not user_key.strip():
        raise HTTPException(status_code=400, detail="No API key configured.")
    return user_key.strip()


def clean_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) >= 2 else text
        if text.lower().startswith("json"):
            text = text[4:]
    if text.endswith("```"):
        text = text[:-3]
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    return text.strip()


@retry(retry=retry_if_exception_type((json.JSONDecodeError, ConnectionError, TimeoutError)),
       stop=stop_after_attempt(MAX_RETRIES),
       wait=wait_exponential(multiplier=1, min=2, max=10),
       before_sleep=before_sleep_log(log, logging.WARNING))
async def call_mistral(api_key: str, user_message: str) -> dict:
    client = Mistral(api_key=api_key)
    response = await asyncio.to_thread(
        client.chat.complete,
        model=MISTRAL_MODEL,
        messages=[
            {"role": "system", "content": LEGAL_SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    raw = response.choices[0].message.content or ""
    try:
        return json.loads(clean_json(raw))
    except json.JSONDecodeError as e:
        log.warning(f"JSON parse failed: {e}")
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw)
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {
            "applicable_laws": [],
            "consequences": [],
            "recommendations": [{"action": "Get legal assistance", "priority": "Immediate", "description": "Please provide more details."}],
            "severity": "Low",
            "summary": "I understand you have a legal concern. Could you provide more details?",
            "disclaimer": "This is an automated response. For specific legal advice, please consult a lawyer."
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("NyayaAI Analysis App starting...")
    yield
    log.info("NyayaAI Analysis App shutting down.")


analysis_app = FastAPI(
    title="NyayaAI — Legal Analysis",
    description="AI-powered legal scenario analysis (BNS/BNSS/BSA 2023)",
    version="2.1.0",
    lifespan=lifespan,
)

analysis_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@analysis_app.get("/")
async def analysis_root():
    return {
        "service": "NyayaAI Legal Analysis",
        "version": "2.1.0",
        "features": ["Query Classification (150+ legal keywords)", "BNS 2023 Framework", "Follow-up Support"],
        "status": "operational",
        "documentation": "/analysis/docs"
    }


@analysis_app.post("/analyze", response_model=dict, summary="Analyze a legal scenario", tags=["Analysis"])
async def analyze_scenario(
    request: ScenarioRequest,
    background_tasks: BackgroundTasks,
    client_id: Optional[str] = None
):
    client_identifier = client_id or (request.api_key[:8] if request.api_key else "anonymous")
    if not rate_limiter.can_proceed(client_identifier):
        raise HTTPException(status_code=429, detail=f"Rate limit: {RATE_LIMIT_PER_MINUTE} requests/minute")

    is_legal, reason = QueryClassifier.is_legal_scenario(request.scenario)
    log.info(f"Query classified: is_legal={is_legal}, reason={reason}")

    if not is_legal:
        return QueryClassifier.get_non_legal_response(request.scenario, reason)

    api_key = resolve_api_key(request.api_key)

    user_message = f"""Jurisdiction: {request.jurisdiction}
{'State: ' + request.state if request.state else ''}
User Query: {request.scenario}"""

    if request.conversation_history and len(request.conversation_history) > 0:
        user_message += "\n\nPrevious conversation:\n"
        for msg in request.conversation_history[-6:]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            role_label = "USER" if role.lower() in ["user", "human"] else "ASSISTANT"
            user_message += f"{role_label}: {content}\n"
        user_message += "\nPlease answer based on the above conversation context."

    start = time.perf_counter()
    log.info(f"Analyzing query | jurisdiction={request.jurisdiction} | length={len(request.scenario)}")

    try:
        result = await call_mistral(api_key, user_message)
        elapsed = time.perf_counter() - start
        log.info(f"Analysis complete | {elapsed:.1f}s | severity={result.get('severity', '?')}")
        result["is_legal_query"] = True
        result["classification_reason"] = reason
        return result
    except json.JSONDecodeError as e:
        log.error(f"JSON parse error: {e}")
        return {
            "applicable_laws": [], "consequences": [],
            "recommendations": [{"action": "Provide more details", "priority": "Immediate", "description": "Could you provide more information?"}],
            "severity": "Low",
            "summary": "I understand you have a legal question. Could you please provide more details?",
            "disclaimer": "This is an automated response.",
            "is_legal_query": True
        }
    except Exception as e:
        log.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@analysis_app.get("/health", summary="Health check", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "NyayaAI Analysis",
        "version": "2.1.0",
        "features": {"query_classification": "enabled (150+ keywords)", "anti_hallucination": "active", "legal_framework": "BNS/BNSS/BSA 2023", "follow_up_support": "enabled"},
        "cache_enabled": ENABLE_CACHE,
        "rate_limit": RATE_LIMIT_PER_MINUTE
    }


@analysis_app.get("/config", summary="Configuration", tags=["System"])
async def get_config():
    return {
        "default_jurisdiction": DEFAULT_JURISDICTION,
        "max_scenario_length": MAX_SCENARIO_LENGTH,
        "valid_jurisdictions": VALID_JURISDICTIONS,
        "query_classification": True,
        "keywords_count": 150,
        "follow_up_support": True,
        "features": {"caching": ENABLE_CACHE, "rate_limiting": RATE_LIMIT_PER_MINUTE, "pii_redaction": REDACT_PII, "profanity_filter": FILTER_PROFANITY},
        "server_key_configured": bool(MISTRAL_API_KEY),
        "allow_user_api_key": ALLOW_USER_API_KEY
    }
    
app1 = FastAPI(title="App One")

@app1.get("/")
async def root():
    return {"message": "Hello from App One"}

@app1.get("/info")
async def info():
    return {"app": "App One", "status": "running"}