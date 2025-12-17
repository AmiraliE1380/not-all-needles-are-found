"""
openai_chat.py
A minimal helper around OpenAI + Gemini chat endpoints.
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

# --------------------------------------------------------------------------- #
#  Environment & clients
# --------------------------------------------------------------------------- #
load_dotenv()

_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_gemini_client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY from env


# --------------------------------------------------------------------------- #
#  Routing helpers
# --------------------------------------------------------------------------- #
def _is_gemini_model(model: str) -> bool:
    return model.startswith("gemini-")


def _is_openai_model(model: str) -> bool:
    return model in OPENAI_MODELS


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

    # ------------------------- Unknown model ------------------------- #
    raise ValueError(
        f"Unknown model '{model}'. "
        f"Expected an OpenAI model from OPENAI_MODELS or a Gemini model like 'gemini-2.5-flash'."
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
