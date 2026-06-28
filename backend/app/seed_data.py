from sqlalchemy.orm import Session
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


def seed_database():
    db = SessionLocal()
    try:
        if db.query(Role).count() > 0 and db.query(Threat).count() > 0:
            return

        permissions_data = [
            {"name": "view_dashboard", "resource": "dashboard", "action": "view"},
            {"name": "view_threats", "resource": "threats", "action": "view"},
            {"name": "create_threats", "resource": "threats", "action": "create"},
            {"name": "view_scans", "resource": "scans", "action": "view"},
            {"name": "create_scans", "resource": "scans", "action": "create"},
            {"name": "view_reports", "resource": "reports", "action": "view"},
            {"name": "create_reports", "resource": "reports", "action": "create"},
            {"name": "view_users", "resource": "users", "action": "view"},
            {"name": "manage_users", "resource": "users", "action": "manage"},
            {"name": "view_settings", "resource": "settings", "action": "view"},
            {"name": "manage_settings", "resource": "settings", "action": "manage"},
            {"name": "view_audit_logs", "resource": "audit_logs", "action": "view"},
            {"name": "manage_api_keys", "resource": "api_keys", "action": "manage"},
            {"name": "use_ai_assistant", "resource": "ai", "action": "use"},
            {"name": "upload_files", "resource": "files", "action": "upload"},
        ]

        permissions = {}
        for p_data in permissions_data:
            perm = Permission(**p_data)
            db.add(perm)
            db.flush()
            permissions[perm.name] = perm

        admin_role = Role(name="admin", description="Full system access")
        analyst_role = Role(name="analyst", description="Security analyst access")
        viewer_role = Role(name="viewer", description="Read-only access")

        admin_role.permissions = list(permissions.values())
        analyst_role.permissions = [
            permissions["view_dashboard"],
            permissions["view_threats"],
            permissions["create_threats"],
            permissions["view_scans"],
            permissions["create_scans"],
            permissions["view_reports"],
            permissions["create_reports"],
            permissions["use_ai_assistant"],
            permissions["upload_files"],
        ]
        viewer_role.permissions = [
            permissions["view_dashboard"],
            permissions["view_threats"],
            permissions["view_scans"],
            permissions["view_reports"],
        ]

        db.add(admin_role)
        db.add(analyst_role)
        db.add(viewer_role)
        db.flush()

        admin_user = User(
            email="admin@zerotrust.com",
            username="admin",
            hashed_password=hash_password("Admin123!"),
            full_name="System Administrator",
            is_active=True,
            role_id=admin_role.id,
        )
        analyst_user = User(
            email="analyst@zerotrust.com",
            username="analyst",
            hashed_password=hash_password("Analyst123!"),
            full_name="Security Analyst",
            is_active=True,
            role_id=analyst_role.id,
        )
        viewer_user = User(
            email="viewer@zerotrust.com",
            username="viewer",
            hashed_password=hash_password("Viewer123!"),
            full_name="Report Viewer",
            is_active=True,
            role_id=viewer_role.id,
        )
        db.add(admin_user)
        db.add(analyst_user)
        db.add(viewer_user)
        db.flush()

        threat_types = [
            ("malicious-ip", "IP Address"), ("malicious-domain", "Domain"),
            ("malicious-hash", "Hash"), ("phishing-url", "URL"),
            ("botnet-c2", "IP Address"), ("ransomware", "Hash"),
        ]
        severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        sources = ["AlienVault OTX", "AbuseIPDB", "VirusTotal", "MISP", "Internal"]

        sample_threats = [
            ("185.220.101.1", "IP Address", "C2 Server Communication", "CRITICAL"),
            ("malware-domain.com", "Domain", "Malware Distribution", "HIGH"),
            ("eicar-test-string", "Hash", "EICAR Test Pattern", "MEDIUM"),
            ("phishing-bank.com", "Domain", "Phishing Campaign", "CRITICAL"),
            ("45.33.32.156", "IP Address", "SSH Brute Force", "HIGH"),
            ("ransomware-sample.exe", "Hash", "Ransomware Strain", "CRITICAL"),
            ("192.168.1.100", "IP Address", "Port Scanning", "LOW"),
            ("botnet-c2.example.com", "Domain", "Botnet C2", "HIGH"),
            ("trojan-downloader.exe", "Hash", "Trojan Downloader", "MEDIUM"),
            ("10.0.0.50", "IP Address", "DNS Tunneling", "MEDIUM"),
        ]

        for indicator, ioc_type, desc, sev in sample_threats:
            threat = Threat(
                indicator=indicator,
                indicator_type=ioc_type,
                threat_type=desc,
                severity=sev,
                confidence=random.uniform(0.5, 1.0),
                source=random.choice(sources),
                description=f"Detected {desc.lower()} activity",
                is_active=random.choice([True, True, False]),
                first_seen=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
                last_seen=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
            )
            db.add(threat)

        sample_vulns = [
            ("CVE-2024-21626", "runc container breakout", "CRITICAL", 9.8, "runc", "runc"),
            ("CVE-2024-3094", "XZ Utils backdoor", "CRITICAL", 10.0, "Tukaani", "XZ Utils"),
            ("CVE-2024-27198", "JetBrains TeamCity auth bypass", "CRITICAL", 9.8, "JetBrains", "TeamCity"),
            ("CVE-2024-6387", "OpenSSH regreSSHion", "HIGH", 8.1, "OpenBSD", "OpenSSH"),
            ("CVE-2024-4577", "PHP CGI argument injection", "CRITICAL", 9.8, "PHP", "PHP"),
            ("CVE-2024-38077", "Windows Remote Desktop licensing", "CRITICAL", 9.8, "Microsoft", "Windows"),
            ("CVE-2024-31497", "PuTTY private key recovery", "HIGH", 7.5, "PuTTY", "PuTTY"),
            ("CVE-2024-28995", "SolarWinds Serv-U directory traversal", "HIGH", 7.5, "SolarWinds", "Serv-U"),
            ("CVE-2024-22252", "VMware ESXi use-after-free", "CRITICAL", 9.8, "VMware", "ESXi"),
            ("CVE-2024-1709", "ConnectWise ScreenConnect auth bypass", "CRITICAL", 10.0, "ConnectWise", "ScreenConnect"),
        ]

        for cve_id, title, severity, score, vendor, product in sample_vulns:
            vuln = Vulnerability(
                cve_id=cve_id,
                title=title,
                description=f"A vulnerability in {product} by {vendor} allows remote code execution.",
                severity=severity,
                cvss_score=score,
                affected_vendor=vendor,
                affected_product=product,
                published_date=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90)),
                remediation=f"Apply the latest security patch from {vendor}",
            )
            db.add(vuln)

        device_data = [
            ("10.0.1.1", "Gateway", "online", [80, 443, 22], "Linux", "Ubuntu 22.04"),
            ("10.0.1.10", "Web Server", "online", [80, 443], "Linux", "Ubuntu 22.04"),
            ("10.0.1.20", "Database", "online", [5432, 22], "Linux", "Debian 12"),
            ("10.0.1.30", "Mail Server", "online", [25, 587, 993], "Linux", "CentOS 9"),
            ("10.0.1.50", "Dev Workstation", "offline", [22], "Windows", "Windows 11"),
            ("192.168.1.100", "Unknown Device", "suspicious", [22, 3389, 445], "Unknown", ""),
        ]
        for ip, hostname, status, ports, os_name, os_ver in device_data:
            if not db.query(Device).filter(Device.ip_address == ip).first():
                db.add(Device(
                    ip_address=ip, hostname=hostname, status=status,
                    open_ports=ports, os=os_name, os_version=os_ver,
                    risk_score=7.5 if status == "suspicious" else 1.0,
                    last_seen=datetime.now(timezone.utc),
                ))

        settings_data = [
            ("ai_provider", "openai", "string", "ai", "AI provider configuration"),
            ("scan_timeout", "300", "integer", "scanner", "Scan timeout in seconds"),
            ("auto_sync_cve", "true", "boolean", "cve", "Auto-sync CVE data"),
            ("retention_days", "90", "integer", "general", "Data retention period"),
            ("max_upload_size", "104857600", "integer", "files", "Max upload size in bytes"),
        ]
        for key, value, value_type, category, desc in settings_data:
            db.add(Setting(
                key=key, value=value, value_type=value_type,
                category=category, description=desc,
            ))

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
