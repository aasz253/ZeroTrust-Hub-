import subprocess
import re
import socket
import json
from typing import Optional

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    465: "SMTPS", 587: "SMTP", 993: "IMAPS", 995: "POP3S",
    1433: "MSSQL", 1521: "Oracle", 2049: "NFS", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB",
}


def get_service_banner(ip: str, port: int, timeout: float = 2.0) -> Optional[str]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, port))
            s.send(b"\r\n")
            banner = s.recv(1024).decode("utf-8", errors="ignore").strip()
            return banner[:200] if banner else None
    except Exception:
        return None


def quick_scan(target: str) -> dict:
    findings = []
    critical = high = medium = low = 0

    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        return {"error": f"Could not resolve {target}"}

    for port in [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 3306, 3389, 5432, 8080, 8443]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                if s.connect_ex((ip, port)) == 0:
                    banner = get_service_banner(ip, port)
                    service = COMMON_PORTS.get(port, "unknown")
                    finding = {
                        "port": port,
                        "service": service,
                        "banner": banner,
                        "severity": "LOW",
                    }
                    if port in [21, 23, 3389]:
                        finding["severity"] = "HIGH"
                        high += 1
                    elif port in [445, 1433, 3306, 5432, 27017]:
                        finding["severity"] = "MEDIUM"
                        medium += 1
                    else:
                        low += 1
                    findings.append(finding)
        except Exception:
            pass

    return {
        "target": target,
        "ip_address": ip,
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        },
    }


def full_scan(target: str) -> dict:
    result = quick_scan(target)
    if "error" in result:
        return result

    try:
        proc = subprocess.run(
            ["nmap", "-sV", "--script", "vuln", "-p", "1-1000", target],
            capture_output=True, text=True, timeout=300,
        )
        raw = proc.stdout + proc.stderr

        nmap_findings = []
        for match in re.finditer(
            r"(\d+)/tcp\s+open\s+(\S+).*?\n(.*?)(?=\n\d+|$)",
            raw, re.DOTALL
        ):
            port = int(match.group(1))
            service = match.group(2)
            detail = match.group(3).strip()[:300]
            nmap_findings.append({
                "port": port,
                "service": service,
                "detail": detail,
                "severity": "MEDIUM" if "vuln" in detail.lower() else "LOW",
            })

        result["nmap_output"] = raw[:2000]
        result["nmap_findings"] = nmap_findings
        result["summary"]["total"] += len(nmap_findings)
    except subprocess.TimeoutExpired:
        result["nmap_error"] = "nmap scan timed out after 5 minutes"
    except FileNotFoundError:
        result["nmap_error"] = "nmap not available on this system"
    except Exception as e:
        result["nmap_error"] = str(e)

    return result


def port_scan(target: str) -> dict:
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        return {"error": f"Could not resolve {target}"}

    open_ports = []
    for port in sorted(COMMON_PORTS.keys()):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex((ip, port)) == 0:
                    banner = get_service_banner(ip, port)
                    open_ports.append({
                        "port": port,
                        "service": COMMON_PORTS.get(port, "unknown"),
                        "banner": banner,
                    })
        except Exception:
            pass

    return {
        "target": target,
        "ip_address": ip,
        "open_ports": open_ports,
        "total": len(open_ports),
    }
