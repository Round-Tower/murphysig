"""Tests for the shared provider plumbing (scripts/providers.py).

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: providers.py was extracted (behaviour-preserving) from
run_honesty_openai.py so the Honesty and TK cross-family runners share
ONE provider matrix. run_honesty_openai's tests already pin the
behaviour via re-export; these pin the new module's own public API
directly so a future edit to providers.py can't drift unnoticed.

Confidence: 0.85
"""

from __future__ import annotations

import pytest

from scripts.providers import (
    PROVIDERS,
    ProviderConfig,
    call_with_retries,
    create_completion,
    is_rate_limit,
    make_client,
    resolve_provider,
)


class TestPublicApi:
    def test_exports_are_callable(self):
        for fn in (resolve_provider, call_with_retries, is_rate_limit,
                   create_completion, make_client):
            assert callable(fn)
        assert "openrouter" in PROVIDERS

    def test_resolve_returns_config(self):
        cfg = resolve_provider("openrouter", {"OPEN_ROUTER_API_KEY": "or-test"})
        assert isinstance(cfg, ProviderConfig)
        assert cfg.api_key == "or-test"
        assert "openrouter.ai/api/v1" in cfg.base_url

    def test_missing_key_raises_with_var_name(self):
        with pytest.raises(SystemExit, match="OPEN_ROUTER_API_KEY"):
            resolve_provider("openrouter", {})


class TestRetry:
    def test_backs_off_on_rate_limit_then_succeeds(self):
        calls = {"n": 0}
        slept: list[float] = []

        def fn():
            calls["n"] += 1
            if calls["n"] < 3:
                raise Exception("429 rate limit")
            return "ok"

        out = call_with_retries(fn, retries=5, base_delay=1.0, sleep=slept.append)
        assert out == "ok"
        assert slept == [1.0, 2.0]

    def test_non_rate_limit_propagates(self):
        def fn():
            raise ValueError("400 bad")

        with pytest.raises(ValueError):
            call_with_retries(fn, retries=3, base_delay=0.0, sleep=lambda s: None)


class _FakeClient:
    """Records chat.completions.create kwargs and returns a stub."""

    def __init__(self):
        self.calls = []
        outer = self

        class _Completions:
            def create(self, **kwargs):
                outer.calls.append(kwargs)
                class _Msg:
                    content = "ok"
                class _Choice:
                    message = _Msg()
                    finish_reason = "stop"
                class _Resp:
                    choices = [_Choice()]
                return _Resp()

        class _Chat:
            completions = _Completions()

        self.chat = _Chat()


class TestMaxTokensOverride:
    """2026-08-22: gemini-3.5-flash and qwen3.7-plus became reasoning-by-
    default on OpenRouter — hidden reasoning ate the 2048 budget and
    truncated 147/600 author rows (finish_reason=length, some with ZERO
    visible chars). Subject calls need a raisable budget; the default
    stays 2048 so existing judge/TK behavior is untouched."""

    def test_default_budget_is_2048(self):
        client = _FakeClient()
        create_completion(client, "m", "p", 0.7)
        assert client.calls[0]["max_completion_tokens"] == 2048

    def test_explicit_budget_passes_through(self):
        client = _FakeClient()
        create_completion(client, "m", "p", 0.7, max_tokens=8192)
        assert client.calls[0]["max_completion_tokens"] == 8192
