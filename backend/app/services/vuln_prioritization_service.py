import json
import urllib.request
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.vuln_prioritization import VulnPriority

logger = logging.getLogger(__name__)

EPSS_API = "https://api.first.org/data/v1/epss?cve={cve}"
CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def _fetch_json(url: str, timeout: int = 10) -> Optional[dict]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ZeroTrust-Hub/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        logger.debug(f"API fetch failed: {url[:80]} - {e}")
        return None


def fetch_epss(cve_id: str) -> dict:
    url = EPSS_API.format(cve=cve_id)
    data = _fetch_json(url)
    if data and "data" in data and len(data["data"]) > 0:
        entry = data["data"][0]
        return {
            "epss_score": float(entry.get("epss", 0)),
            "epss_percentile": float(entry.get("percentile", 0)),
        }
    return {"epss_score": 0.0, "epss_percentile": 0.0}


def fetch_cisa_kev() -> list[dict]:
    data = _fetch_json(CISA_KEV_URL)
    if data and "vulnerabilities" in data:
        return data["vulnerabilities"]
    return []


def build_cisa_kev_index() -> dict:
    cisa_index = {}
    items = fetch_cisa_kev()
    for item in items:
        cve = item.get("cveID", "").upper()
        if cve:
            cisa_index[cve] = {
                "date_added": item.get("dateAdded"),
                "known_ransomware": item.get("knownRansomwareCampaignUse") == "Known",
                "short_description": item.get("shortDescription"),
                "required_action": item.get("requiredAction"),
                "due_date": item.get("dueDate"),
            }
    return cisa_index


def _calculate_priority(vuln) -> str:
    score = vuln.combined_score or 0
    if score >= 8.0 or vuln.is_cisa_kev:
        return "CRITICAL"
    elif score >= 5.0:
        return "HIGH"
    elif score >= 3.0:
        return "MEDIUM"
    return "LOW"


def _calculate_combined(cvss: float, epss: float, is_kev: bool) -> float:
    base = cvss * 0.4 + (epss * 10) * 0.3
    if is_kev:
        base += 2.0
    return min(10.0, base)


def prioritize_cve(cve_id: str, cvss_score: float = 0.0, affected_vendor: str = "",
                   affected_product: str = "", description: str = "",
                   is_kev: bool = False, db: Session = None) -> dict:
    cvss = max(0.0, min(10.0, cvss_score))
    epss_data = fetch_epss(cve_id)
    epss_score = epss_data.get("epss_score", 0.0)
    epss_percentile = epss_data.get("epss_percentile", 0.0)

    combined = _calculate_combined(cvss, epss_score, is_kev)
    priority_tier = _calculate_priority(
        type("obj", (object,), {"combined_score": combined, "is_cisa_kev": is_kev})()
    )

    result = {
        "cve_id": cve_id,
        "cvss_score": cvss,
        "epss_score": epss_score,
        "epss_percentile": epss_percentile,
        "is_cisa_kev": is_kev,
        "combined_score": round(combined, 2),
        "priority_tier": priority_tier,
    }

    if db:
        existing = db.query(VulnPriority).filter(VulnPriority.cve_id == cve_id).first()
        if existing:
            existing.cvss_score = cvss
            existing.epss_score = epss_score
            existing.epss_percentile = epss_percentile
            existing.is_cisa_kev = is_kev
            existing.combined_score = result["combined_score"]
            existing.priority_tier = priority_tier
            existing.affected_vendor = affected_vendor
            existing.affected_product = affected_product
            existing.description = description
            existing.last_updated = datetime.now(timezone.utc)
        else:
            entry = VulnPriority(
                cve_id=cve_id,
                cvss_score=cvss,
                cvss_severity="CRITICAL" if cvss >= 9.0 else "HIGH" if cvss >= 7.0 else "MEDIUM" if cvss >= 4.0 else "LOW",
                epss_score=epss_score,
                epss_percentile=epss_percentile,
                is_cisa_kev=is_kev,
                combined_score=result["combined_score"],
                priority_tier=priority_tier,
                affected_vendor=affected_vendor,
                affected_product=affected_product,
                description=description,
            )
            db.add(entry)
        db.commit()

    return result


def batch_prioritize(db: Session) -> dict:
    from app.models.vulnerability import Vulnerability
    vulns = db.query(Vulnerability).all()
    cisa_kev = build_cisa_kev_index()

    results = []
    for vuln in vulns:
        kev_info = cisa_kev.get(vuln.cve_id.upper(), {})
        is_kev = bool(kev_info)
        result = prioritize_cve(
            cve_id=vuln.cve_id,
            cvss_score=vuln.cvss_score or 0,
            affected_vendor=vuln.affected_vendor or "",
            affected_product="",
            description=vuln.description or "",
            is_kev=is_kev,
            db=db,
        )
        results.append(result)

    return {
        "scored": len(results),
        "critical": sum(1 for r in results if r["priority_tier"] == "CRITICAL"),
        "high": sum(1 for r in results if r["priority_tier"] == "HIGH"),
        "medium": sum(1 for r in results if r["priority_tier"] == "MEDIUM"),
        "low": sum(1 for r in results if r["priority_tier"] == "LOW"),
        "cisa_kev_found": sum(1 for r in results if r["is_cisa_kev"]),
    }
