import subprocess
import re
from typing import Optional


def list_available() -> list[dict]:
    networks = []
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "ssid,signal,security,chan", "dev", "wifi", "list"],
            capture_output=True, text=True, timeout=15,
        )
        seen = set()
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split(":")
            if len(parts) >= 3:
                ssid = parts[0]
                signal = parts[1]
                security = parts[2]
                channel = parts[3] if len(parts) > 3 else ""
                if ssid and ssid not in seen:
                    seen.add(ssid)
                    signal_int = int(signal) if signal.isdigit() else 0
                    networks.append({
                        "ssid": ssid,
                        "signal": signal_int,
                        "signal_percent": min(100, max(0, (signal_int + 100) // 2)),
                        "security": security if security != "" else "Open",
                        "channel": channel,
                    })
        networks.sort(key=lambda n: n["signal"], reverse=True)
    except Exception:
        pass
    return networks


def get_active_connection() -> Optional[dict]:
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "name,type,device", "con", "show", "--active"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 3 and parts[1] == "wifi":
                return {
                    "ssid": parts[0],
                    "interface": parts[2],
                    "status": "connected",
                }
    except Exception:
        pass
    return {"ssid": None, "interface": None, "status": "disconnected"}


def get_interface() -> Optional[str]:
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "device,type", "dev", "status"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 2 and parts[1] == "wifi":
                return parts[0]
    except Exception:
        pass
    return None


def connect(ssid: str, password: str = "") -> dict:
    iface = get_interface()
    if not iface:
        return {"success": False, "error": "No WiFi interface found"}

    try:
        cmd = ["nmcli", "dev", "wifi", "connect", ssid]
        if password:
            cmd.extend(["password", password])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {"success": True, "message": f"Connected to {ssid}"}
        else:
            error = result.stderr.strip() or result.stdout.strip()
            return {"success": False, "error": error}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Connection timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def disconnect() -> dict:
    active = get_active_connection()
    if not active or not active.get("ssid"):
        return {"success": False, "error": "Not connected to any WiFi"}

    iface = active.get("interface")
    if not iface:
        return {"success": False, "error": "No WiFi interface"}

    try:
        result = subprocess.run(
            ["nmcli", "dev", "disconnect", iface],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return {"success": True, "message": f"Disconnected from {active['ssid']}"}
        return {"success": False, "error": result.stderr.strip()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_status() -> dict:
    active = get_active_connection()
    networks = list_available()
    return {
        "active_connection": active,
        "available_networks": len(networks),
        "interface": get_interface(),
    }
