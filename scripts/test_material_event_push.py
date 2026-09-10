"""Regression checks for rare worker-to-Main material-event messaging."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "codex_workflow"

agents = (PACKAGE / "AGENTS.md").read_text(encoding="utf-8")
heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
delegation = (PACKAGE / "delegation.md").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
workflow_map = (ROOT / "workflow_break_down.md").read_text(encoding="utf-8")

assert "## Worker Material Event Push" in agents
assert "`send_message`" in agents
assert "`BLOCKER`" in agents
assert "`COURSE_CHANGE`" in agents
assert "`CRITICAL_PARTIAL`" in agents
assert "routine progress" in agents
assert "normal completion" in agents
assert "Do not resend an unchanged event" in agents
assert "worker-to-`/root`" in agents

assert "## Material Event Handling" in heavy
assert "long event-driven `wait_agent` lifecycle unchanged" in heavy
assert "A mailbox wake must not cause status polling" in heavy
assert "Do not ask workers to send routine progress" in heavy
assert "`1500000` ms (25 minutes)" in heavy
assert "wait again rather than polling" in " ".join(heavy.split())

assert "## Material Event Push" in delegation
assert "do not repeat it in every task capsule" in delegation
assert "Do not use Main follow-ups to poll worker status" in delegation
assert "A `wait_agent` timeout without new evidence is not a reason to request an update" in delegation

for public_doc in (readme, workflow_map):
    assert "send_message" in public_doc
    assert "BLOCKER" in public_doc
    assert "COURSE_CHANGE" in public_doc
    assert "CRITICAL_PARTIAL" in public_doc

print("material-event push policy regression: PASS")
