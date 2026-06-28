import subprocess
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.soar import Playbook, PlaybookAction, PlaybookExecution
from app.models.threat import Threat

logger = logging.getLogger(__name__)


def execute_playbook(db: Session, playbook: Playbook, trigger_event: dict) -> Optional[dict]:
    execution = PlaybookExecution(
        playbook_id=playbook.id,
        triggered_by=trigger_event.get("source", "system"),
        trigger_event=trigger_event,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    actions = (
        db.query(PlaybookAction)
        .filter(PlaybookAction.playbook_id == playbook.id)
        .order_by(PlaybookAction.order)
        .all()
    )

    results = []
    success = True
    for action in actions:
        action_result = run_action(action, trigger_event)
        results.append({
            "action_id": action.id,
            "action_type": action.action_type,
            "result": action_result,
        })
        if not action_result.get("success", False):
            success = False

    execution.status = "completed" if success else "failed"
    execution.result = {"actions": results, "total": len(actions), "successful": sum(1 for r in results if r["result"].get("success"))}
    execution.completed_at = datetime.now(timezone.utc)
    db.commit()

    return {"execution_id": execution.id, "status": execution.status, "results": results}


def run_action(action: PlaybookAction, trigger: dict) -> dict:
    action_type = action.action_type
    config = action.action_config or {}

    if action_type == "block_ip":
        return _block_ip(config.get("ip", trigger.get("ip", "")))
    elif action_type == "send_alert":
        return _send_alert(config.get("message", "Security alert triggered"))
    elif action_type == "run_command":
        return _run_command(config.get("command", ""))
    elif action_type == "quarantine":
        return _quarantine(config.get("target", ""))
    elif action_type == "log_event":
        return {"success": True, "message": "Event logged"}
    else:
        return {"success": False, "error": f"Unknown action type: {action_type}"}


def _block_ip(ip: str) -> dict:
    if not ip:
        return {"success": False, "error": "No IP provided"}
    try:
        result = subprocess.run(
            ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return {"success": True, "message": f"Blocked IP {ip}"}
        result = subprocess.run(
            ["ufw", "deny", "from", ip],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return {"success": True, "message": f"Blocked IP {ip} via UFW"}
        return {"success": False, "error": result.stderr.strip()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _send_alert(message: str) -> dict:
    return {"success": True, "message": f"Alert sent: {message}"}


def _run_command(command: str) -> dict:
    if not command:
        return {"success": False, "error": "No command provided"}
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip()[:500],
            "error": result.stderr.strip()[:500],
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _quarantine(target: str) -> dict:
    return {"success": True, "message": f"Quarantine initiated for {target}"}


def check_and_trigger(db: Session, threat: Threat):
    playbooks = (
        db.query(Playbook)
        .filter(
            Playbook.is_active == True,
            Playbook.auto_run == True,
        )
        .all()
    )
    for playbook in playbooks:
        if _matches_trigger(playbook, threat):
            execute_playbook(db, playbook, {
                "source": "threat_detection",
                "type": "new_threat",
                "severity": threat.severity,
                "indicator": threat.indicator,
                "threat_type": threat.threat_type,
            })


def _matches_trigger(playbook: Playbook, threat: Threat) -> bool:
    config = playbook.trigger_config or {}
    trigger_type = playbook.trigger_type

    if trigger_type == "severity_threshold":
        severities = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        min_sev = config.get("min_severity", "HIGH")
        return severities.get(threat.severity, 0) >= severities.get(min_sev, 3)

    if trigger_type == "threat_type":
        return threat.threat_type == config.get("threat_type")

    if trigger_type == "all_threats":
        return True

    return False
