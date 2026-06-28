import psutil
import os
from datetime import datetime, timezone
from typing import Optional

SUSPICIOUS_NAMES = [
    "powershell.exe", "cmd.exe", "wscript.exe", "cscript.exe",
    "mshta.exe", "regsvr32.exe", "rundll32.exe", "taskkill.exe",
    "net.exe", "nltest.exe", "psexec.exe", "mimikatz.exe",
    "nc.exe", "ncat.exe", "wget.exe", "certutil.exe",
]

SUSPICIOUS_ARGS = [
    "-enc", "-encodedcommand", "bypass", "hidden",
    "downloadstring", "invoke-expression", "iex",
    "start-process -hidden", "create process",
    "dumpcred", "sekurlsa",
]

SUSPICIOUS_PORTS = [4444, 5555, 6666, 7777, 8443, 9001, 1337, 31337, 4443, 8081]


def scan_processes() -> list[dict]:
    processes = []
    for proc in psutil.process_iter(["pid", "name", "exe", "cmdline", "username", "cpu_percent", "memory_percent", "connections"]):
        try:
            pinfo = proc.info
            cmdline = " ".join(pinfo["cmdline"] or [])
            is_suspicious = False
            reason = None

            name = (pinfo["name"] or "").lower()
            if name in SUSPICIOUS_NAMES:
                is_suspicious = True
                reason = f"Suspicious process name: {name}"

            for arg in SUSPICIOUS_ARGS:
                if arg in cmdline.lower():
                    is_suspicious = True
                    reason = f"Suspicious argument: {arg}"
                    break

            connections = []
            try:
                for conn in proc.connections():
                    conn_info = {
                        "fd": conn.fd,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "laddr": str(conn.laddr),
                        "raddr": str(conn.raddr),
                        "status": conn.status,
                    }
                    connections.append(conn_info)
                    if conn.raddr and hasattr(conn.raddr, "port") and conn.raddr.port in SUSPICIOUS_PORTS:
                        is_suspicious = True
                        reason = f"Connection to suspicious port: {conn.raddr.port}"
            except (psutil.AccessDenied, ValueError):
                pass

            if pinfo["cpu_percent"] and pinfo["cpu_percent"] > 80:
                if not is_suspicious:
                    is_suspicious = True
                    reason = f"High CPU usage: {pinfo['cpu_percent']}%"

            processes.append({
                "pid": pinfo["pid"],
                "name": pinfo["name"],
                "exe": pinfo["exe"],
                "cmdline": cmdline[:500] if cmdline else "",
                "username": pinfo["username"],
                "cpu_percent": round(pinfo["cpu_percent"] or 0, 1),
                "memory_percent": round(pinfo["memory_percent"] or 0, 1),
                "connections": connections[:10],
                "is_suspicious": is_suspicious,
                "anomaly_reason": reason,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
            continue

    return processes


def get_process_detail(pid: int) -> Optional[dict]:
    try:
        proc = psutil.Process(pid)
        return {
            "pid": proc.pid,
            "name": proc.name(),
            "exe": proc.exe(),
            "cmdline": " ".join(proc.cmdline()),
            "username": proc.username(),
            "cpu_percent": proc.cpu_percent(interval=0.5),
            "memory_percent": proc.memory_percent(),
            "connections": [
                {"laddr": str(c.laddr), "raddr": str(c.raddr), "status": c.status}
                for c in proc.connections()
            ][:20],
            "open_files": [f.path for f in proc.open_files()][:20],
            "create_time": datetime.fromtimestamp(proc.create_time(), tz=timezone.utc).isoformat(),
            "status": proc.status(),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None
