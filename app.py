"""
app.py
------
Main Streamlit web application for the Qatar Airways Agent Gatekeeper.

Sections:
  1. Dashboard       – Summary statistics and quick overview
  2. Register Agent  – Register a new AI agent for a customer
  3. Revoke Agent    – Revoke an existing active agent
  4. Submit Request  – Submit an action request for evaluation
  5. Audit History   – Browse the full audit log
  6. Registered Agents – View all agents (active and revoked)

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime

import data_manager as dm
import rules_engine  as re_engine

# ── Page configuration (must be first Streamlit call) ─────────────────────────
st.set_page_config(
    page_title  = "Agent Gatekeeper – Qatar Airways",
    page_icon   = "✈️",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  STYLES  –  Qatar Airways brand colours
#  Primary burgundy : #8B0033   (Qatar Airways maroon)
#  Accent gold      : #C8963E
#  Light grey bg    : #F5F5F5
#  White card       : #FFFFFF
# ══════════════════════════════════════════════════════════════════════════════
STYLE = """
<style>
/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #F5F5F5;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #6B0028 0%, #8B0033 60%, #A80040 100%);
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 15px !important;
    padding: 4px 0 !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.3) !important;
}

/* ── Main header banner ── */
.qa-header {
    background: linear-gradient(135deg, #6B0028 0%, #8B0033 70%, #A80040 100%);
    padding: 28px 36px 20px 36px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 4px 18px rgba(139,0,51,0.25);
}
.qa-header h1 {
    color: #FFFFFF;
    font-size: 2.0rem;
    font-weight: 700;
    margin: 0 0 4px 0;
    letter-spacing: 0.5px;
}
.qa-header h3 {
    color: #F0C070;
    font-size: 1.1rem;
    font-weight: 400;
    margin: 0 0 2px 0;
}
.qa-header p {
    color: rgba(255,255,255,0.75);
    font-size: 0.85rem;
    margin: 0;
}

/* ── Section title ── */
.section-title {
    color: #8B0033;
    font-size: 1.5rem;
    font-weight: 700;
    border-left: 5px solid #8B0033;
    padding-left: 12px;
    margin-bottom: 18px;
    margin-top: 8px;
}

/* ── Cards ── */
.card {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 20px 24px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    margin-bottom: 16px;
}

/* ── Metric tiles ── */
.metric-tile {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 20px 16px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    border-top: 4px solid #8B0033;
}
.metric-tile .metric-value {
    font-size: 2.4rem;
    font-weight: 700;
    color: #8B0033;
}
.metric-tile .metric-label {
    font-size: 0.85rem;
    color: #666;
    margin-top: 4px;
}

/* ── Decision badges ── */
.badge-allow {
    background: #1A7F3C; color: white;
    padding: 4px 14px; border-radius: 20px;
    font-weight: 600; font-size: 0.85rem; display: inline-block;
}
.badge-ask {
    background: #C8963E; color: white;
    padding: 4px 14px; border-radius: 20px;
    font-weight: 600; font-size: 0.85rem; display: inline-block;
}
.badge-block {
    background: #C0392B; color: white;
    padding: 4px 14px; border-radius: 20px;
    font-weight: 600; font-size: 0.85rem; display: inline-block;
}

/* ── Result banner ── */
.result-allow  { background:#E8F5E9; border-left:6px solid #1A7F3C;
                 padding:16px 20px; border-radius:8px; margin-top:16px; }
.result-ask    { background:#FFF8E1; border-left:6px solid #C8963E;
                 padding:16px 20px; border-radius:8px; margin-top:16px; }
.result-block  { background:#FDECEA; border-left:6px solid #C0392B;
                 padding:16px 20px; border-radius:8px; margin-top:16px; }

/* ── Status pills ── */
.pill-active  { background:#E8F5E9; color:#1A7F3C;
                padding:2px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }
.pill-revoked { background:#FDECEA; color:#C0392B;
                padding:2px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }

/* ── Info box ── */
.info-box {
    background: #EEF4FF;
    border: 1px solid #BBCFFF;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 16px;
    font-size: 0.9rem;
    color: #2C3E70;
}

/* ── Buttons ── */
.stButton > button {
    background: #8B0033 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 8px 24px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: background 0.2s ease !important;
}
.stButton > button:hover {
    background: #6B0028 !important;
}

/* ── Divider ── */
hr { border-color: #E0E0E0 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def header_banner():
    st.markdown("""
    <div class="qa-header">
        <h1>✈️ &nbsp; Agent Gatekeeper – Qatar Airways</h1>
        <h3>AI Agent Request Governance System</h3>
        <p>Student Enrolment Number: PGD202571903 &nbsp;|&nbsp; MBA Academic Project</p>
    </div>
    """, unsafe_allow_html=True)


def decision_color(decision: str) -> str:
    return {"ALLOW": "🟢", "ASK CUSTOMER": "🟡", "BLOCK": "🔴"}.get(decision, "⚪")


def render_decision_result(result: dict, action: str, amount: float):
    """Render a coloured result card after request evaluation."""
    d   = result["decision"]
    cls = {"ALLOW": "result-allow", "ASK CUSTOMER": "result-ask", "BLOCK": "result-block"}[d]
    emoji = decision_color(d)

    amount_str = f"₹{amount:,.0f}" if amount > 0 else "N/A"

    st.markdown(f"""
    <div class="{cls}">
        <h3 style="margin:0 0 8px 0">{emoji} &nbsp; {d}</h3>
        <p style="margin:0"><strong>Rule Applied:</strong> {result['rule']}</p>
        <p style="margin:4px 0"><strong>Action:</strong> {action} &nbsp;|&nbsp;
           <strong>Amount:</strong> {amount_str}</p>
        <p style="margin:4px 0 0 0"><strong>Reason:</strong> {result['reason']}</p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR  –  Navigation
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ✈️ Qatar Airways")
    st.markdown("### Agent Gatekeeper")
    st.markdown("---")
    page = st.radio(
        "Navigate to:",
        ["🏠 Dashboard",
         "📋 Register Agent",
         "🚫 Revoke Agent",
         "📨 Submit Request",
         "📜 Audit History",
         "👥 Registered Agents"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**Enrolment:** PGD202571903")
    st.markdown("**Project:** Agent Gatekeeper")
    st.markdown(f"**Date:** {datetime.now().strftime('%d %b %Y')}")


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
header_banner()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown('<div class="section-title">Dashboard Overview</div>', unsafe_allow_html=True)

    agents    = dm.load_agents()
    active    = [a for a in agents if a["status"] == "active"]
    revoked   = [a for a in agents if a["status"] == "revoked"]
    log       = dm.load_audit_log()
    allows    = [e for e in log if e["decision"] == "ALLOW"]
    asks      = [e for e in log if e["decision"] == "ASK CUSTOMER"]
    blocks    = [e for e in log if e["decision"] == "BLOCK"]

    # ── Metric tiles ──────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-value">{len(active)}</div>
            <div class="metric-label">Active Agents</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-tile" style="border-top-color:#C0392B">
            <div class="metric-value" style="color:#C0392B">{len(revoked)}</div>
            <div class="metric-label">Revoked Agents</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-tile" style="border-top-color:#1A7F3C">
            <div class="metric-value" style="color:#1A7F3C">{len(allows)}</div>
            <div class="metric-label">Requests Allowed</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-tile" style="border-top-color:#C8963E">
            <div class="metric-value" style="color:#C8963E">{len(asks)}</div>
            <div class="metric-label">Awaiting Customer</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="metric-tile" style="border-top-color:#C0392B">
            <div class="metric-value" style="color:#C0392B">{len(blocks)}</div>
            <div class="metric-label">Requests Blocked</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Rules Reference ───────────────────────────────────────────────────
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📌 Decision Rules Reference")
        rules_data = {
            "Rule": ["R1", "R2", "R3", "R4", "R5", "R6", "R7"],
            "Condition": [
                "Agent not registered",
                "Registered → View Fares",
                "Registered → View Booking",
                "Authorised → Book ≤ ₹10,000",
                "Book Flight > ₹10,000",
                "Change Flight / Refund",
                "Agent is revoked",
            ],
            "Decision": ["BLOCK", "ALLOW", "ALLOW", "ALLOW", "ASK CUSTOMER", "ASK CUSTOMER", "BLOCK"],
        }
        df_rules = pd.DataFrame(rules_data)
        st.dataframe(df_rules, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📋 Recent Audit Entries")
        if log:
            recent = log[-5:][::-1]
            for entry in recent:
                d = entry["decision"]
                emoji = decision_color(d)
                st.markdown(
                    f"{emoji} **{entry['action']}** by *{entry['agent_name']}* "
                    f"→ **{d}** ({entry['rule']})"
                )
        else:
            st.info("No requests evaluated yet. Submit a request to see results here.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Quick start guide ─────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### 🚀 Quick Start Guide")
    st.markdown("""
1. **Register Agent** → Add a customer and their AI agent (with or without spending authorisation).
2. **Submit Request** → Choose the customer, agent, action and amount – the system will decide automatically.
3. **Audit History** → View every decision with the rule applied and the reason.
4. **Revoke Agent** → Permanently block an agent from future actions.
5. **Run Test Scenarios** → Use the demo button in *Submit Request* to run all 6 test cases at once.
    """)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: REGISTER AGENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Register Agent":
    st.markdown('<div class="section-title">Register a New AI Agent</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    📌 <strong>What is agent registration?</strong><br>
    When a customer wants an AI agent to act on their behalf (e.g., view fares, book flights),
    the agent must first be <strong>registered</strong> here.
    You can optionally authorise the agent to spend up to <strong>₹10,000</strong> without asking the customer each time.
    </div>
    """, unsafe_allow_html=True)

    with st.form("registration_form", clear_on_submit=True):
        st.markdown("#### Enter Registration Details")
        col1, col2 = st.columns(2)

        with col1:
            cust_name  = st.text_input("Customer Full Name *", placeholder="e.g. Priya Sharma", key="reg_customer_name")
        with col2:
            agent_name = st.text_input("Agent Name *",         placeholder="e.g. PriyaBot",     key="reg_agent_name")

        authorised = st.checkbox(
            "✅ Authorise this agent to spend up to ₹10,000 on the customer's behalf",
            value=False,
        )

        st.markdown(f"""
        <div style="font-size:0.82rem; color:#666; margin-top:4px;">
        Registration timestamp will be recorded automatically:
        <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong>
        </div>
        """, unsafe_allow_html=True)

        submitted = st.form_submit_button("Register Agent ✈️")

        if submitted:
            if not cust_name.strip() or not agent_name.strip():
                st.error("❌ Both Customer Name and Agent Name are required.")
            else:
                result = dm.register_agent(cust_name, agent_name, authorised)
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    auth_text = "✅ Authorised (₹10,000 limit)" if authorised else "❌ Not authorised"
                    st.success(f"""
✅ **Agent successfully registered!**

| Field | Value |
|-------|-------|
| Customer Name | {result['customer_name']} |
| Agent Name | {result['agent_name']} |
| Spending Authorisation | {auth_text} |
| Registered At | {result['registered_at']} |
| Status | Active |
                    """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: REVOKE AGENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🚫 Revoke Agent":
    st.markdown('<div class="section-title">Revoke an AI Agent</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    ⚠️ <strong>Important:</strong> Revoking an agent is <strong>permanent</strong>.
    Once revoked, the agent will be <strong>blocked from all actions</strong> (Rule R7).
    To use the same agent again, it must be freshly registered and re-authorised.
    </div>
    """, unsafe_allow_html=True)

    active_agents = dm.get_active_agents()

    if not active_agents:
        st.warning("⚠️ There are no active agents to revoke. Register an agent first.")
    else:
        agent_labels = [
            f"{a['customer_name']} → {a['agent_name']} (Registered: {a['registered_at']})"
            for a in active_agents
        ]

        # Dropdown outside a form so details update immediately
        selected_label = st.selectbox(
            "Choose an active agent:",
            agent_labels,
            key="revoke_agent_select"
        )

        idx = agent_labels.index(selected_label)
        chosen = active_agents[idx]

        # Display details of the currently selected agent
        st.markdown(f"""
        <div style="background:#FFF8E1; border:1px solid #C8963E; border-radius:8px;
                    padding:12px 16px; margin:12px 0; font-size:0.9rem;">
        <strong>Selected Agent:</strong> {chosen['agent_name']}<br>
        <strong>Customer:</strong> {chosen['customer_name']}<br>
        <strong>Authorised:</strong> {'Yes' if chosen['authorised'] else 'No'}<br>
        <strong>Registered At:</strong> {chosen['registered_at']}
        </div>
        """, unsafe_allow_html=True)

        confirm = st.checkbox(
            "I confirm I want to revoke this agent permanently.",
            key="revoke_agent_confirm"
        )

        if st.button("Revoke Agent 🚫", key="revoke_agent_button"):
            if not confirm:
                st.error("❌ Please tick the confirmation checkbox before revoking.")
            else:
                result = dm.revoke_agent(
                    chosen["customer_name"],
                    chosen["agent_name"]
                )

                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    a = result["agent"]
                    st.success(f"""
                    ✅ **Agent successfully revoked.**

                    **Agent Name:** {a['agent_name']}  
                    **Customer:** {a['customer_name']}  
                    **Revoked At:** {a['revoked_at']}  
                    **Status:** 🔴 Revoked

                    This agent will now be blocked from future actions (Rule R7).
                    """)

    # Display previously revoked agents
    revoked_agents = dm.get_revoked_agents()

    if revoked_agents:
        st.markdown("---")
        st.markdown("#### 🔴 Previously Revoked Agents")

        df_rev = pd.DataFrame(revoked_agents)[
            ["customer_name", "agent_name", "registered_at", "revoked_at"]
        ]

        df_rev.columns = ["Customer", "Agent", "Registered At", "Revoked At"]
        st.dataframe(df_rev, hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: SUBMIT REQUEST
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📨 Submit Request":
    st.markdown('<div class="section-title">Submit an Agent Request</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    📨 <strong>How this works:</strong> Fill in the form below with the customer name, agent name,
    the action the agent wants to perform, and the amount (if applicable).
    The <strong>Gatekeeper</strong> will evaluate the request against the seven rules and
    return a decision: <strong>ALLOW</strong>, <strong>ASK CUSTOMER</strong>, or <strong>BLOCK</strong>.
    </div>
    """, unsafe_allow_html=True)

    ACTIONS = ["View Fares", "View Booking", "Book Flight", "Change Flight", "Refund"]

    with st.form("request_form"):
        st.markdown("#### Request Details")
        col1, col2 = st.columns(2)
        with col1:
            req_customer = st.text_input("Customer Name *", placeholder="e.g. Priya Sharma")
        with col2:
            req_agent    = st.text_input("Agent Name *",    placeholder="e.g. PriyaBot")

        col3, col4 = st.columns(2)
        with col3:
            req_action = st.selectbox("Requested Action *", ACTIONS)
        with col4:
            req_amount = st.number_input(
                "Amount (₹ INR)",
                min_value=0.0, step=500.0, value=0.0,
                help="Enter 0 for non-monetary actions like View Fares or View Booking."
            )

        submitted = st.form_submit_button("🔍 Evaluate Request")

        if submitted:
            if not req_customer.strip() or not req_agent.strip():
                st.error("❌ Customer Name and Agent Name are required.")
            else:
                result = re_engine.evaluate_request(
                    customer_name = req_customer,
                    agent_name    = req_agent,
                    action        = req_action,
                    amount        = req_amount,
                    save_to_log   = True,
                )
                render_decision_result(result, req_action, req_amount)

                if result["decision"] == "ASK CUSTOMER":
                    st.markdown("""
                    <div style="background:#FFF3E0; border:1px solid #E65100;
                                border-radius:8px; padding:12px 16px; margin-top:12px;">
                    ⚠️ <strong>Action Required:</strong> This request is pending customer approval.
                    The agent must <strong>NOT</strong> execute this action until the customer explicitly confirms.
                    Please contact the customer and obtain written or verbal approval before proceeding.
                    </div>
                    """, unsafe_allow_html=True)

    # ── Demo: Run all 6 test scenarios ────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🧪 Run All Six Test Scenarios")
    st.markdown("""
    Click the button below to automatically run all six test scenarios and log the results.
    This is useful for demonstrating the system to your professor.
    """)

    if st.button("▶️ Run All 6 Test Scenarios"):
        # First, set up demo agents if they don't exist
        # Scenario agents: PriyaBot (authorised), RahulBot (revoked), SunilBot (not authorised)
        setup_log = []

        # Ensure PriyaBot is registered and authorised
        existing = dm.get_agent("Priya Sharma", "PriyaBot")
        if existing is None:
            dm.register_agent("Priya Sharma", "PriyaBot", authorised=True)
            setup_log.append("✅ Registered **PriyaBot** for Priya Sharma (authorised)")
        elif existing["status"] == "revoked":
            dm.register_agent("Priya Sharma", "PriyaBot_v2", authorised=True)
            setup_log.append("✅ Registered **PriyaBot_v2** for Priya Sharma (authorised)")

        # Ensure RahulBot is registered and then revoked
        rahul = dm.get_agent("Rahul Mehta", "RahulBot")
        if rahul is None:
            dm.register_agent("Rahul Mehta", "RahulBot", authorised=False)
            dm.revoke_agent("Rahul Mehta", "RahulBot")
            setup_log.append("✅ Registered then revoked **RahulBot** for Rahul Mehta")
        elif rahul["status"] == "active":
            dm.revoke_agent("Rahul Mehta", "RahulBot")
            setup_log.append("✅ Revoked **RahulBot** for Rahul Mehta")

        if setup_log:
            with st.expander("📋 Demo Setup (agents created automatically)"):
                for msg in setup_log:
                    st.markdown(msg)

        # Determine which PriyaBot name to use
        priya_agent = "PriyaBot" if dm.get_agent("Priya Sharma", "PriyaBot") and \
                      dm.get_agent("Priya Sharma", "PriyaBot")["status"] == "active" else "PriyaBot_v2"

        SCENARIOS = [
            {
                "num":      1,
                "title":    "Known agent views flight fares",
                "customer": "Priya Sharma",
                "agent":    priya_agent,
                "action":   "View Fares",
                "amount":   0,
                "expected": "ALLOW",
            },
            {
                "num":      2,
                "title":    "Unknown agent attempts a booking",
                "customer": "John Doe",
                "agent":    "GhostBot",
                "action":   "Book Flight",
                "amount":   8000,
                "expected": "BLOCK",
            },
            {
                "num":      3,
                "title":    "Known agent books a flight worth ₹15,000",
                "customer": "Priya Sharma",
                "agent":    priya_agent,
                "action":   "Book Flight",
                "amount":   15000,
                "expected": "ASK CUSTOMER",
            },
            {
                "num":      4,
                "title":    "Authorised agent books a flight worth ₹8,000",
                "customer": "Priya Sharma",
                "agent":    priya_agent,
                "action":   "Book Flight",
                "amount":   8000,
                "expected": "ALLOW",
            },
            {
                "num":      5,
                "title":    "Revoked agent attempts a booking",
                "customer": "Rahul Mehta",
                "agent":    "RahulBot",
                "action":   "Book Flight",
                "amount":   5000,
                "expected": "BLOCK",
            },
            {
                "num":      6,
                "title":    "Known agent requests a refund",
                "customer": "Priya Sharma",
                "agent":    priya_agent,
                "action":   "Refund",
                "amount":   8000,
                "expected": "ASK CUSTOMER",
            },
        ]

        st.markdown("### 📊 Test Results")
        all_pass = True

        for sc in SCENARIOS:
            result = re_engine.evaluate_request(
                customer_name = sc["customer"],
                agent_name    = sc["agent"],
                action        = sc["action"],
                amount        = sc["amount"],
                save_to_log   = True,
            )

            d        = result["decision"]
            expected = sc["expected"]
            passed   = d == expected
            if not passed:
                all_pass = False

            status_icon = "✅ PASS" if passed else "❌ FAIL"
            d_emoji     = decision_color(d)

            with st.expander(
                f"Scenario {sc['num']}: {sc['title']}  |  "
                f"{d_emoji} {d}  |  {status_icon}"
            ):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Customer:** {sc['customer']}")
                    st.markdown(f"**Agent:** {sc['agent']}")
                    st.markdown(f"**Action:** {sc['action']}")
                    st.markdown(f"**Amount:** ₹{sc['amount']:,}" if sc['amount'] else "**Amount:** N/A")
                with col_b:
                    st.markdown(f"**Expected:** {expected}")
                    st.markdown(f"**Got:** {d}")
                    st.markdown(f"**Rule:** {result['rule']}")
                    st.markdown(f"**Result:** {status_icon}")
                st.markdown(f"**Reason:** {result['reason']}")

        st.markdown("---")
        if all_pass:
            st.success("🎉 All 6 scenarios passed! The Gatekeeper is working correctly.")
        else:
            st.error("❌ One or more scenarios did not match the expected outcome. Check above.")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: AUDIT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📜 Audit History":
    st.markdown('<div class="section-title">Audit Log</div>', unsafe_allow_html=True)

    log = dm.load_audit_log()

    if not log:
        st.info("📭 No audit entries yet. Submit a request to see the log here.")
    else:
        df_log = pd.DataFrame(log)
        df_log.columns = [
            "Timestamp", "Customer", "Agent", "Action",
            "Amount (₹)", "Decision", "Rule", "Reason"
        ]

        # ── Filter controls ───────────────────────────────────────────────
        st.markdown("#### 🔎 Filter")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filter_decision = st.multiselect(
                "Filter by Decision:",
                ["ALLOW", "ASK CUSTOMER", "BLOCK"],
                default=["ALLOW", "ASK CUSTOMER", "BLOCK"],
            )
        with fc2:
            filter_action = st.multiselect(
                "Filter by Action:",
                sorted(df_log["Action"].unique().tolist()),
                default=sorted(df_log["Action"].unique().tolist()),
            )
        with fc3:
            filter_customer = st.multiselect(
                "Filter by Customer:",
                sorted(df_log["Customer"].unique().tolist()),
                default=sorted(df_log["Customer"].unique().tolist()),
            )

        filtered = df_log[
            df_log["Decision"].isin(filter_decision) &
            df_log["Action"].isin(filter_action) &
            df_log["Customer"].isin(filter_customer)
        ]

        st.markdown(f"**Showing {len(filtered)} of {len(df_log)} entries**")
        st.dataframe(filtered[::-1].reset_index(drop=True), hide_index=True, use_container_width=True)

        # ── Summary ───────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("#### 📊 Decision Summary")
        summary = df_log["Decision"].value_counts().reset_index()
        summary.columns = ["Decision", "Count"]
        sc1, sc2 = st.columns([1, 2])
        with sc1:
            st.dataframe(summary, hide_index=True, use_container_width=True)
        with sc2:
            # Simple bar using st.bar_chart
            chart_data = summary.set_index("Decision")
            st.bar_chart(chart_data, color="#8B0033")

        # ── Download ──────────────────────────────────────────────────────
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label     = "⬇️ Download Audit Log (CSV)",
            data      = csv,
            file_name = "qatar_gatekeeper_audit.csv",
            mime      = "text/csv",
        )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: REGISTERED AGENTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Registered Agents":
    st.markdown('<div class="section-title">Registered Agents</div>', unsafe_allow_html=True)

    agents = dm.load_agents()

    if not agents:
        st.info("📭 No agents registered yet. Go to **Register Agent** to add one.")
    else:
        active_list  = [a for a in agents if a["status"] == "active"]
        revoked_list = [a for a in agents if a["status"] == "revoked"]

        # ── Active Agents ─────────────────────────────────────────────────
        st.markdown(f"### 🟢 Active Agents  ({len(active_list)})")
        if active_list:
            df_active = pd.DataFrame(active_list)[[
                "customer_name", "agent_name", "authorised", "registered_at"
            ]].copy()
            df_active["authorised"] = df_active["authorised"].map(
                {True: "✅ Yes (₹10,000)", False: "❌ No"}
            )
            df_active.columns = ["Customer", "Agent", "Authorised", "Registered At"]
            st.dataframe(df_active, hide_index=True, use_container_width=True)
        else:
            st.info("No active agents.")

        # ── Revoked Agents ────────────────────────────────────────────────
        st.markdown(f"### 🔴 Revoked Agents  ({len(revoked_list)})")
        if revoked_list:
            df_revoked = pd.DataFrame(revoked_list)[[
                "customer_name", "agent_name", "authorised", "registered_at", "revoked_at"
            ]].copy()
            df_revoked["authorised"] = df_revoked["authorised"].map(
                {True: "Yes", False: "No"}
            )
            df_revoked.columns = ["Customer", "Agent", "Was Authorised", "Registered At", "Revoked At"]
            st.dataframe(df_revoked, hide_index=True, use_container_width=True)
        else:
            st.info("No revoked agents.")

        # ── Summary ───────────────────────────────────────────────────────
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Agents",   len(agents))
        m2.metric("Active Agents",  len(active_list))
        m3.metric("Revoked Agents", len(revoked_list))
