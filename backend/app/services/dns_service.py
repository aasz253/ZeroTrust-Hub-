import socket
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.dns_security import MaliciousDomain, DNSQuery, DNSBlockerRule

logger = logging.getLogger(__name__)

KNOWN_MALICIOUS = [
    "malware-domain.com", "evil.com", "botnet-c2.example.com",
    "phishing-bank.com", "ransomware-c2.net", "trojan-dropper.org",
    "malicious.com", "badhost.net", "c2-server.io", "phishing.xyz",
]

THREAT_CATEGORIES = {
    "phishing": ["phish", "login", "verify", "bank", "paypal", "secure-"],
    "malware": ["malware", "virus", "trojan", "ransom", "exploit", "dropper"],
    "c2": ["c2", "botnet", "command", "panel", "gate"],
    "spam": ["spam", "dbl", "uribl", "spamhaus"],
    "tracking": ["tracker", "analytics", "pixel", "adserver", "doubleclick"],
}


def resolve_domain(domain: str) -> Optional[str]:
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None
    except Exception:
        return None


def is_malicious_domain(domain: str, db: Session = None) -> dict:
    result = {"is_malicious": False, "threat_type": None, "source": None, "confidence": 0}

    domain_lower = domain.lower()

    if db:
        match = db.query(MaliciousDomain).filter(
            MaliciousDomain.domain == domain_lower,
            MaliciousDomain.is_active == True,
        ).first()
        if match:
            return {
                "is_malicious": True,
                "threat_type": match.threat_type,
                "source": match.source,
                "confidence": match.confidence or 1.0,
            }

        rules = db.query(DNSBlockerRule).filter(
            DNSBlockerRule.is_active == True
        ).all()
        for rule in rules:
            if rule.pattern_type == "exact" and rule.domain.lower() == domain_lower:
                return {
                    "is_malicious": True,
                    "threat_type": rule.category or "blocked",
                    "source": "blocklist",
                    "confidence": 1.0,
                }
            if rule.pattern_type == "suffix" and domain_lower.endswith(rule.domain.lower()):
                return {
                    "is_malicious": True,
                    "threat_type": rule.category or "blocked",
                    "source": "blocklist",
                    "confidence": 0.9,
                }
            if rule.pattern_type == "contains" and rule.domain.lower() in domain_lower:
                return {
                    "is_malicious": True,
                    "threat_type": rule.category or "blocked",
                    "source": "blocklist",
                    "confidence": 0.8,
                }

    if domain_lower in KNOWN_MALICIOUS:
        return {"is_malicious": True, "threat_type": "known_malicious", "source": "builtin", "confidence": 1.0}

    parts = domain_lower.split(".")
    if len(parts) >= 2:
        sld = parts[-2] if len(parts) >= 2 else ""
        for category, keywords in THREAT_CATEGORIES.items():
            for kw in keywords:
                if kw in sld or kw in domain_lower:
                    return {
                        "is_malicious": True,
                        "threat_type": category,
                        "source": "heuristic",
                        "confidence": 0.5,
                    }

    return result


def analyze_query(domain: str, source_ip: str = None, query_type: str = "A",
                  db: Session = None) -> dict:
    malicious_result = is_malicious_domain(domain, db) if db else is_malicious_domain(domain)
    response_ip = resolve_domain(domain)

    if db:
        query = DNSQuery(
            source_ip=source_ip,
            domain=domain.lower(),
            query_type=query_type,
            response_ip=response_ip,
            is_malicious=malicious_result["is_malicious"],
            is_blocked=malicious_result["is_malicious"],
            threat_match=malicious_result.get("threat_type"),
        )
        db.add(query)
        db.commit()

    return {
        "domain": domain,
        "resolved_ip": response_ip,
        "malicious": malicious_result["is_malicious"],
        "threat_type": malicious_result.get("threat_type"),
        "confidence": malicious_result.get("confidence", 0),
        "should_block": malicious_result["is_malicious"],
    }


def add_malicious_domain(domain: str, threat_type: str = "manual", confidence: float = 1.0,
                         source: str = "manual", db: Session = None) -> dict:
    existing = db.query(MaliciousDomain).filter(MaliciousDomain.domain == domain).first()
    if existing:
        return {"success": True, "message": "Domain already in database", "id": existing.id}

    entry = MaliciousDomain(
        domain=domain.lower(),
        threat_type=threat_type,
        severity="HIGH" if confidence >= 0.8 else "MEDIUM",
        source=source,
        confidence=confidence,
        is_active=True,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"success": True, "message": "Domain added", "id": entry.id}


def log_query(domain: str, source_ip: str = None, query_type: str = "A",
              response_ip: str = None, is_blocked: bool = False, db: Session = None):
    if not db:
        return
    malicious = is_malicious_domain(domain, db)
    query = DNSQuery(
        source_ip=source_ip,
        domain=domain.lower(),
        query_type=query_type,
        response_ip=response_ip,
        is_malicious=malicious["is_malicious"],
        is_blocked=is_blocked,
        threat_match=malicious.get("threat_type"),
    )
    db.add(query)
    db.commit()
