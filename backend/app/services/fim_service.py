import os
import hashlib
import stat
import pwd
import grp
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.fim import FimEntry

WATCHED_PATHS = [
    "/etc/passwd", "/etc/shadow", "/etc/hosts", "/etc/hostname",
    "/etc/ssh/sshd_config", "/etc/sudoers", "/etc/crontab",
    "/etc/resolv.conf", "/etc/nginx/nginx.conf", "/etc/apache2/",
    "/var/log/auth.log", "/var/log/syslog",
]


def hash_file(filepath: str) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, FileNotFoundError, IsADirectoryError):
        return None


def get_file_info(filepath: str) -> Optional[dict]:
    try:
        st = os.stat(filepath)
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        file_hash = hash_file(filepath)
        perms = stat.filemode(st.st_mode)
        return {
            "file_path": filepath,
            "file_name": os.path.basename(filepath),
            "current_hash": file_hash,
            "file_size": st.st_size,
            "permissions": perms,
            "owner": f"{owner}:{group}",
            "modified": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc),
        }
    except (PermissionError, FileNotFoundError):
        return None


def scan_all_watched(db: Session) -> list[dict]:
    results = []
    for path in WATCHED_PATHS:
        if os.path.isfile(path):
            result = check_file(db, path)
            if result:
                results.append(result)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files[:50]:
                    fp = os.path.join(root, f)
                    result = check_file(db, fp)
                    if result:
                        results.append(result)
    return results


def check_file(db: Session, filepath: str) -> Optional[dict]:
    info = get_file_info(filepath)
    if not info:
        return None

    entry = db.query(FimEntry).filter(FimEntry.file_path == filepath).first()
    now = datetime.now(timezone.utc)

    if not entry:
        entry = FimEntry(
            file_path=filepath,
            file_name=info["file_name"],
            status="monitored",
            current_hash=info["current_hash"],
            previous_hash=info["current_hash"],
            file_size=info["file_size"],
            permissions=info["permissions"],
            owner=info["owner"],
            last_checked=now,
            last_changed=now,
            is_critical="etc/shadow" in filepath or "sudoers" in filepath,
        )
        db.add(entry)
        db.commit()
        return {"file_path": filepath, "status": "added", "hash": info["current_hash"]}

    changed = entry.current_hash != info["current_hash"]
    if changed:
        entry.previous_hash = entry.current_hash
        entry.current_hash = info["current_hash"]
        entry.file_size = info["file_size"]
        entry.permissions = info["permissions"]
        entry.owner = info["owner"]
        entry.last_changed = now
        entry.change_count = (entry.change_count or 0) + 1
        entry.status = "changed"

    entry.last_checked = now
    db.commit()

    return {
        "file_path": filepath,
        "status": "changed" if changed else "unchanged",
        "hash": info["current_hash"],
        "change_count": entry.change_count,
    }


def add_watched_path(db: Session, filepath: str) -> dict:
    if not os.path.exists(filepath):
        return {"success": False, "error": "File does not exist"}

    existing = db.query(FimEntry).filter(FimEntry.file_path == filepath).first()
    if existing:
        return {"success": False, "error": "Already being monitored"}

    info = get_file_info(filepath)
    if not info:
        return {"success": False, "error": "Cannot read file"}

    entry = FimEntry(
        file_path=filepath,
        file_name=info["file_name"],
        status="monitored",
        current_hash=info["current_hash"],
        previous_hash=info["current_hash"],
        file_size=info["file_size"],
        permissions=info["permissions"],
        owner=info["owner"],
        last_checked=datetime.now(timezone.utc),
    )
    db.add(entry)
    db.commit()
    return {"success": True, "file_path": filepath}
