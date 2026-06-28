import socket
import threading
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.honeypot import HoneypotEvent

logger = logging.getLogger(__name__)

HONEYPOT_SERVICES = {
    2222: "ssh",
    8080: "http",
    3307: "mysql",
}

_active_listeners = []
_running = False


class HoneypotListener:
    def __init__(self, service: str, port: int, db_session_factory):
        self.service = service
        self.port = port
        self.db_factory = db_session_factory
        self.sock = None
        self.thread = None

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1.0)
        try:
            self.sock.bind(("0.0.0.0", self.port))
            self.sock.listen(5)
            self.thread = threading.Thread(target=self._listen, daemon=True)
            self.thread.start()
            logger.info(f"Honeypot {self.service} listening on port {self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start {self.service} honeypot on port {self.port}: {e}")
            return False

    def stop(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

    def _listen(self):
        while _running:
            try:
                conn, addr = self.sock.accept()
                threading.Thread(target=self._handle, args=(conn, addr), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                if _running:
                    logger.error(f"Honeypot accept error: {e}")
                break

    def _handle(self, conn, addr):
        ip, port = addr
        try:
            conn.settimeout(10)
            if self.service == "ssh":
                self._handle_ssh(conn, ip, port)
            elif self.service == "http":
                self._handle_http(conn, ip, port)
            elif self.service == "mysql":
                self._handle_mysql(conn, ip, port)
        except Exception as e:
            logger.debug(f"Honeypot handle error: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _log_event(self, ip: str, port: int, username: str = None, password: str = None,
                   command: str = None, payload: str = None, attack_type: str = None):
        try:
            db: Session = self.db_factory()
            event = HoneypotEvent(
                service=self.service,
                source_ip=ip,
                source_port=port,
                destination_port=self.port,
                protocol="tcp",
                username=username,
                password=password,
                command=command,
                payload=payload,
                attack_type=attack_type or "connection",
                severity="HIGH" if attack_type in ("brute_force", "exploit") else "MEDIUM",
                timestamp=datetime.now(timezone.utc),
            )
            db.add(event)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to log honeypot event: {e}")

    def _handle_ssh(self, conn, ip, port):
        banner = b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3\r\n"
        conn.send(banner)
        data = conn.recv(4096)
        raw = data.decode("utf-8", errors="replace")
        username, password = "", ""
        if "SSH-" in raw:
            pass
        elif "\x00" in raw:
            payload = raw
            self._log_event(ip, port, payload=raw, attack_type="ssh_probe")
            conn.send(b"Protocol mismatch.\r\n")
            return
        conn.send(b"Password: ")
        try:
            pwd_data = conn.recv(4096)
            password = pwd_data.decode("utf-8", errors="replace").strip()
            self._log_event(ip, port, username="root", password=password, attack_type="brute_force")
        except Exception:
            pass
        conn.send(b"\nAuthentication failed.\r\n")

    def _handle_http(self, conn, ip, port):
        try:
            data = conn.recv(8192)
            raw = data.decode("utf-8", errors="replace")
            lines = raw.split("\r\n")
            request_line = lines[0] if lines else ""
            method = "GET"
            path = "/"
            if request_line:
                parts = request_line.split(" ")
                if len(parts) >= 2:
                    method = parts[0]
                    path = parts[1]
            attack_type = None
            for keyword in ["admin", "wp-admin", "phpmyadmin", ".env", "mysql", "config", "shell", "cmd", "exec"]:
                if keyword in path.lower():
                    attack_type = "scanning"
                    break
            for keyword in ["'", " UNION ", "SELECT ", "DROP ", "1=1", "../"]:
                if keyword in raw:
                    attack_type = "exploit"
                    break
            self._log_event(ip, port, payload=raw[:2000], attack_type=attack_type or "http_probe")
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/html\r\n"
                b"Server: Apache/2.4.41\r\n"
                b"Content-Length: 189\r\n"
                b"\r\n"
                b"<html><body><h1>Welcome to nginx!</h1>"
                b"<p>If you see this page, the nginx web server is successfully installed.</p>"
                b"</body></html>"
            )
            conn.send(response)
        except Exception:
            pass

    def _handle_mysql(self, conn, ip, port):
        greeting = (
            b"\x4a\x00\x00\x00\x0a\x38\x2e\x30\x2e\x33\x36\x00"
            b"\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x2f\x3a\x4b\x5c\x6d\x7e\x8f\x00\x63\x61\x63\x68\x69\x6e\x67\x5f"
            b"\x73\x68\x61\x32\x5f\x70\x61\x73\x73\x77\x6f\x72\x64\x00"
        )
        conn.send(greeting)
        try:
            data = conn.recv(4096)
            raw = data.hex()
            if len(data) > 4:
                username = data[4:].split(b"\x00")[0].decode("utf-8", errors="replace")
                self._log_event(ip, port, username=username, payload=raw[:500], attack_type="database_probe")
            else:
                self._log_event(ip, port, payload=raw[:500], attack_type="mysql_probe")
        except Exception:
            pass
        conn.send(b"\xff\x00\x00\x00\x02\x04Access denied\r\n")


def start_honeypots(db_session_factory):
    global _running
    _running = True
    for port, service in HONEYPOT_SERVICES.items():
        listener = HoneypotListener(service, port, db_session_factory)
        if listener.start():
            _active_listeners.append(listener)
    return _active_listeners


def stop_honeypots():
    global _running
    _running = False
    for listener in _active_listeners:
        listener.stop()
    _active_listeners.clear()
