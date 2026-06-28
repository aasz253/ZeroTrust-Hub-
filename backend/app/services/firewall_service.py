import subprocess
import re
import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.firewall import FirewallRule, RuleAction, RuleDirection, RuleProtocol

logger = logging.getLogger(__name__)

IPTABLES = "/sbin/iptables"
NFT = "/usr/sbin/nft"


def _run(cmd: list[str]) -> tuple[str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return "", "command not found"
    except Exception as e:
        return "", str(e)


def _has_nftables() -> bool:
    out, _ = _run([NFT, "--version"])
    return "nftables" in out


def _has_iptables() -> bool:
    out, _ = _run([IPTABLES, "--version"])
    return "iptables" in out


def get_firewall_type() -> str:
    if _has_nftables():
        return "nftables"
    if _has_iptables():
        return "iptables"
    return "none"


def _apply_iptables(rule: FirewallRule, add: bool = True) -> bool:
    cmd = [IPTABLES]
    if rule.direction == "inbound":
        cmd += ["-A", "INPUT"]
    elif rule.direction == "outbound":
        cmd += ["-A", "OUTPUT"]
    else:
        cmd += ["-A", "FORWARD"]

    if rule.protocol and rule.protocol != "any":
        cmd += ["-p", rule.protocol]
    if rule.source_ip:
        cmd += ["-s", rule.source_ip]
    if rule.destination_ip:
        cmd += ["-d", rule.destination_ip]
    if rule.source_port:
        cmd += ["--sport", str(rule.source_port)]
    if rule.destination_port:
        cmd += ["--dport", str(rule.destination_port)]
    if rule.interface:
        cmd += ["-i", rule.interface]

    if rule.action == "allow":
        cmd += ["-j", "ACCEPT"]
    elif rule.action == "block":
        cmd += ["-j", "DROP"]
    elif rule.action == "rate_limit":
        cmd += ["-m", "limit", "--limit", "5/min", "-j", "ACCEPT"]

    if rule.log_hits:
        cmd = cmd[:-1] + ["-j", "LOG", "--log-prefix", f"FW-RULE-{rule.id}: "] + cmd[-1:]

    if not add:
        cmd[1] = "-D" if cmd[1] == "-A" else "-D"

    out, err = _run(cmd)
    if err:
        logger.error(f"iptables error: {err}")
        return False
    return True


def _apply_nftables(rule: FirewallRule, add: bool = True) -> bool:
    family = "ip"
    table = "filter"
    chain = rule.direction or "input"

    if add:
        expr = f"add rule {family} {table} {chain}"
    else:
        expr = f"delete rule {family} {table} {chain}"

    criteria = []
    if rule.protocol and rule.protocol != "any":
        criteria.append(f"meta l4proto {rule.protocol}")
    if rule.source_ip:
        criteria.append(f"ip saddr {rule.source_ip}")
    if rule.destination_ip:
        criteria.append(f"ip daddr {rule.destination_ip}")
    if rule.source_port:
        criteria.append(f"th sport {rule.source_port}")
    if rule.destination_port:
        criteria.append(f"th dport {rule.destination_port}")

    action = "accept" if rule.action == "allow" else "drop"
    if criteria:
        expr += f" {' '.join(criteria)} {action}"
    else:
        expr += f" {action}"

    out, err = _run(["bash", "-c", f"echo '{expr}' | {NFT} -f -"])
    if err and "Error" in err:
        logger.error(f"nftables error: {err}")
        return False
    return True


def apply_rule(rule: FirewallRule, add: bool = True) -> bool:
    fw_type = get_firewall_type()
    if fw_type == "nftables":
        return _apply_nftables(rule, add)
    elif fw_type == "iptables":
        return _apply_iptables(rule, add)
    else:
        logger.warning("No firewall tool available")
        return False


def sync_rules_to_system(db: Session) -> dict:
    rules = db.query(FirewallRule).filter(FirewallRule.is_active == True).all()
    applied = 0
    failed = 0
    for rule in rules:
        if apply_rule(rule, add=True):
            applied += 1
        else:
            failed += 1
    return {"applied": applied, "failed": failed, "total": len(rules)}


def get_system_rules() -> list[dict]:
    items = []
    fw_type = get_firewall_type()
    if fw_type == "iptables":
        out, _ = _run([IPTABLES, "-L", "-n", "--line-numbers"])
        if out:
            for line in out.split("\n"):
                if "ACCEPT" in line or "DROP" in line or "REJECT" in line:
                    items.append({"type": "iptables", "line": line})
    elif fw_type == "nftables":
        out, _ = _run([NFT, "list", "ruleset"])
        if out:
            items.append({"type": "nftables", "dump": out[:10000]})
    return items


def flush_system_rules() -> bool:
    fw_type = get_firewall_type()
    if fw_type == "iptables":
        for chain in ["INPUT", "OUTPUT", "FORWARD"]:
            _run([IPTABLES, "-F", chain])
        return True
    elif fw_type == "nftables":
        _run([NFT, "flush", "ruleset"])
        return True
    return False
