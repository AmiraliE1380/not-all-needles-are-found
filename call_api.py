"""
openai_chat.py
A minimal helper around OpenAI + Gemini + Claude + DeepSeek chat endpoints.
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

# DeepSeek (OpenAI-compatible API)
# Docs: base_url can be https://api.deepseek.com/v1 (OpenAI-compatible) :contentReference[oaicite:1]{index=1}
_deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
)

# Lazy-ish: instantiate if SDK is available; otherwise error only when used.
_claude_client = None
if Anthropic is not None:
    _claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


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


def _is_deepseek_model(model: str) -> bool:
    # DeepSeek’s OpenAI-compatible model ids include:
    # - deepseek-chat
    # - deepseek-reasoner
    # We also accept user-friendly aliases like "deepseek-v3.2".
    return model.startswith("deepseek-")


def _normalize_claude_model(model: str) -> str:
    """
    Allow a couple of user-friendly aliases, while preserving backward compatibility.
    Official Haiku 4.5 model id (per Anthropic) is: "claude-haiku-4-5"
    """
    aliases = {
        "claude-4.5-haiku": "claude-haiku-4-5",
        "claude-haiku-4.5": "claude-haiku-4-5",
        "claude-haiku-4-5": "claude-haiku-4-5",
    }
    return aliases.get(model, model)


def _normalize_deepseek_model(model: str) -> str:
    """
    DeepSeek API model ids (Chat Completions) are:
      - deepseek-chat (V3.2 non-thinking)
      - deepseek-reasoner (V3.2 thinking)
    We accept a few aliases for convenience/back-compat.
    :contentReference[oaicite:2]{index=2}
    """
    aliases = {
        # User-friendly names -> official API ids
        "deepseek-v3.2": "deepseek-chat",
        "deepseek-v3-2": "deepseek-chat",
        "deepseek-v3.2-chat": "deepseek-chat",
        "deepseek-v3.2-non-thinking": "deepseek-chat",
        "deepseek-v3.2-thinking": "deepseek-reasoner",
        "deepseek-v3.2-reasoner": "deepseek-reasoner",
        # Identity mappings
        "deepseek-chat": "deepseek-chat",
        "deepseek-reasoner": "deepseek-reasoner",
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
    - model starts with "gemini-"  -> Gemini API
    - model in OPENAI_MODELS      -> OpenAI API
    - model starts with "claude-" -> Anthropic Claude API
    - model starts with "deepseek-" -> DeepSeek API (OpenAI-compatible)
    """

    # ------------------------- Gemini routing ------------------------- #
    if _is_gemini_model(model):
        config = types.GenerateContentConfig(
            temperature=0.0,        # deterministic
            top_p=1.0,              # no nucleus sampling
            frequency_penalty=0.0,  # allow repetition
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
        )
        return response.choices[0].message.content.strip()

    # ------------------------- DeepSeek routing ------------------------- #
    if _is_deepseek_model(model):
        if not os.getenv("DEEPSEEK_API_KEY"):
            raise RuntimeError(
                "DeepSeek requested but DEEPSEEK_API_KEY is not set."
            )

        deepseek_model = _normalize_deepseek_model(model)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # DeepSeek parameters requested:
        # temperature=0, top_p=1, frequency_penalty=0, presence_penalty=0.3
        # Note: DeepSeek docs indicate some parameters may be unsupported for certain
        # modes/models; if unsupported, they are ignored rather than erroring. :contentReference[oaicite:3]{index=3}
        response = _deepseek_client.chat.completions.create(
            model=deepseek_model,
            messages=messages,
            temperature=0.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.3,
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

        # To stay deterministic and avoid request errors, set temperature=0 and omit top_p.
        claude_kwargs = dict(
            model=claude_model,
            max_tokens=1024,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            temperature=0.0,
        )

        if system_prompt:
            claude_kwargs["system"] = [{"type": "text", "text": system_prompt}]

        resp = _claude_client.messages.create(**claude_kwargs)
        return _extract_claude_text(resp)

    # ------------------------- Unknown model ------------------------- #
    raise ValueError(
        f"Unknown model '{model}'. "
        f"Expected an OpenAI model from OPENAI_MODELS, a Gemini model like 'gemini-2.5-flash', "
        f"a Claude model like 'claude-haiku-4-5', "
        f"or a DeepSeek model like 'deepseek-chat' / 'deepseek-reasoner' / 'deepseek-v3.2'."
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
    print(chat_with_model(claude_demo_prompt, model="claude-haiku-4-5"))

    print("\n=== DeepSeek demo ===")
    deepseek_demo_prompt = "Briefly explain what a context window is for LLMs."
    # DeepSeek-V3.2 non-thinking mode is exposed as model id "deepseek-chat". :contentReference[oaicite:4]{index=4}
    print(chat_with_model(deepseek_demo_prompt, model="deepseek-chat"))
    # Or using alias:
    # print(chat_with_model(deepseek_demo_prompt, model="deepseek-v3.2"))
