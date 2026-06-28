import re
import time
import hashlib
from typing import Optional
from collections import defaultdict
from app.core.config import settings

BLOCKED_USER_AGENTS = [
    "curl", "wget", "python-requests", "python-httpx", "python-urllib",
    "go-http-client", "java/", "libwww", "perl", "ruby", "scrapy",
    "zgrab", "masscan", "nmap", "sqlmap", "nikto", "dirbuster",
    "gobuster", "wfuzz", "hydra", "medusa", "thc", "openssl",
    "fetch", "lwp", "httpclient", "okhttp", "apache-http",
]

BLOCKED_EXTENSIONS = [
    ".env", ".git", ".svn", ".htaccess", ".htpasswd",
    ".bak", ".old", ".swp", ".sql", ".dump",
    "wp-config", "phpinfo", "shell", "cmd",
]

BLOCKED_PATHS = [
    "/wp-admin", "/wp-content", "/wp-includes",
    "/administrator", "/phpmyadmin", "/phpPgAdmin",
    "/mysql", "/sql", "/backup", "/dump",
    "/.env", "/.git/config", "/vendor/",
    "/server-status", "/cgi-bin/",
]

SQL_INJECTION_PATTERNS = [
    r"(\bOR\b|\bAND\b).*[=].*[=]",
    r"(\bUNION\b.*\bSELECT\b)",
    r"(\bDROP\b.*\bTABLE\b)",
    r"(\bDELETE\b.*\bFROM\b)",
    r"(\bUPDATE\b.*\bSET\b)",
    r"(\bINSERT\b.*\bINTO\b)",
    r"(\bEXEC\b|\bEXECUTE\b)",
    r"(\bXP_\b|\bsp_\b)",
    r"(\bLOAD_FILE\b|\bINTO\b.*\bOUTFILE\b)",
    r"(\bCHAR\b|\bCONVERT\b).*\(.*\).*\bSELECT\b",
    r"'.*\bOR\b.*'",
    r".*'.*=.*'",
]

XSS_PATTERNS = [
    r"<script[^>]*>",
    r"javascript\s*:",
    r"onerror\s*=",
    r"onload\s*=",
    r"onclick\s*=",
    r"onmouseover\s*=",
    r"<iframe[^>]*>",
    r"<embed[^>]*>",
    r"<object[^>]*>",
    r"alert\s*\(",
    r"prompt\s*\(",
    r"confirm\s*\(",
    r"document\s*\.\s*cookie",
    r"document\s*\.\s*location",
    r"<[^>]*style\s*=\s*['\"][^'\"]*expression",
]

FAILED_LOGINS: dict[str, list[float]] = defaultdict(list)
LOGIN_ATTEMPTS: dict[str, int] = defaultdict(int)
LOCKED_IPS: dict[str, float] = {}

BOT_HITS: dict[str, list[float]] = defaultdict(list)


def is_bot_user_agent(ua: str) -> bool:
    ua_lower = ua.lower().strip()
    if not ua_lower:
        return True
    if ua_lower.startswith("python") or ua_lower.startswith("go-http"):
        return True
    for pattern in BLOCKED_USER_AGENTS:
        if pattern in ua_lower:
            return True
    return False


def is_blocked_path(path: str) -> bool:
    path_lower = path.lower()
    for bp in BLOCKED_PATHS:
        if bp in path_lower:
            return True
    for ext in BLOCKED_EXTENSIONS:
        if ext in path_lower:
            return True
    return False


def has_sql_injection(value: str) -> bool:
    if not isinstance(value, str):
        return False
    upper = value.upper()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, upper):
            return True
    return False


def has_xss(value: str) -> bool:
    if not isinstance(value, str):
        return False
    for pattern in XSS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False


def sanitize_input(value: str) -> str:
    if not isinstance(value, str):
        return value
    value = re.sub(r"<[^>]*>", "", value)
    value = value.replace("javascript:", "").replace("JAVASCRIPT:", "")
    value = value.replace("onerror=", "").replace("onload=", "").replace("onclick=", "")
    return value[:2000]


def check_brute_force(ip: str, email: str) -> Optional[str]:
    now = time.time()
    LOCKED_IPS.clear()

    if ip in LOCKED_IPS and now - LOCKED_IPS[ip] < 900:
        remaining = int(900 - (now - LOCKED_IPS[ip]))
        return f"IP blocked for {remaining}s (too many attempts)"

    FAILED_LOGINS[ip] = [t for t in FAILED_LOGINS[ip] if now - t < 900]
    if len(FAILED_LOGINS[ip]) >= 5:
        LOCKED_IPS[ip] = now
        return "Too many login attempts. IP blocked for 15 minutes."

    key = f"{ip}:{email}"
    LOGIN_ATTEMPTS[key] = LOGIN_ATTEMPTS.get(key, 0) + 1
    if LOGIN_ATTEMPTS[key] >= 5:
        LOCKED_IPS[ip] = now
        return "Too many login attempts for this account. IP blocked for 15 minutes."

    return None


def record_failed_login(ip: str, email: str):
    FAILED_LOGINS[ip].append(time.time())
    key = f"{ip}:{email}"
    LOGIN_ATTEMPTS[key] = LOGIN_ATTEMPTS.get(key, 0) + 1


def is_rate_limited(
    key: str,
    max_requests: int,
    window: float = 60.0,
) -> bool:
    now = time.time()
    store = BOT_HITS
    store[key] = [t for t in store.get(key, []) if now - t < window]
    if len(store.get(key, [])) >= max_requests:
        return True
    store[key].append(now)
    return False


def get_client_ip(request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
