from fastapi import APIRouter, Depends, UploadFile, File as FileUpload, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.file import File
from app.models.malware import MalwareReport
from app.core.security import get_current_user
from app.core.config import settings
import aiofiles
import os
import hashlib
import uuid
import httpx
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/files", tags=["Files"])


async def vt_hash_lookup(sha256: str) -> dict | None:
    if not settings.VIRUSTOTAL_API_KEY:
        return None
    url = f"https://www.virustotal.com/api/v3/files/{sha256}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers={"x-apikey": settings.VIRUSTOTAL_API_KEY})
            if resp.status_code == 200:
                data = resp.json()
                attrs = data.get("data", {}).get("attributes", {})
                stats = attrs.get("last_analysis_stats", {})
                malicious = stats.get("malicious", 0)
                total = sum(stats.values()) or 1
                return {
                    "detection_ratio": f"{malicious}/{sum(stats.values())}",
                    "malicious": malicious,
                    "total": sum(stats.values()),
                    "risk_score": round((malicious / total) * 10, 1),
                    "threat_family": (attrs.get("popular_threat_classification", {})
                                      .get("suggested_threat_label", None)),
                    "tags": attrs.get("tags", []),
                    "type_description": attrs.get("type_description", ""),
                    "names": attrs.get("names", []),
                    "signatures": attrs.get("signature_info", {}),
                }
    except Exception as e:
        logger.warning(f"VT hash lookup failed: {e}")
    return None


async def vt_upload_file(file_content: bytes, filename: str) -> dict | None:
    if not settings.VIRUSTOTAL_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {"file": (filename, file_content)}
            resp = await client.post(
                "https://www.virustotal.com/api/v3/files",
                headers={"x-apikey": settings.VIRUSTOTAL_API_KEY},
                files=files,
            )
            if resp.status_code == 200:
                data = resp.json()
                analysis_id = data.get("data", {}).get("id", "")
                if analysis_id:
                    import asyncio
                    await asyncio.sleep(5)
                    analysis_resp = await client.get(
                        f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                        headers={"x-apikey": settings.VIRUSTOTAL_API_KEY},
                    )
                    if analysis_resp.status_code == 200:
                        adata = analysis_resp.json()
                        astats = adata.get("data", {}).get("attributes", {}).get("stats", {})
                        malicious = astats.get("malicious", 0)
                        total = sum(astats.values()) or 1
                        return {
                            "detection_ratio": f"{malicious}/{sum(astats.values())}",
                            "malicious": malicious,
                            "total": sum(astats.values()),
                            "risk_score": round((malicious / total) * 10, 1),
                        }
    except Exception as e:
        logger.warning(f"VT upload failed: {e}")
    return None


@router.post("/upload")
async def upload_file(
    file: UploadFile = FileUpload(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

    content = await file.read()
    sha256_hash = hashlib.sha256(content).hexdigest()
    md5_hash = hashlib.md5(content).hexdigest()

    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(upload_dir, stored_name)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    db_file = File(
        user_id=current_user.id,
        original_name=file.filename or "unknown",
        stored_name=stored_name,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type or "application/octet-stream",
        hash_sha256=sha256_hash,
        hash_md5=md5_hash,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    vt_result = await vt_hash_lookup(sha256_hash)
    if not vt_result:
        vt_result = await vt_upload_file(content, file.filename or "file")

    risk_score = vt_result["risk_score"] if vt_result else 0.0
    risk_level = "MALICIOUS" if vt_result and vt_result.get("malicious", 0) > 0 else "CLEAN" if vt_result else "UNKNOWN"
    if vt_result and vt_result.get("malicious", 0) >= 5:
        risk_level = "CRITICAL"
    elif vt_result and vt_result.get("malicious", 0) >= 2:
        risk_level = "SUSPICIOUS"

    malware_report = MalwareReport(
        file_name=file.filename or "unknown",
        file_hash_sha256=sha256_hash,
        file_hash_md5=md5_hash,
        file_size=len(content),
        file_type=file.content_type or "application/octet-stream",
        risk_score=risk_score,
        risk_level=risk_level,
        detection_ratio=vt_result["detection_ratio"] if vt_result else None,
        threat_family=vt_result.get("threat_family") if vt_result else None,
        signatures=vt_result.get("signatures") if vt_result else None,
        indicators=vt_result.get("tags") if vt_result else None,
        ai_analysis=f"VirusTotal analysis: {vt_result.get('malicious', 0)}/{vt_result.get('total', 0)} engines detected this file as malicious." if vt_result else "No VirusTotal results available.",
        recommended_action="Quarantine and investigate immediately." if risk_level in ("CRITICAL", "MALICIOUS") else "No action required." if risk_level == "CLEAN" else "Review manually.",
        analyzed_at=datetime.now(timezone.utc),
    )
    db.add(malware_report)
    db.commit()

    return {
        "id": db_file.id,
        "original_name": db_file.original_name,
        "sha256": sha256_hash,
        "md5": md5_hash,
        "size": len(content),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "detection_ratio": malware_report.detection_ratio,
        "threat_family": malware_report.threat_family,
        "malware_report_id": malware_report.id,
    }
