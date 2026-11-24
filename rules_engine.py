"""
rules_engine.py
---------------
Implements the seven decision-making rules for the Agent Gatekeeper.

Each public function takes the relevant inputs and returns a dict:
  {
    "decision": "ALLOW" | "ASK CUSTOMER" | "BLOCK",
    "rule":     "R1" ... "R7",
    "reason":   "<human-readable explanation>",
  }

The main entry point is  evaluate_request().
"""

from data_manager import get_agent, append_audit_entry

# Actions that always require customer confirmation (R6)
CONFIRMATION_ACTIONS = {"Change Flight", "Refund"}

# Actions that are purely informational (R2, R3)
VIEW_ACTIONS = {"View Fares", "View Booking"}

# Maximum amount an authorised agent can transact automatically (R4)
SPENDING_LIMIT = 10_000.0


def evaluate_request(
    customer_name: str,
    agent_name:    str,
    action:        str,
    amount:        float,
    save_to_log:   bool = True,
) -> dict:
    """
    Apply all seven rules in priority order and return the gatekeeper decision.

    Priority order
    --------------
    1. R7 – Revoked agent check   (always first)
    2. R1 – Unknown agent check
    3. R2 – View Fares
    4. R3 – View Booking
    5. R6 – Change / Refund
    6. R4 – Authorised booking ≤ ₹10,000
    7. R5 – Booking > ₹10,000

    Parameters
    ----------
    customer_name : Name of the customer submitting the request.
    agent_name    : Name of the agent acting on behalf of the customer.
    action        : One of the five supported actions.
    amount        : Amount in INR (use 0 for non-monetary actions).
    save_to_log   : If True, the result is written to the audit log.

    Returns
    -------
    dict with keys: decision, rule, reason
    """

    agent = get_agent(customer_name, agent_name)

    # ── R7: Revoked agent – always block first ─────────────────────────────
    if agent and agent["status"] == "revoked":
        result = _make_result(
            "BLOCK", "R7",
            f"Agent '{agent_name}' was revoked on {agent['revoked_at']} "
            f"and is permanently blocked from all actions."
        )

    # ── R1: Unknown / unregistered agent ──────────────────────────────────
    elif agent is None:
        result = _make_result(
            "BLOCK", "R1",
            f"Agent '{agent_name}' is not registered for customer '{customer_name}'. "
            f"Unknown agents are blocked from all actions."
        )

    # ── R2: View Fares ─────────────────────────────────────────────────────
    elif action == "View Fares":
        result = _make_result(
            "ALLOW", "R2",
            f"Registered agent '{agent_name}' is allowed to view flight fares. "
            f"This is a read-only, non-monetary action."
        )

    # ── R3: View Booking ───────────────────────────────────────────────────
    elif action == "View Booking":
        result = _make_result(
            "ALLOW", "R3",
            f"Registered agent '{agent_name}' is allowed to view booking details. "
            f"This is a read-only, non-monetary action."
        )

    # ── R6: Change Flight or Refund ────────────────────────────────────────
    elif action in CONFIRMATION_ACTIONS:
        result = _make_result(
            "ASK CUSTOMER", "R6",
            f"The action '{action}' requires explicit customer confirmation "
            f"before it can be executed. Please contact {customer_name} to approve."
        )

    # ── R4 / R5: Book Flight ───────────────────────────────────────────────
    elif action == "Book Flight":
        if agent["authorised"] and amount <= SPENDING_LIMIT:
            result = _make_result(
                "ALLOW", "R4",
                f"Agent '{agent_name}' is registered and authorised to spend up to "
                f"₹{SPENDING_LIMIT:,.0f}. The requested amount ₹{amount:,.0f} is within the limit."
            )
        elif amount > SPENDING_LIMIT:
            result = _make_result(
                "ASK CUSTOMER", "R5",
                f"The booking amount ₹{amount:,.0f} exceeds the ₹{SPENDING_LIMIT:,.0f} limit. "
                f"Customer confirmation from {customer_name} is required before proceeding."
            )
        else:
            # Registered but NOT authorised, amount within limit
            result = _make_result(
                "ASK CUSTOMER", "R5",
                f"Agent '{agent_name}' is registered but has NOT been authorised with a "
                f"spending limit. Customer confirmation is required for any booking."
            )

    else:
        # Fallback – should not normally be reached
        result = _make_result(
            "BLOCK", "R1",
            f"Unrecognised action '{action}'. Request blocked as a safety measure."
        )

    # ── Save to audit log ─────────────────────────────────────────────────
    if save_to_log:
        append_audit_entry(
            customer_name = customer_name,
            agent_name    = agent_name,
            action        = action,
            amount        = amount,
            decision      = result["decision"],
            rule          = result["rule"],
            reason        = result["reason"],
        )

    return result


def _make_result(decision: str, rule: str, reason: str) -> dict:
    """Helper to build a consistent result dictionary."""
    return {"decision": decision, "rule": rule, "reason": reason}
