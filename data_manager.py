"""
data_manager.py
---------------
Handles all permanent data storage for the Agent Gatekeeper application.

This module reads and writes two JSON files inside the 'data/' folder:
  - agents.json      : stores all registered and revoked agent records
  - audit_log.json   : stores every decision ever made by the rules engine

No database or internet connection is required – everything is saved locally.
"""

import json
import os
from datetime import datetime

# ── Folder and file paths ──────────────────────────────────────────────────────
DATA_DIR      = os.path.join(os.path.dirname(__file__), "data")
AGENTS_FILE   = os.path.join(DATA_DIR, "agents.json")
AUDIT_FILE    = os.path.join(DATA_DIR, "audit_log.json")


def _ensure_data_dir():
    """Create the data/ directory if it does not already exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
#  AGENT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def load_agents() -> list:
    """Return the list of all agent records (active + revoked)."""
    _ensure_data_dir()
    if not os.path.exists(AGENTS_FILE):
        return []
    with open(AGENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_agents(agents: list):
    """Write the full agent list back to disk."""
    _ensure_data_dir()
    with open(AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, indent=2, ensure_ascii=False)


def register_agent(customer_name: str, agent_name: str, authorised: bool) -> dict:
    """
    Register a new AI agent for a customer.

    Parameters
    ----------
    customer_name : str   – The customer's full name.
    agent_name    : str   – A unique name for the AI agent.
    authorised    : bool  – True if the customer authorises up to ₹10,000 spending.

    Returns
    -------
    dict  – The newly created agent record, or an error dict if name already taken.
    """
    agents = load_agents()

    # Check for duplicate active agent name (case-insensitive)
    for agent in agents:
        if (agent["agent_name"].lower() == agent_name.lower()
                and agent["customer_name"].lower() == customer_name.lower()
                and agent["status"] == "active"):
            return {"error": f"Agent '{agent_name}' is already registered for '{customer_name}'."}

    new_agent = {
        "customer_name":    customer_name.strip(),
        "agent_name":       agent_name.strip(),
        "authorised":       authorised,
        "status":           "active",
        "registered_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "revoked_at":       None,
    }
    agents.append(new_agent)
    _save_agents(agents)
    return new_agent


def revoke_agent(customer_name: str, agent_name: str) -> dict:
    """
    Revoke an active agent.  The record is kept but marked 'revoked'.

    Returns a result dict with key 'success' or 'error'.
    """
    agents = load_agents()
    for agent in agents:
        if (agent["agent_name"].lower() == agent_name.lower()
                and agent["customer_name"].lower() == customer_name.lower()
                and agent["status"] == "active"):
            agent["status"]     = "revoked"
            agent["revoked_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _save_agents(agents)
            return {"success": True, "agent": agent}

    return {"error": f"No active agent named '{agent_name}' found for customer '{customer_name}'."}


def get_agent(customer_name: str, agent_name: str) -> dict | None:
    """
    Look up an agent by customer name + agent name.
    Returns the most recently registered record, or None if not found.
    """
    agents = load_agents()
    matches = [
        a for a in agents
        if a["agent_name"].lower()   == agent_name.lower()
        and a["customer_name"].lower() == customer_name.lower()
    ]
    if not matches:
        return None
    # Return the latest registration
    return matches[-1]


def get_active_agents() -> list:
    """Return only agents with status == 'active'."""
    return [a for a in load_agents() if a["status"] == "active"]


def get_revoked_agents() -> list:
    """Return only agents with status == 'revoked'."""
    return [a for a in load_agents() if a["status"] == "revoked"]


# ══════════════════════════════════════════════════════════════════════════════
#  AUDIT LOG
# ══════════════════════════════════════════════════════════════════════════════

def load_audit_log() -> list:
    """Return the full audit log as a list of dicts."""
    _ensure_data_dir()
    if not os.path.exists(AUDIT_FILE):
        return []
    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def append_audit_entry(
    customer_name: str,
    agent_name:    str,
    action:        str,
    amount:        float,
    decision:      str,
    rule:          str,
    reason:        str,
) -> dict:
    """
    Add one entry to the permanent audit log.

    Parameters
    ----------
    customer_name : Customer who made the request.
    agent_name    : Agent that submitted the request.
    action        : Requested action (e.g. 'Book Flight').
    amount        : Amount in INR (0 for non-monetary actions).
    decision      : 'ALLOW', 'ASK CUSTOMER', or 'BLOCK'.
    rule          : Rule that fired (e.g. 'R4').
    reason        : Human-readable explanation.

    Returns
    -------
    dict  – The entry that was saved.
    """
    log = load_audit_log()
    entry = {
        "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "customer_name": customer_name.strip(),
        "agent_name":    agent_name.strip(),
        "action":        action,
        "amount_inr":    amount,
        "decision":      decision,
        "rule":          rule,
        "reason":        reason,
    }
    log.append(entry)
    _ensure_data_dir()
    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    return entry
