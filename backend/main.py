from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.middleware.cors import setup_cors
from app.middleware.security import security_middleware
from app.database.session import engine, Base
from app.websocket_manager import ws_manager
from app.seed_data import seed_database
from app.core.security import decode_token
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Database table creation failed: {e}")
    try:
        seed_database()
        logger.info("Database seeded")
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
    try:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    except Exception as e:
        logger.error(f"Upload dir creation failed: {e}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="ZeroTrust Hub - AI-Powered Cybersecurity Dashboard API",
    lifespan=lifespan,
)

setup_cors(app)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With, Origin, Accept",
}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=CORS_HEADERS,
    )


app.middleware("http")(security_middleware)


from app.routers import auth as auth_router_mod
from app.routers import dashboard as dash_router_mod
from app.routers import vulnerabilities as vuln_router_mod
from app.routers import threats as threat_router_mod
from app.routers import scans as scan_router_mod
from app.routers import ai as ai_router_mod
from app.routers import reports as report_router_mod
from app.routers import notifications as notif_router_mod
from app.routers import files as file_router_mod
from app.routers import settings as settings_router_mod
from app.routers import users as user_router_mod
from app.routers import audit_logs as audit_router_mod
from app.routers import api_keys as apikey_router_mod
from app.routers import network as network_router_mod
from app.routers import wifi as wifi_router_mod
from app.routers import mfa as mfa_router_mod
from app.routers import siem as siem_router_mod
from app.routers import edr as edr_router_mod
from app.routers import soar as soar_router_mod
from app.routers import fim as fim_router_mod

app.include_router(auth_router_mod.router)
app.include_router(mfa_router_mod.router)
app.include_router(network_router_mod.router)
app.include_router(wifi_router_mod.router)
app.include_router(siem_router_mod.router)
app.include_router(edr_router_mod.router)
app.include_router(soar_router_mod.router)
app.include_router(fim_router_mod.router)
app.include_router(user_router_mod.router)
app.include_router(dash_router_mod.router)
app.include_router(vuln_router_mod.router)
app.include_router(threat_router_mod.router)
app.include_router(scan_router_mod.router)
app.include_router(ai_router_mod.router)
app.include_router(report_router_mod.router)
app.include_router(notif_router_mod.router)
app.include_router(file_router_mod.router)
app.include_router(settings_router_mod.router)
app.include_router(audit_router_mod.router)
app.include_router(apikey_router_mod.router)


@app.post("/api/debug/seed-data")
def force_seed():
    from app.database.session import SessionLocal
    from app.models.role import Role, Permission
    from app.models.user import User
    from app.models.setting import Setting
    from app.models.threat import Threat
    from app.models.vulnerability import Vulnerability
    from app.models.network import Device
    from app.core.security import hash_password
    from datetime import datetime, timedelta, timezone
    import random

    db = SessionLocal()
    try:
        threat_data = [
            ("185.220.101.1", "IP Address", "C2 Server Communication", "CRITICAL"),
            ("malware-domain.com", "Domain", "Malware Distribution", "HIGH"),
            ("45.33.32.156", "IP Address", "SSH Brute Force", "HIGH"),
            ("phishing-bank.com", "Domain", "Phishing Campaign", "CRITICAL"),
            ("192.168.1.100", "IP Address", "Port Scanning", "LOW"),
            ("botnet-c2.example.com", "Domain", "Botnet C2", "HIGH"),
            ("10.0.0.50", "IP Address", "DNS Tunneling", "MEDIUM"),
            ("ransomware-sample.exe", "Hash", "Ransomware", "CRITICAL"),
            ("trojan-downloader.exe", "Hash", "Trojan Downloader", "MEDIUM"),
            ("evil.com", "Domain", "Malicious Domain", "HIGH"),
        ]
        sources = ["AlienVault", "AbuseIPDB", "VirusTotal", "MISP"]

        for indicator, ioc_type, desc, sev in threat_data:
            if not db.query(Threat).filter(Threat.indicator == indicator).first():
                db.add(Threat(
                    indicator=indicator, indicator_type=ioc_type,
                    threat_type=desc, severity=sev,
                    confidence=random.uniform(0.6, 1.0),
                    source=random.choice(sources),
                    is_active=True,
                    first_seen=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
                    last_seen=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
                ))

        vuln_data = [
            ("CVE-2024-21626", "runc container breakout", "CRITICAL", 9.8, "runc", "Apply latest patch"),
            ("CVE-2024-3094", "XZ Utils backdoor", "CRITICAL", 10.0, "Tukaani", "Update to patched version"),
            ("CVE-2024-6387", "OpenSSH regreSSHion", "HIGH", 8.1, "OpenBSD", "Update OpenSSH"),
            ("CVE-2024-4577", "PHP CGI argument injection", "CRITICAL", 9.8, "PHP", "Apply PHP patch"),
            ("CVE-2024-38077", "Windows RDL exploit", "CRITICAL", 9.8, "Microsoft", "Apply security update"),
            ("CVE-2024-31497", "PuTTY key recovery", "HIGH", 7.5, "PuTTY", "Update PuTTY"),
            ("CVE-2024-1709", "ScreenConnect auth bypass", "CRITICAL", 10.0, "ConnectWise", "Update immediately"),
            ("CVE-2024-22252", "VMware ESXi escape", "CRITICAL", 9.8, "VMware", "Apply VMware patch"),
            ("CVE-2024-28995", "SolarWinds path traversal", "HIGH", 7.5, "SolarWinds", "Apply patch"),
            ("CVE-2024-27198", "TeamCity auth bypass", "CRITICAL", 9.8, "JetBrains", "Update TeamCity"),
        ]
        for cve_id, title, sev, score, vendor, remediation in vuln_data:
            if not db.query(Vulnerability).filter(Vulnerability.cve_id == cve_id).first():
                db.add(Vulnerability(
                    cve_id=cve_id, title=title, severity=sev, cvss_score=score,
                    affected_vendor=vendor, remediation=remediation,
                    description=f"Security vulnerability in {vendor}",
                    published_date=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90)),
                ))

        device_data = [
            ("10.0.1.1", "Gateway", "online", [80, 443, 22], "Linux", "Ubuntu 22.04", 1.0),
            ("10.0.1.10", "Web Server", "online", [80, 443], "Linux", "Ubuntu 22.04", 1.0),
            ("10.0.1.20", "Database", "online", [5432, 22], "Linux", "Debian 12", 1.0),
            ("10.0.1.30", "Mail Server", "online", [25, 587, 993], "Linux", "CentOS 9", 1.0),
            ("10.0.1.50", "Dev Workstation", "offline", [22], "Windows", "Windows 11", 1.0),
            ("192.168.1.100", "Unknown Device", "suspicious", [22, 3389, 445], "Unknown", "", 7.5),
        ]
        for ip, hostname, status, ports, os_name, os_ver, risk in device_data:
            if not db.query(Device).filter(Device.ip_address == ip).first():
                db.add(Device(
                    ip_address=ip, hostname=hostname, status=status,
                    open_ports=ports, os=os_name, os_version=os_ver,
                    risk_score=risk, last_seen=datetime.now(timezone.utc),
                ))

        db.commit()
        return {"detail": f"Seeded {len(threat_data)} threats, {len(vuln_data)} vulnerabilities, {len(device_data)} devices"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


@app.post("/api/debug/fix-admin")
def fix_admin():
    from app.database.session import SessionLocal
    from app.models.role import Role
    from app.models.user import User
    db = SessionLocal()
    try:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.add(admin_role)
            db.flush()
        admin_user = db.query(User).filter(User.email == "admin@zerotrust.com").first()
        if admin_user:
            admin_user.role_id = admin_role.id
            db.commit()
            return {"detail": "Admin role assigned to admin@zerotrust.com"}
        return {"detail": "Admin user not found"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": settings.VERSION, "app": settings.APP_NAME}


@app.get("/api/debug/db-check")
def db_check():
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            return {"db": "connected", "result": result[0]}
    except Exception as e:
        return {"db": "error", "detail": str(e)}


@app.get("/api/debug/seed-check")
def seed_check():
    from app.database.session import SessionLocal
    db = SessionLocal()
    try:
        from app.models.role import Role
        from app.models.user import User
        roles = db.query(Role).count()
        users = db.query(User).count()
        return {"roles": roles, "users": users}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        await websocket.close(code=4001)
        return

    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.send_notification(user_id, {
                "type": "pong",
                "data": data,
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
    except Exception:
        ws_manager.disconnect(websocket, user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
