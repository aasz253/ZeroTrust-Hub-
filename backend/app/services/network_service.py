import subprocess
import re
import socket
from typing import Optional

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    465: "SMTPS", 587: "SMTP", 993: "IMAPS", 995: "POP3S",
    1433: "MSSQL", 1521: "Oracle", 2049: "NFS", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB",
}


def get_wifi_ssid() -> Optional[str]:
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi", "list"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().split("\n"):
            if line.startswith("yes:"):
                return line.split(":", 1)[1]
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["iwgetid", "-r"], capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_gateway_ip() -> Optional[str]:
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True, text=True, timeout=5
        )
        match = re.search(r"via\s+(\S+)", result.stdout)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def get_network_name() -> Optional[str]:
    try:
        result = subprocess.run(
            ["ip", "-o", "-4", "addr", "show"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 4 and parts[3] != "lo":
                return parts[1]
    except Exception:
        pass
    return None


def check_port(ip: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((ip, port)) == 0
    except Exception:
        return False


def discover_devices() -> list[dict]:
    devices = []
    seen_ips = set()

    try:
        result = subprocess.run(
            ["arp", "-a"], capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().split("\n"):
            match = re.match(
                r".*?\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)",
                line
            )
            if match:
                ip = match.group(1)
                mac = match.group(2)
                if ip not in seen_ips:
                    seen_ips.add(ip)
                    hostname = None
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except Exception:
                        pass

                    open_ports = []
                    for port in sorted(COMMON_PORTS.keys()):
                        if check_port(ip, port, timeout=0.5):
                            open_ports.append(port)

                    devices.append({
                        "ip_address": ip,
                        "mac_address": mac,
                        "hostname": hostname,
                        "status": "online" if open_ports else "offline",
                        "open_ports": open_ports,
                        "risk_score": round(len(open_ports) * 0.5, 1),
                    })
    except Exception:
        pass

    return devices


def get_network_info() -> dict:
    return {
        "wifi_ssid": get_wifi_ssid(),
        "gateway_ip": get_gateway_ip(),
        "interface_name": get_network_name(),
    }
