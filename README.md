# Qatar Airways – Agent Gatekeeper

**Student Enrolment Number:** PGD202571903  
**Project:** Agent Gatekeeper – Qatar Airways  
**Technology:** Python + Streamlit

---

## What This Application Does

The **Agent Gatekeeper** is an AI agent governance tool for Qatar Airways.  
It receives requests from customers' AI agents and decides whether to **ALLOW**, **ASK CUSTOMER**, or **BLOCK** the action — based on a clear set of business rules.

---

## Project Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit web application |
| `data_manager.py` | Handles all data saving and loading (agents, audit log) |
| `rules_engine.py` | Contains all 7 decision-making rules |
| `requirements.txt` | Python packages needed |
| `README.md` | This file |
| `data/` | Auto-created folder – stores agent and audit log data |

---

## How to Install and Run

### Step 1 – Make sure Python is installed
Open Command Prompt and type:
```
python --version
```
You should see something like `Python 3.10.x`. If not, download Python from https://python.org

### Step 2 – Open the project folder in Command Prompt
```
cd "c:\Users\anjal_4gsjure\OneDrive\Desktop\Qatar-Airways-Agent-Gatekeeper"
```

### Step 3 – Install required packages
```
pip install -r requirements.txt
```

### Step 4 – Run the application
```
streamlit run app.py
```

The app will open automatically in your web browser at `http://localhost:8501`

---

## Decision Rules

| Rule | Condition | Decision |
|------|-----------|----------|
| R1 | Agent is not registered | BLOCK |
| R2 | Registered agent – View Fares | ALLOW |
| R3 | Registered agent – View Booking | ALLOW |
| R4 | Registered + authorised – Book Flight ≤ ₹10,000 | ALLOW |
| R5 | Book Flight > ₹10,000 | ASK CUSTOMER |
| R6 | Change Flight or Refund | ASK CUSTOMER |
| R7 | Agent is revoked | BLOCK |

> **Priority:** Revocation check (R7) always runs first, before any other rule.

---

## Six Test Scenarios

| # | Scenario | Expected Decision |
|---|----------|------------------|
| 1 | Known agent views flight fares | ALLOW |
| 2 | Unknown agent attempts booking | BLOCK |
| 3 | Known agent books flight worth ₹15,000 | ASK CUSTOMER |
| 4 | Authorised agent books flight worth ₹8,000 | ALLOW |
| 5 | Revoked agent attempts booking | BLOCK |
| 6 | Known agent requests a refund | ASK CUSTOMER |

---

## How to Demonstrate to Your Professor

1. Start the app with `streamlit run app.py`
2. Go to **Register Agent** – register "Priya Sharma" with agent "PriyaBot" (with ₹10,000 authorisation)
3. Register "Rahul Mehta" with agent "RahulBot" (no spending authorisation)
4. Go to **Revoke Agent** – revoke "RahulBot"
5. Go to **Submit Request** – run all six test scenarios (a demo button is provided)
6. Go to **Audit History** – show the full log of all decisions
7. Go to **Dashboard** – show the summary statistics

---

## Support

This project was built for academic purposes as part of an MBA programme.  
Enrolment Number: **PGD202571903**
