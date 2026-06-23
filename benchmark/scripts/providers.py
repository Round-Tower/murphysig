"""Shared provider plumbing for the cross-family benchmark runners.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file — extracted, behaviour-preserving, from
run_honesty_openai.py which was Signed: Kev + claude-opus-4-7, 2026-04-23)

Context: The Honesty cross-family runner grew the provider matrix
(base URL + key env per family), rate-limit backoff, and the
graceful chat-completions call (temperature / token-param fallbacks).
The TK cross-family runner needs the exact same plumbing. Extracting
it here keeps ONE provider matrix and stops the TK runner importing
from the Honesty runner (wrong-way coupling). run_honesty_openai.py
re-exports these names, so its existing tests
(tests/test_provider_runner.py) pin this behaviour unchanged — the
extraction is proven safe by the green suite.

Confidence: 0.85 — pure move; no logic changed. The OpenAI client
creation is factored into make_client() so both runners share it too.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

# OpenAI-compatible chat-completions endpoints. base_url None = OpenAI
# proper. OPENAI_BASE_URL in the environment overrides any preset
# (useful for proxies / local models).
PROVIDERS: dict[str, dict] = {
    "openai": {"base_url": None, "key_env": "OPENAI_API_KEY"},
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_env": "GEMINI_API_KEY",
    },
    "groq": {"base_url": "https://api.groq.com/openai/v1", "key_env": "GROQ_API_KEY"},
    "xai": {"base_url": "https://api.x.ai/v1", "key_env": "XAI_API_KEY"},
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "key_env": "DEEPSEEK_API_KEY"},
    "mistral": {"base_url": "https://api.mistral.ai/v1", "key_env": "MISTRAL_API_KEY"},
    "together": {"base_url": "https://api.together.xyz/v1", "key_env": "TOGETHER_API_KEY"},
    # One key, every family — Gemini/Llama/Grok/DeepSeek/Qwen/Mistral/GPT.
    # Model ids are namespaced ("google/gemini-2.5-pro", "meta-llama/...").
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPEN_ROUTER_API_KEY",
        "key_aliases": ["OPENROUTER_API_KEY"],
    },
}


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    base_url: str | None
    api_key: str


def resolve_provider(name: str, env: dict | os._Environ) -> ProviderConfig:
    """Resolve a provider preset + API key from the environment."""
    preset = PROVIDERS.get(name)
    if preset is None:
        raise SystemExit(f"unknown provider {name!r} — choose from {sorted(PROVIDERS)}")
    candidates = [preset["key_env"], *preset.get("key_aliases", [])]
    api_key = next((env[c] for c in candidates if env.get(c) and env[c] != "123"), "")
    if not api_key:
        raise SystemExit(
            f"{preset['key_env']} not set (or placeholder). Add it to benchmark/.env."
        )
    base_url = env.get("OPENAI_BASE_URL") or preset["base_url"]
    return ProviderConfig(name=name, base_url=base_url, api_key=api_key)


def make_client(cfg: ProviderConfig):
    """Construct an OpenAI client for a resolved provider config."""
    from openai import OpenAI

    if cfg.base_url:
        return OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)
    return OpenAI(api_key=cfg.api_key)


def is_rate_limit(err: Exception) -> bool:
    """True for a 429 / upstream rate-limit, across SDK error shapes."""
    msg = str(err).lower()
    return "429" in msg or "rate-limit" in msg or "rate limit" in msg or "ratelimit" in msg


def call_with_retries(fn, *, retries: int, base_delay: float, sleep=time.sleep):
    """Call fn(); on a rate-limit error, back off exponentially and retry.
    Non-rate-limit errors propagate immediately. sleep is injectable for
    tests."""
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 — provider SDKs vary
            if not is_rate_limit(e) or attempt == retries:
                raise
            sleep(base_delay * (2**attempt))
    raise AssertionError("unreachable")  # pragma: no cover


def create_completion(client, model: str, prompt: str, temperature: float):
    """Chat-completions call with graceful fallbacks:
    - GPT-5-family reasoning models reject explicit temperature;
    - older/compat providers reject max_completion_tokens (want max_tokens);
    - upstream 429s (free-tier bursts) are retried with backoff.
    """
    base = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    last_err: Exception | None = None
    for tok_param in ("max_completion_tokens", "max_tokens"):
        kwargs = {**base, tok_param: 2048}
        for with_temp in (True, False):
            def _do(wt=with_temp, kw=kwargs):
                if wt:
                    return client.chat.completions.create(temperature=temperature, **kw)
                return client.chat.completions.create(**kw)

            try:
                return call_with_retries(_do, retries=5, base_delay=2.0)
            except Exception as e:  # noqa: BLE001 — provider SDKs vary
                last_err = e
                msg = str(e)
                if with_temp and "temperature" in msg:
                    continue  # retry same token param without temperature
                if "max_completion_tokens" in msg or "max_tokens" in msg:
                    break  # try the other token param
                raise
    raise last_err  # both param spellings rejected
