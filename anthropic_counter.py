"""
anthropic_counter.py

Counts tokens in a text file using Anthropic Claude's official tokenizer
(via the Token Count API).
"""

from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic


def count_claude_tokens(txt_path: str, model: str = "claude-sonnet-4-5") -> int:
    path = Path(txt_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8")

    client = Anthropic()  # reads ANTHROPIC_API_KEY from environment

    resp = client.messages.count_tokens(
        model=model,
        messages=[{"role": "user", "content": text}],
    )
    return resp.input_tokens


if __name__ == "__main__":
    load_dotenv()  # loads ANTHROPIC_API_KEY from .env

    txt_file_path = "texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_200k_expected_100%.txt"
    token_count = count_claude_tokens(txt_file_path)

    print(f"Claude token count for '{txt_file_path}': {token_count}")
