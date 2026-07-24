import re
from dataclasses import dataclass
from typing import Optional


class Intent:
    GREETING             = "GREETING"
    GOODBYE              = "GOODBYE"
    CONTACT_INFO         = "CONTACT_INFO"
    FAQ_ROI              = "FAQ_ROI"
    FAQ_LOCAL_AGENCY     = "FAQ_LOCAL_AGENCY"
    FAQ_GENERAL          = "FAQ_GENERAL"
    CERTIFICATIONS       = "CERTIFICATIONS"
    CLIENTS_PORTFOLIO    = "CLIENTS_PORTFOLIO"
    AWARDS               = "AWARDS"
    ABOUT_COMPANY        = "ABOUT_COMPANY"
    SERVICE_SEO_BRANDING = "SERVICE_SEO_BRANDING"
    SERVICE_CONTENT      = "SERVICE_CONTENT"
    SERVICE_LEAD_GEN     = "SERVICE_LEAD_GEN"
    SERVICE_ECOMMERCE    = "SERVICE_ECOMMERCE"
    SERVICE_ORM          = "SERVICE_ORM"
    SERVICE_CELEBRITY    = "SERVICE_CELEBRITY"
    SERVICE_POLITICAL    = "SERVICE_POLITICAL"
    SERVICES_GENERAL     = "SERVICES_GENERAL"
    INDUSTRY_HEALTHCARE  = "INDUSTRY_HEALTHCARE"
    INDUSTRY_REAL_ESTATE = "INDUSTRY_REAL_ESTATE"
    INDUSTRY_EDUCATION   = "INDUSTRY_EDUCATION"
    INDUSTRY_HOSPITALITY = "INDUSTRY_HOSPITALITY"
    INDUSTRY_JEWELLERY   = "INDUSTRY_JEWELLERY"
    INDUSTRY_MANUFACT    = "INDUSTRY_MANUFACTURING"
    UNKNOWN              = "UNKNOWN"


@dataclass
class DetectedIntent:
    name:       str
    confidence: str            # "high" | "medium" | "low"
    matched_on: Optional[str]  # keyword that triggered the match


# ── Intent keyword map — checked in strict priority order ─────────────
# Format: (intent_name, [keywords], confidence)
_INTENT_MAP: list[tuple[str, list[str], str]] = [

    (Intent.GREETING, [
        "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
        "namaste", "howdy", "greetings", "what can you do", "what can you help",
        "how can you help me", "start"
    ], "high"),

    (Intent.GOODBYE, [
        "bye", "goodbye", "good bye", "see you", "see ya",
        "that's all", "thats all", "i'm done", "im done",
        "no more questions", "nothing else", "thanks", "thank you",
        "thank u", "cheers", "take care"
    ], "high"),

    (Intent.CONTACT_INFO, [
        "contact", "email", "phone", "call", "address", "office",
        "location", "reach", "get in touch", "reach out",
        "how to contact", "where are you", "your number", "whatsapp"
    ], "high"),

    (Intent.FAQ_ROI, [
        "roi", "return on investment", "measure results", "how do you measure",
        "track performance", "how will i know", "metrics", "kpi",
        "performance report", "results tracking"
    ], "high"),

    (Intent.FAQ_LOCAL_AGENCY, [
        "why local", "why choose you", "why crushaders", "why not national",
        "local agency vs", "what makes you different", "why should i choose",
        "what makes you special", "advantage of local"
    ], "high"),

    (Intent.FAQ_GENERAL, [
        "faq", "frequently asked", "how do you work",
        "what is your process", "how long does it take", "what is aeo"
    ], "medium"),

    (Intent.CERTIFICATIONS, [
        "certified", "certification", "google partner", "meta partner",
        "amazon partner", "partner status", "accredited", "badge", "qualified"
    ], "high"),

    (Intent.CLIENTS_PORTFOLIO, [
        "clients", "portfolio", "case study", "case studies",
        "who have you worked", "past work", "previous clients",
        "examples of your work", "client list", "who are your clients"
    ], "high"),

    (Intent.AWARDS, [
        "award", "awards", "recognition", "nasscom", "startup odisha",
        "brand leadership", "accolade", "achievement", "won any"
    ], "high"),

    (Intent.ABOUT_COMPANY, [
        "about", "who are you", "who is crushaders", "about crushaders",
        "tell me about", "company history", "founded", "when did you start",
        "how old", "how many clients", "how many countries", "team size",
        "how many employees", "years of experience", "company overview"
    ], "high"),

    (Intent.SERVICE_SEO_BRANDING, [
        "seo", "aeo", "search engine optimisation", "search engine optimization",
        "answer engine", "google ranking", "organic traffic", "branding",
        "brand identity", "digital branding", "search ranking",
        "keyword ranking", "rank on google", "improve ranking"
    ], "high"),

    (Intent.SERVICE_CONTENT, [
        "content creation", "blog", "blog writing", "social media content",
        "video production", "infographic", "content marketing",
        "copywriting", "write content", "articles"
    ], "high"),

    (Intent.SERVICE_LEAD_GEN, [
        "lead generation", "lead gen", "more leads", "get leads",
        "paid ads", "google ads", "meta ads", "facebook ads",
        "amazon ads", "ppc", "digital advertising", "customer acquisition"
    ], "high"),

    (Intent.SERVICE_ECOMMERCE, [
        "ecommerce", "e-commerce", "online store", "online shop",
        "shopify", "woocommerce", "sell online", "online selling",
        "product listing", "digital storefront"
    ], "high"),

    (Intent.SERVICE_ORM, [
        "orm", "online reputation", "reputation management",
        "negative review", "bad review", "remove review",
        "brand reputation", "brand protection", "pr crisis"
    ], "high"),

    (Intent.SERVICE_CELEBRITY, [
        "celebrity", "celebrity management", "public figure",
        "celebrity profile", "influencer management", "personal brand management"
    ], "high"),

    (Intent.SERVICE_POLITICAL, [
        "political", "election", "campaign", "political campaign",
        "voter", "candidate", "electoral"
    ], "high"),

    (Intent.SERVICES_GENERAL, [
        "services", "what do you offer", "what do you provide",
        "what can you help with", "your offerings", "capabilities",
        "solutions", "what do you do", "help my business"
    ], "medium"),

    (Intent.INDUSTRY_HEALTHCARE, [
        "healthcare", "hospital", "clinic", "medical", "doctor",
        "pharma", "health sector", "patient", "dentist"
    ], "high"),

    (Intent.INDUSTRY_REAL_ESTATE, [
        "real estate", "property", "builder", "developer", "construction",
        "housing", "apartments", "plots"
    ], "high"),

    (Intent.INDUSTRY_EDUCATION, [
        "education", "school", "college", "university", "institute",
        "coaching", "edtech", "ed-tech", "admissions", "students"
    ], "high"),

    (Intent.INDUSTRY_HOSPITALITY, [
        "hospitality", "hotel", "resort", "tourism", "travel",
        "restaurant", "food business"
    ], "high"),

    (Intent.INDUSTRY_JEWELLERY, [
        "jewellery", "jewelry", "jewels", "watches", "gems",
        "gold", "diamond", "ornaments"
    ], "high"),

    (Intent.INDUSTRY_MANUFACT, [
        "manufacturing", "factory", "industrial", "production",
        "manufacturer", "b2b manufacturing"
    ], "high"),
]


def _normalise(text: str) -> str:
    """Lowercase and strip punctuation for consistent matching."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def detect_intent(message: str) -> DetectedIntent:
    """
    Detect intent via keyword matching in strict priority order.

    Phase 2 upgrade path:
      Replace this function body with a semantic search call.
      Return type (DetectedIntent) stays the same — chat_service
      needs zero changes.
    """
    normalised = _normalise(message)

    for intent_name, keywords, confidence in _INTENT_MAP:
        for keyword in keywords:
            if keyword in normalised:
                return DetectedIntent(
                    name=intent_name,
                    confidence=confidence,
                    matched_on=keyword
                )

    return DetectedIntent(name=Intent.UNKNOWN, confidence="low", matched_on=None)