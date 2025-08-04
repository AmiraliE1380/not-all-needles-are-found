"""
openai_chat.py
A minimal helper around OpenAI’s chat-completion endpoint.

Usage
-----
>>> from openai_chat import chat_with_model
>>> print(chat_with_model(
...     prompt="Hello! How long can the context of GPT-4o be?",
...     model="gpt-4o-mini"))
"""

from __future__ import annotations

import os
from typing import List, Optional

from dotenv import load_dotenv
from openai import OpenAI

# --------------------------------------------------------------------------- #
#  Environment & client setup
# --------------------------------------------------------------------------- #
load_dotenv()  # Loads OPENAI_API_KEY (and anything else) from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Accepted model names (extend or trim as you like)
OPENAI_MODELS: List[str] = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo-2024-04-09",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4-0613",
    "gpt-4-32k-0613",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-instruct",
    "o1",
    "o1-mini",
    "o1-pro",
    "o3-mini",
    "o3",
    "o3-pro",
]

def chat_with_model(
    prompt: str,
    model: str = "gpt-4o-mini",
    *,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Send `prompt` to `model` and return the assistant’s reply (content only).

    Parameters
    ----------
    prompt : str
        The user’s message.
    model : str, default "gpt-4o-mini"
        Any model from `OPENAI_MODELS`.
    system_prompt : str | None, optional
        Prepend a system message if you want extra instructions/context.

    Returns
    -------
    str
        The assistant’s reply text.

    Raises
    ------
    ValueError
        If `model` is not in `OPENAI_MODELS`.
    OpenAIError
        Any error bubbled up from the OpenAI client (network, quota, etc.).
    """
    if model not in OPENAI_MODELS:
        raise ValueError(
            f"Model '{model}' is not in the approved list.\n"
            f"Allowed values: {', '.join(OPENAI_MODELS)}"
        )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.3,
    )
    return response.choices[0].message.content.strip()


# --------------------------------------------------------------------------- #
#  Demo (run `python openai_chat.py` directly)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    demo_prompt = (
        "Hello! How long can the context of famous LLMs be? "
        "Give me the maximum context window in tokens."
    )
    print(chat_with_model(demo_prompt, model="gpt-4o-mini"))
