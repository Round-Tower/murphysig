"""Tests for the multi-provider TK (tacit knowledge) briefing runner.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The TK cross-family runner mirrors run_honesty_openai.py but
for the briefing task. TK is DELTA-based — the same model briefs each
case twice (unsigned vs signed) and the headline is the within-model
difference — so the signature-rendering + variant logic is the part
worth pinning. These cover the pure logic; no API calls.

Confidence: 0.85
"""

from __future__ import annotations

from scripts.run_tk_openai import (
    apply_variant,
    build_briefing_prompt,
    format_signature_block,
    load_tk_fixtures,
)


class TestFormatSignatureBlock:
    def test_renders_murphysig_fields(self):
        sig = {
            "context": "Quick helper during a migration.",
            "confidence": 0.5,
            "open": "Does page > total_pages behave correctly?",
            "heuristic": "Standard pagination pattern, not validated",
        }
        block = format_signature_block(sig, today="2026-06-23")
        assert "Signed:" in block
        assert "2026-06-23" in block
        assert "MurphySig v0.4" in block
        assert "Context: Quick helper during a migration." in block
        assert "Confidence: 0.5" in block
        assert "Open: Does page > total_pages behave correctly?" in block
        assert "Heuristic: Standard pagination pattern, not validated" in block

    def test_heuristic_is_optional(self):
        sig = {"context": "ctx", "confidence": 0.9, "open": "q"}
        block = format_signature_block(sig, today="2026-06-23")
        assert "Heuristic:" not in block
        assert "Context: ctx" in block

    def test_uses_generic_author_not_a_real_name(self):
        # The signature must not bait fabrication — a generic author keeps
        # TK measuring *briefing uplift*, not provenance honesty.
        sig = {"context": "ctx", "confidence": 0.5, "open": "q"}
        block = format_signature_block(sig, today="2026-06-23")
        assert "Signed: Developer" in block


class TestApplyVariant:
    def _case(self):
        return {
            "id": "pagination",
            "code": "def paginate(): pass\n",
            "signature": {"context": "ctx", "confidence": 0.5, "open": "q"},
        }

    def test_unsigned_is_bare_code(self):
        out = apply_variant(self._case(), "unsigned", today="2026-06-23")
        assert out == "def paginate(): pass\n"
        assert "Signed:" not in out

    def test_signed_prepends_signature_block(self):
        out = apply_variant(self._case(), "signed", today="2026-06-23")
        assert "Signed:" in out
        assert "Context: ctx" in out
        # the original code still present, after the block
        assert out.rstrip().endswith("def paginate(): pass")
        assert out.index("Signed:") < out.index("def paginate")


class TestBuildBriefingPrompt:
    def test_embeds_code_into_template(self):
        template = "Brief this code:\n\n{code}"
        out = build_briefing_prompt(template, "def f(): pass\n")
        assert "Brief this code:" in out
        assert "def f(): pass" in out
        assert "{code}" not in out


class TestLoadFixtures:
    def test_loads_cases_and_briefing_template(self):
        cases, template = load_tk_fixtures()
        ids = {c["id"] for c in cases}
        assert {"pagination", "sql_injection", "god_method"} <= ids
        for c in cases:
            assert "code" in c
            assert "signature" in c
        assert "{code}" in template
