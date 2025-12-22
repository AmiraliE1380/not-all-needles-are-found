from pathlib import Path
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


def count_gemini_tokens(
    txt_path: str,
    model: str = "gemini-2.5-flash",
) -> int:
    path = Path(txt_path)
    if not path.exists():
        raise FileNotFoundError(path)

    text = path.read_text(encoding="utf-8")

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.count_tokens(
        model=model,
        contents=text,
    )

    return response.total_tokens


if __name__ == "__main__":
    import sys

    # if len(sys.argv) != 2:
    #     print("Usage: python gemini_token_counter.py <file.txt>")
    #     sys.exit(1)
    addr = "texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_1000k_expected_90%.txt"
    addr = "texts/la_comédie_humaine_(balzac)/all_combined/combined_test_1139158.txt"

    tokens = count_gemini_tokens(addr)
    print(f"Gemini token count: {tokens}")
