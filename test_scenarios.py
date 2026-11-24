"""
test_scenarios.py
-----------------
Runs all six test scenarios from the command line and prints results.
Run with:
    python test_scenarios.py
"""
import os
import data_manager as dm
import rules_engine  as re

# ── Clean slate for reproducible test ─────────────────────────────────────
os.makedirs("data", exist_ok=True)
open("data/agents.json",    "w").write("[]")
open("data/audit_log.json", "w").write("[]")

# ── Setup demo agents ──────────────────────────────────────────────────────
dm.register_agent("Priya Sharma", "PriyaBot", authorised=True)   # active + authorised
dm.register_agent("Rahul Mehta",  "RahulBot", authorised=False)  # will be revoked
dm.revoke_agent(  "Rahul Mehta",  "RahulBot")

SCENARIOS = [
    (1, "Known agent views flight fares",         "Priya Sharma", "PriyaBot", "View Fares",  0,     "ALLOW"),
    (2, "Unknown agent attempts booking",          "John Doe",     "GhostBot", "Book Flight", 8000,  "BLOCK"),
    (3, "Known agent books flight Rs 15,000",      "Priya Sharma", "PriyaBot", "Book Flight", 15000, "ASK CUSTOMER"),
    (4, "Authorised agent books Rs 8,000 flight",  "Priya Sharma", "PriyaBot", "Book Flight", 8000,  "ALLOW"),
    (5, "Revoked agent attempts booking",          "Rahul Mehta",  "RahulBot", "Book Flight", 5000,  "BLOCK"),
    (6, "Known agent requests a refund",           "Priya Sharma", "PriyaBot", "Refund",      8000,  "ASK CUSTOMER"),
]

print()
print("=" * 72)
print("  QATAR AIRWAYS AGENT GATEKEEPER  -  TEST RESULTS")
print("  Enrolment: PGD202571903")
print("=" * 72)

all_pass = True
for num, title, cust, agent, action, amount, expected in SCENARIOS:
    result = re.evaluate_request(cust, agent, action, float(amount), save_to_log=True)
    got    = result["decision"]
    rule   = result["rule"]
    reason = result["reason"]
    passed = got == expected
    if not passed:
        all_pass = False
    status = "PASS" if passed else "FAIL"
    print(f"  Scenario {num}: {status}")
    print(f"    Title    : {title}")
    print(f"    Expected : {expected}")
    print(f"    Got      : {got}  (Rule {rule})")
    short = reason[:80] + "..." if len(reason) > 80 else reason
    print(f"    Reason   : {short}")
    print()

print("=" * 72)
outcome = "ALL 6 SCENARIOS PASSED" if all_pass else "SOME SCENARIOS FAILED"
print(f"  OVERALL: {outcome}")
print("=" * 72)

log = dm.load_audit_log()
print(f"\n  Audit log entries saved: {len(log)}")
print()
