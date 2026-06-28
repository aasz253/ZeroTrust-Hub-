import json
import urllib.request
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.geoip import GeoIPRule, GeoIPCache, GeoIPHit

logger = logging.getLogger(__name__)

IPAPI_URL = "http://ip-api.com/json/{ip}"


def _lookup_ipapi(ip: str) -> Optional[dict]:
    try:
        url = IPAPI_URL.format(ip=ip)
        req = urllib.request.Request(url, headers={"User-Agent": "ZeroTrust-Hub/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "success":
                return {
                    "country_code": data.get("countryCode", ""),
                    "country_name": data.get("country", ""),
                    "city": data.get("city", ""),
                    "isp": data.get("isp", ""),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                }
    except Exception as e:
        logger.debug(f"GeoIP lookup failed for {ip}: {e}")
    return None


def get_ip_info(ip: str, db: Session) -> dict:
    cache = db.query(GeoIPCache).filter(GeoIPCache.ip_address == ip).first()
    if cache and cache.expires_at and cache.expires_at > datetime.now(timezone.utc):
        return {
            "country_code": cache.country_code,
            "country_name": cache.country_name,
            "city": cache.city,
            "isp": cache.isp,
            "latitude": cache.latitude,
            "longitude": cache.longitude,
            "is_blocked": cache.is_blocked,
            "cached": True,
        }

    info = _lookup_ipapi(ip)
    if not info:
        return {"country_code": None, "country_name": "Unknown", "cached": False}

    rules = db.query(GeoIPRule).filter(
        GeoIPRule.country_code == info["country_code"],
        GeoIPRule.is_active == True,
    ).all()
    is_blocked = any(r.action == "block" for r in rules)

    if cache:
        cache.country_code = info["country_code"]
        cache.country_name = info["country_name"]
        cache.city = info.get("city")
        cache.isp = info.get("isp")
        cache.latitude = info.get("lat")
        cache.longitude = info.get("lon")
        cache.is_blocked = is_blocked
        cache.expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    else:
        cache = GeoIPCache(
            ip_address=ip,
            country_code=info["country_code"],
            country_name=info["country_name"],
            city=info.get("city"),
            isp=info.get("isp"),
            latitude=info.get("lat"),
            longitude=info.get("lon"),
            is_blocked=is_blocked,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(cache)
    db.commit()

    return {
        "country_code": info["country_code"],
        "country_name": info["country_name"],
        "city": info.get("city"),
        "isp": info.get("isp"),
        "latitude": info.get("lat"),
        "longitude": info.get("lon"),
        "is_blocked": is_blocked,
        "cached": False,
    }


def log_hit(ip: str, country_code: str, country_name: str, action: str,
            path: str = None, user_agent: str = None, db: Session = None):
    if not db:
        return
    hit = GeoIPHit(
        ip_address=ip,
        country_code=country_code,
        country_name=country_name,
        action=action,
        path=path,
        user_agent=user_agent,
    )
    db.add(hit)
    rule = db.query(GeoIPRule).filter(
        GeoIPRule.country_code == country_code, GeoIPRule.is_active == True
    ).first()
    if rule:
        rule.hit_count = (rule.hit_count or 0) + 1
    db.commit()


def check_ip(ip: str, path: str = None, user_agent: str = None, db: Session = None) -> dict:
    info = get_ip_info(ip, db) if db else _lookup_ipapi(ip) or {}
    country_code = info.get("country_code")
    country_name = info.get("country_name", "Unknown")

    if db and country_code:
        rules = db.query(GeoIPRule).filter(
            GeoIPRule.country_code == country_code,
            GeoIPRule.is_active == True,
        ).all()
        for rule in rules:
            if rule.action == "block":
                log_hit(ip, country_code, country_name, "blocked", path, user_agent, db)
                return {
                    "blocked": True,
                    "reason": f"Traffic from {country_name} ({country_code}) is blocked",
                    "country_code": country_code,
                    "country_name": country_name,
                }

    return {
        "blocked": False,
        "country_code": country_code,
        "country_name": country_name,
    }
