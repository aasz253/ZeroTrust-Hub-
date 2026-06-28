import socket
import threading
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.siem import SiemLog

logger = logging.getLogger(__name__)

SYSLOG_PORT = 514
_syslog_server: Optional[threading.Thread] = None
_syslog_running = False


def start_syslog_server(db_session_factory):
    global _syslog_server, _syslog_running
    if _syslog_running:
        return

    _syslog_running = True
    _syslog_server = threading.Thread(
        target=_run_syslog_server,
        args=(db_session_factory,),
        daemon=True,
    )
    _syslog_server.start()
    logger.info("Syslog UDP receiver started on port %d", SYSLOG_PORT)


def _run_syslog_server(db_session_factory):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)
    try:
        sock.bind(("0.0.0.0", SYSLOG_PORT))
    except PermissionError:
        logger.warning("Cannot bind to port %d (need root). Syslog disabled.", SYSLOG_PORT)
        return
    except OSError:
        logger.warning("Port %d in use. Syslog disabled.", SYSLOG_PORT)
        return

    while _syslog_running:
        try:
            data, addr = sock.recvfrom(65535)
            raw = data.decode("utf-8", errors="ignore")
            db = db_session_factory()
            try:
                log_entry = parse_syslog(raw, addr[0])
                db.add(log_entry)
                db.commit()
            except Exception as e:
                logger.error("Failed to parse syslog: %s", e)
                db.rollback()
            finally:
                db.close()
        except socket.timeout:
            continue
        except Exception as e:
            logger.error("Syslog server error: %s", e)

    sock.close()


def parse_syslog(raw: str, source_ip: str) -> SiemLog:
    entry = SiemLog(
        source_ip=source_ip,
        raw=raw,
        message=raw,
        timestamp=datetime.now(timezone.utc),
    )
    if "emerg" in raw.lower():
        entry.severity = "EMERGENCY"
    elif "alert" in raw.lower():
        entry.severity = "ALERT"
    elif "crit" in raw.lower():
        entry.severity = "CRITICAL"
    elif "err" in raw.lower():
        entry.severity = "ERROR"
    elif "warn" in raw.lower():
        entry.severity = "WARNING"
    elif "notice" in raw.lower():
        entry.severity = "NOTICE"
    elif "info" in raw.lower():
        entry.severity = "INFO"
    else:
        entry.severity = "DEBUG"

    return entry


def correlate_logs(db: Session, log_id: int) -> list[SiemLog]:
    log = db.query(SiemLog).filter(SiemLog.id == log_id).first()
    if not log:
        return []

    related = (
        db.query(SiemLog)
        .filter(
            SiemLog.source_ip == log.source_ip,
            SiemLog.id != log.id,
        )
        .order_by(SiemLog.timestamp.desc())
        .limit(50)
        .all()
    )
    return related
