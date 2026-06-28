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
from datetime import datetime, timezone

router = APIRouter(prefix="/api/files", tags=["Files"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = FileUpload(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large",
        )

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

    malware_report = MalwareReport(
        file_name=file.filename or "unknown",
        file_hash_sha256=sha256_hash,
        file_hash_md5=md5_hash,
        file_size=len(content),
        file_type=file.content_type or "application/octet-stream",
        risk_score=0.0,
        risk_level="UNKNOWN",
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
        "malware_report_id": malware_report.id,
    }
