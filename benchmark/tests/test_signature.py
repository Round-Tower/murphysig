"""Tests for signature generator — written first per TDD."""

import pytest

from src.models import SignatureVariant, TestCase
from src.signature import apply_signature


@pytest.fixture
def sample_case() -> TestCase:
    return TestCase(
        id="test_case",
        name="Test Case",
        code="def hello():\n    return 'world'",
        expected_issues=["some issue"],
        has_bug=True,
        high_signature_context="battle-tested, production-proven",
        low_signature_context="sketchy, untested, first attempt",
    )


class TestApplySignatureNone:
    def test_returns_bare_code(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.NONE)
        assert result == sample_case.code

    def test_no_murphysig_marker(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.NONE)
        assert "MurphySig" not in result


class TestApplySignatureHigh:
    def test_contains_code(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.HIGH)
        assert "def hello():" in result

    def test_contains_murphysig_marker(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.HIGH)
        assert "MurphySig" in result

    def test_contains_high_confidence(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.HIGH)
        assert "0.9" in result

    def test_contains_context(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.HIGH)
        assert "battle-tested" in result

    def test_signature_is_python_comment(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.HIGH)
        sig_lines = [
            line for line in result.splitlines()
            if "MurphySig" in line or "Confidence" in line or "Context" in line
        ]
        assert all(line.strip().startswith("#") for line in sig_lines)


class TestApplySignatureLow:
    def test_contains_code(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.LOW)
        assert "def hello():" in result

    def test_contains_murphysig_marker(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.LOW)
        assert "MurphySig" in result

    def test_contains_low_confidence(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.LOW)
        assert "0.3" in result

    def test_contains_context(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.LOW)
        assert "sketchy" in result

    def test_signature_precedes_code(self, sample_case: TestCase):
        result = apply_signature(sample_case, SignatureVariant.LOW)
        sig_pos = result.index("MurphySig")
        code_pos = result.index("def hello():")
        assert sig_pos < code_pos


class TestApplySignatureSpecCompliance:
    """Assert the generator produces spec v0.3.3 compliant signatures.

    The spec requires:
      Signed: NAME, YYYY-MM-DD           (single line, date after name)
      Format: MurphySig vX.Y.Z (URL)      (spec URL for cross-model discovery)
      Confidence: VALUE - context         (honest uncertainty)
    """

    def test_has_signed_field(self, sample_case: TestCase):
        for variant in [SignatureVariant.HIGH, SignatureVariant.LOW]:
            result = apply_signature(sample_case, variant)
            assert "# Signed:" in result

    def test_date_on_signed_line(self, sample_case: TestCase):
        """Spec v0.3.3: date belongs on the Signed: line, not a separate # Date: line."""
        import re

        for variant in [SignatureVariant.HIGH, SignatureVariant.LOW]:
            result = apply_signature(sample_case, variant)
            signed_line = next(line for line in result.splitlines() if "# Signed:" in line)
            assert re.search(r"\d{4}-\d{2}-\d{2}", signed_line), (
                f"Date must appear on the Signed: line per spec v0.3.3, got: {signed_line!r}"
            )

    def test_has_confidence_field(self, sample_case: TestCase):
        for variant in [SignatureVariant.HIGH, SignatureVariant.LOW]:
            result = apply_signature(sample_case, variant)
            assert "# Confidence:" in result

    def test_has_format_line_with_spec_url(self, sample_case: TestCase):
        """Spec v0.3.3: signatures should link to the spec URL for cross-model discovery."""
        for variant in [SignatureVariant.HIGH, SignatureVariant.LOW]:
            result = apply_signature(sample_case, variant)
            assert "# Format: MurphySig v0.3.3" in result
            assert "https://murphysig.dev/spec" in result
