"""
openai_chat.py
A minimal helper around OpenAI + Gemini + Claude chat endpoints.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from constant_vals import OPENAI_MODELS

# Gemini (assumed installed and configured)
from google import genai
from google.genai import types

# Claude (Anthropic) - optional dependency (only required if you call Claude)
try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover
    Anthropic = None  # type: ignore

# --------------------------------------------------------------------------- #
#  Environment & clients
# --------------------------------------------------------------------------- #
load_dotenv()

_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_gemini_client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY from env

# Lazy-ish: instantiate if SDK is available; otherwise error only when used.
_claude_client = None
if Anthropic is not None:
    _claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))  # default env var :contentReference[oaicite:4]{index=4}


# --------------------------------------------------------------------------- #
#  Routing helpers
# --------------------------------------------------------------------------- #
def _is_gemini_model(model: str) -> bool:
    return model.startswith("gemini-")


def _is_openai_model(model: str) -> bool:
    return model in OPENAI_MODELS


def _is_claude_model(model: str) -> bool:
    # Canonical Anthropic model ids generally start with "claude-"
    return model.startswith("claude-")


def _normalize_claude_model(model: str) -> str:
    """
    Allow a couple of user-friendly aliases, while preserving backward compatibility.
    Official Haiku 4.5 model id (per Anthropic) is: "claude-haiku-4-5" :contentReference[oaicite:5]{index=5}
    """
    aliases = {
        "claude-4.5-haiku": "claude-haiku-4-5",
        "claude-haiku-4.5": "claude-haiku-4-5",
        "claude-haiku-4-5": "claude-haiku-4-5",
    }
    return aliases.get(model, model)


def _extract_claude_text(message) -> str:
    """
    Anthropic Messages API returns content blocks; concatenate text blocks.
    """
    blocks = getattr(message, "content", None) or []
    out = []
    for b in blocks:
        b_type = getattr(b, "type", None) if not isinstance(b, dict) else b.get("type")
        if b_type == "text":
            text = getattr(b, "text", None) if not isinstance(b, dict) else b.get("text")
            if text:
                out.append(text)
    return "".join(out).strip()


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
def chat_with_model(
    prompt: str,
    model: str = "gpt-5-mini",
    *,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Send `prompt` to `model` and return the assistant's reply (content only).

    Routing:
    - model starts with "gemini-" -> Gemini API
    - model in OPENAI_MODELS     -> OpenAI API
    - model starts with "claude-" -> Anthropic Claude API
    """

    # ------------------------- Gemini routing ------------------------- #
    if _is_gemini_model(model):
        config = types.GenerateContentConfig(
            temperature=0.0,        # deterministic
            top_p=1.0,              # no nucleus sampling
            frequency_penalty=0.0,  # allow repetition
            # presence_penalty=0.3,   # encourage topic diversity
            system_instruction=system_prompt if system_prompt else None,
        )

        resp = _gemini_client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        return (resp.text or "").strip()

    # ------------------------- OpenAI routing ------------------------- #
    if _is_openai_model(model):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = _openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=1.0 if model in {"gpt-5-mini", "gpt-5"} else 0.0,
            top_p=1.0,
            frequency_penalty=0.0,
            # presence_penalty=0.3,
        )

        return response.choices[0].message.content.strip()

    # ------------------------- Claude routing ------------------------- #
    if _is_claude_model(model):
        if _claude_client is None:
            raise RuntimeError(
                "Claude requested but Anthropic SDK is not available. "
                "Install it with `pip install anthropic` and set ANTHROPIC_API_KEY."
            )

        claude_model = _normalize_claude_model(model)

        # NOTE:
        # - Anthropic supports temperature/top_p, but recommends adjusting only one. :contentReference[oaicite:6]{index=6}
        # - Some 4.5 deployments (e.g., Bedrock) explicitly reject providing both temperature and top_p. :contentReference[oaicite:7]{index=7}
        # To stay deterministic and avoid request errors, we set temperature=0.0 and omit top_p.
        # Anthropic Messages API does not expose OpenAI-style frequency_penalty/presence_penalty. :contentReference[oaicite:8]{index=8}
        claude_kwargs = dict(
            model=claude_model,
            max_tokens=1024,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            temperature=0.0,
        )

        if system_prompt:  # only include if non-empty
            claude_kwargs["system"] = [{"type": "text", "text": system_prompt}]

        resp = _claude_client.messages.create(**claude_kwargs)
        return _extract_claude_text(resp)


    # ------------------------- Unknown model ------------------------- #
    raise ValueError(
        f"Unknown model '{model}'. "
        f"Expected an OpenAI model from OPENAI_MODELS, a Gemini model like 'gemini-2.5-flash', "
        f"or a Claude model like 'claude-haiku-4-5'."
    )


# --------------------------------------------------------------------------- #
#  Demo
# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    demo_prompt = (
        "Hello! How long can the context of famous LLMs be? "
        "Give me the maximum context window in tokens."
    )

    print("=== OpenAI demo ===")
    print(chat_with_model(demo_prompt, model="gpt-5-mini"))

    print("\n=== Gemini demo ===")
    gemini_demo_prompt = "Briefly explain what a context window is for LLMs."
    print(chat_with_model(gemini_demo_prompt, model="gemini-2.5-flash"))

    print("\n=== Claude demo ===")
    claude_demo_prompt = "Briefly explain what a context window is for LLMs."
    # Official model id per Anthropic: claude-haiku-4-5 :contentReference[oaicite:10]{index=10}
    print(chat_with_model(claude_demo_prompt, model="claude-haiku-4-5"))
