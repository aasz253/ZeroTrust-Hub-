import ssl
import socket
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.ssl_monitor import SSLCertificate

logger = logging.getLogger(__name__)

COMMON_PORTS = [443, 8443, 465, 993, 995, 2525, 587]

WEAK_CIPHERS = [
    "RC4", "DES", "3DES", "MD5", "SHA1", "EXPORT", "NULL",
    "LOW", "MEDIUM", "aNULL", "eNULL",
]

WEAK_PROTOCOLS = ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"]


def check_certificate(domain: str, port: int = 443) -> dict:
    result = {
        "domain": domain,
        "port": port,
        "error": None,
        "issuer": None,
        "subject": None,
        "serial_number": None,
        "fingerprint_sha256": None,
        "valid_from": None,
        "valid_to": None,
        "days_remaining": 0,
        "is_expired": False,
        "is_expiring_soon": False,
        "is_self_signed": False,
        "is_wildcard": False,
        "weak_cipher": False,
        "protocol_version": None,
        "cipher_suite": None,
        "dns_names": [],
        "ocsp_url": None,
        "revocation_status": None,
        "errors": [],
    }

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_default_verify_paths()

        with socket.create_connection((domain, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                cipher_name = ssock.cipher()
                result["protocol_version"] = ssock.version()
                result["cipher_suite"] = cipher_name[0] if cipher_name else None

                if result["cipher_suite"]:
                    for weak in WEAK_CIPHERS:
                        if weak in result["cipher_suite"].upper():
                            result["weak_cipher"] = True
                            break

                if result["protocol_version"]:
                    for wp in WEAK_PROTOCOLS:
                        if wp in result["protocol_version"]:
                            result["errors"].append(f"Weak protocol: {result['protocol_version']}")
                            result["weak_cipher"] = True
                            break

                for entry in cert.get("subject", []):
                    for key, value in entry:
                        if key == "commonName":
                            result["subject"] = value
                        if key == "organizationName":
                            result["subject"] = f"{result['subject']} ({value})" if result.get("subject") else value

                for entry in cert.get("issuer", []):
                    for key, value in entry:
                        if key == "commonName":
                            result["issuer"] = value

                result["serial_number"] = cert.get("serialNumber")
                result["fingerprint_sha256"] = None

                not_before = cert.get("notBefore")
                not_after = cert.get("notAfter")

                if not_before:
                    result["valid_from"] = _parse_ssl_time(not_before)
                if not_after:
                    result["valid_to"] = _parse_ssl_time(not_after)

                if result["valid_to"]:
                    now = datetime.now(timezone.utc)
                    delta = result["valid_to"] - now
                    result["days_remaining"] = max(0, delta.days)
                    result["is_expired"] = delta.total_seconds() <= 0
                    result["is_expiring_soon"] = 0 < delta.days <= 30

                subj_alt_names = cert.get("subjectAltName", [])
                for _, name in subj_alt_names:
                    result["dns_names"].append(name)
                    if name.startswith("*."):
                        result["is_wildcard"] = True

                if result["subject"] == result["issuer"]:
                    result["is_self_signed"] = True

                ca_issuers = cert.get("caIssuers", [])
                result["ocsp_url"] = ca_issuers[0] if ca_issuers else None

    except ssl.SSLCertVerificationError as e:
        result["errors"].append(f"Certificate verification: {str(e)[:200]}")
    except ssl.SSLError as e:
        result["errors"].append(f"SSL error: {str(e)[:200]}")
    except socket.timeout:
        result["error"] = f"Connection timeout to {domain}:{port}"
    except socket.gaierror:
        result["error"] = f"DNS resolution failed for {domain}"
    except ConnectionRefusedError:
        result["error"] = f"Connection refused on {domain}:{port}"
    except Exception as e:
        result["error"] = str(e)[:200]

    if result["error"]:
        result["status"] = "error"
    elif result["is_expired"]:
        result["status"] = "expired"
    elif result["is_expiring_soon"]:
        result["status"] = "expiring"
    elif result["weak_cipher"]:
        result["status"] = "weak"
    else:
        result["status"] = "valid"

    return result


def _parse_ssl_time(time_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(time_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            return datetime.strptime(time_str, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def scan_domain(domain: str, port: int = None, db: Session = None) -> dict:
    ports_to_check = [port] if port else COMMON_PORTS
    best_result = None

    for p in ports_to_check:
        result = check_certificate(domain, p)
        if result.get("status") != "error":
            best_result = result
            break
        if not best_result:
            best_result = result

    if not best_result:
        best_result = check_certificate(domain, 443)
        best_result = best_result or {"domain": domain, "error": "No response"}

    if db:
        existing = db.query(SSLCertificate).filter(SSLCertificate.domain == domain).first()
        if existing:
            existing.issuer = best_result.get("issuer")
            existing.subject = best_result.get("subject")
            existing.serial_number = best_result.get("serial_number")
            existing.valid_from = best_result.get("valid_from")
            existing.valid_to = best_result.get("valid_to")
            existing.days_remaining = best_result.get("days_remaining", 0)
            existing.is_expired = best_result.get("is_expired", False)
            existing.is_expiring_soon = best_result.get("is_expiring_soon", False)
            existing.is_self_signed = best_result.get("is_self_signed", False)
            existing.is_wildcard = best_result.get("is_wildcard", False)
            existing.weak_cipher = best_result.get("weak_cipher", False)
            existing.protocol_version = best_result.get("protocol_version")
            existing.cipher_suite = best_result.get("cipher_suite")
            existing.dns_names = best_result.get("dns_names", [])
            existing.ocsp_url = best_result.get("ocsp_url")
            existing.errors = best_result.get("errors", [])
            existing.status = best_result.get("status", "unknown")
            existing.last_checked = datetime.now(timezone.utc)
            existing.updated_at = datetime.now(timezone.utc)
        else:
            existing = SSLCertificate(
                domain=domain,
                port=best_result.get("port", 443),
                issuer=best_result.get("issuer"),
                subject=best_result.get("subject"),
                serial_number=best_result.get("serial_number"),
                valid_from=best_result.get("valid_from"),
                valid_to=best_result.get("valid_to"),
                days_remaining=best_result.get("days_remaining", 0),
                is_expired=best_result.get("is_expired", False),
                is_expiring_soon=best_result.get("is_expiring_soon", False),
                is_self_signed=best_result.get("is_self_signed", False),
                is_wildcard=best_result.get("is_wildcard", False),
                weak_cipher=best_result.get("weak_cipher", False),
                protocol_version=best_result.get("protocol_version"),
                cipher_suite=best_result.get("cipher_suite"),
                dns_names=best_result.get("dns_names", []),
                ocsp_url=best_result.get("ocsp_url"),
                errors=best_result.get("errors", []),
                status=best_result.get("status", "unknown"),
                last_checked=datetime.now(timezone.utc),
                next_check=datetime.now(timezone.utc) + timedelta(days=1),
            )
            db.add(existing)
        db.commit()
        db.refresh(existing)

    return best_result
