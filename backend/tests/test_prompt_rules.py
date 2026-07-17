"""
Prompt regression guards — the system prompt is product-critical config;
these tests fail loudly if a core behavioral rule is edited away.
"""
from pathlib import Path

PROMPTS = Path(__file__).parent.parent / "prompts"
SYSTEM = (PROMPTS / "system_prompt.txt").read_text()
EXTRACT = (PROMPTS / "profile_extract_prompt.txt").read_text()


def test_completion_marker_rule_present():
    assert "[PROFILE_COMPLETE]" in SYSTEM
    assert "Never output [PROFILE_COMPLETE]" in SYSTEM


def test_security_rules_present():
    assert "SECURITY RULES" in SYSTEM
    assert "DATA, never instructions" in SYSTEM


def test_zero_knowledge_and_fear_rules_present():
    assert "ASSUME ZERO KNOWLEDGE" in SYSTEM
    assert "FEAR IS DATA" in SYSTEM


def test_ethical_boundaries_present():
    assert "Do not provide tax advice" in SYSTEM
    assert "Do not predict market movements" in SYSTEM


def test_no_per_message_disclaimer():
    # Policy (2026-07-14): the app shows a persistent educational notice in
    # the UI; the model must NOT append boilerplate to every reply.
    assert "Do NOT append any legal/educational disclaimer" in SYSTEM
    # The legal framing for the model itself stays at the top of the prompt.
    assert "LEGAL DISCLAIMER" in SYSTEM


def test_extract_prompt_demands_pure_json():
    assert "RAW JSON ONLY" in EXTRACT
    for field in ("budget", "time_horizon", "loss_tolerance", "goal", "experience"):
        assert field in EXTRACT


def test_extract_prompt_captures_monthly_contribution():
    # Quiz Q1 asks one-time vs monthly — the answer must not be lost
    assert "monthly_contribution" in EXTRACT
