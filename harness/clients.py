"""Free-tier model clients (Groq, OpenRouter :free models only).

Keys come from the environment (GROQ_API_KEY, OPENROUTER_API_KEY), loaded from
a private env file outside this repo. Keys are never logged or written.
"""
import os
import time

import httpx

ENDPOINTS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
}
KEY_VARS = {"groq": "GROQ_API_KEY", "openrouter": "OPENROUTER_API_KEY"}


def _check_free(provider, model):
    if provider == "openrouter" and not model.endswith(":free"):
        raise ValueError("OpenRouter models must be :free variants")
    if provider not in ENDPOINTS:
        raise ValueError(f"unknown provider {provider}")


def _retry_wait(response, delay):
    """Prefer Retry-After when it is a plain delay in seconds, capped at 60s."""
    raw = response.headers.get("Retry-After") or response.headers.get("retry-after")
    if raw:
        try:
            return min(max(float(raw), delay), 60.0)
        except ValueError:
            pass
    return delay


def call_model(provider, model, messages, temperature=0.0, max_tokens=2048, retries=6, reasoning_effort=None):
    _check_free(provider, model)
    key = os.environ.get(KEY_VARS[provider])
    if not key:
        raise RuntimeError(f"{KEY_VARS[provider]} not set")
    headers = {"Authorization": f"Bearer {key}"}
    if provider == "openrouter":
        # Optional identifying headers; no secrets.
        headers["HTTP-Referer"] = "https://github.com/dgarcia-lokolys/apart-epistemics-sprint"
        headers["X-Title"] = "ClaimStanceBench"
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    delay = 5.0
    last_err = "retries exhausted"
    for attempt in range(retries + 1):
        r = httpx.post(ENDPOINTS[provider], headers=headers, json=body, timeout=180)
        if r.status_code == 429 and attempt < retries:
            wait = _retry_wait(r, delay)
            time.sleep(wait)
            delay = max(delay * 2, wait)
            continue
        if r.status_code != 200:
            # Error text only; never include headers or the key.
            last_err = f"{provider} {model} HTTP {r.status_code}: {r.text[:300]}"
            if r.status_code >= 500 and attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError(last_err)
        data = r.json()
        if data.get("error"):
            err = data["error"]
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            raise RuntimeError(f"{provider} {model} API error: {msg[:300]}")
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"{provider} {model} empty choices")
        choice = choices[0]
        msg = choice.get("message") or {}
        content = msg.get("content") or ""
        # Reasoning, if present, is stored separately and is not scored.
        reasoning = msg.get("reasoning") or msg.get("reasoning_content") or ""
        finish = choice.get("finish_reason") or choice.get("native_finish_reason") or ""
        usage = data.get("usage") or {}
        return {
            "content": content,
            "reasoning": reasoning,
            "finish_reason": finish,
            "usage": usage,
        }
    raise RuntimeError(last_err)
