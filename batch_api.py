"""
batch_api.py
Submit many Chat Completions via OpenAI's Batch API and fetch results.

Usage
-----
from batch_api import BatchItem, run_chat_batch_and_get_results

items = [
    BatchItem(custom_id="q1", prompt="Give me 3 facts about the Moon."),
    BatchItem(custom_id="q2", prompt="Translate 'Hello' to French.", system_prompt="Be literal."),
]
out = run_chat_batch_and_get_results(items, default_model="gpt-5-mini")
print(out["q1"])
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

# --------------------------------------------------------------------------- #
#  Environment & client setup
# --------------------------------------------------------------------------- #
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --------------------------------------------------------------------------- #
#  Data model
# --------------------------------------------------------------------------- #
@dataclass
class BatchItem:
    custom_id: str
    prompt: str
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


def _default_temperature_for(model: str) -> float:
    return 1.0 if model in {"gpt-5-mini", "gpt-5"} else 0.0


def _make_chat_body(item: BatchItem, default_model: str) -> dict:
    model = item.model or default_model
    body = {
        "model": model,
        "messages": (
            [{"role": "system", "content": item.system_prompt}] if item.system_prompt else []
        ) + [{"role": "user", "content": item.prompt}],
        "temperature": _default_temperature_for(model)
        if item.temperature is None
        else item.temperature,
    }
    if item.top_p is not None:
        body["top_p"] = item.top_p
    if item.frequency_penalty is not None:
        body["frequency_penalty"] = item.frequency_penalty
    if item.presence_penalty is not None:
        body["presence_penalty"] = item.presence_penalty
    return body


def _write_jsonl_for_batch(items: Iterable[BatchItem], default_model: str) -> str:
    fd, path = tempfile.mkstemp(prefix="openai_batch_", suffix=".jsonl")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(
                json.dumps(
                    {
                        "custom_id": it.custom_id,
                        "method": "POST",
                        "url": "/v1/chat/completions",
                        "body": _make_chat_body(it, default_model),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    return path


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
def submit_chat_batch(
    items: List[BatchItem],
    *,
    default_model: str = "gpt-5-mini",
    completion_window: str = "24h",
):
    """
    Creates a Batch job and returns the batch object (opaque dict-like).
    """
    if not items:
        raise ValueError("No BatchItem entries provided.")
    jsonl_path = _write_jsonl_for_batch(items, default_model)

    # 1) Upload input JSONL
    with open(jsonl_path, "rb") as fh:
        input_file = client.files.create(file=fh, purpose="batch")

    # 2) Create the batch job
    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window=completion_window,
    )
    return batch


def wait_for_batch(
    batch_id: str,
    *,
    poll_interval_seconds: float = 5.0,
    timeout_seconds: Optional[float] = None,
):
    """
    Polls until batch is in a terminal state; returns final batch object.
    """
    start = time.time()
    while True:
        batch = client.batches.retrieve(batch_id)
        if batch.status in {"completed", "failed", "expired", "cancelled"}:
            return batch
        if timeout_seconds is not None and (time.time() - start) > timeout_seconds:
            raise TimeoutError(f"Timed out waiting for batch {batch_id}.")
        time.sleep(poll_interval_seconds)


def cancel_batch(batch_id: str):
    return client.batches.cancel(batch_id)


def fetch_batch_results(batch_id: str) -> Dict[str, str]:
    """
    For a completed batch, downloads & parses output JSONL.
    Returns: dict custom_id -> assistant text (or error string).
    """
    batch = client.batches.retrieve(batch_id)
    if batch.status != "completed":
        raise RuntimeError(f"Batch {batch_id} is not completed (status={batch.status}).")
    if not batch.output_file_id:
        raise RuntimeError(f"No output_file_id for batch {batch_id}.")

    # Download output JSONL
    stream = client.files.content(batch.output_file_id)
    content = stream.read().decode("utf-8")

    results: Dict[str, str] = {}
    for line in content.strip().splitlines():
        obj = json.loads(line)
        cid = obj.get("custom_id", "")
        error = obj.get("error")
        if error:
            results[cid] = f"[BATCH ERROR] {error}"
            continue

        body = obj.get("response", {}).get("body", {})
        choices = body.get("choices", [])
        message = choices[0].get("message") if choices else None
        text = (message or {}).get("content")
        results[cid] = text.strip() if isinstance(text, str) else json.dumps(body)
    return results


def run_chat_batch_and_get_results(
    items: List[BatchItem],
    *,
    default_model: str = "gpt-5-mini",
    completion_window: str = "24h",
    poll_interval_seconds: float = 5.0,
) -> Dict[str, str]:
    batch = submit_chat_batch(items, default_model=default_model, completion_window=completion_window)
    wait_for_batch(batch.id, poll_interval_seconds=poll_interval_seconds)
    return fetch_batch_results(batch.id)


# --------------------------------------------------------------------------- #
#  Demo
# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    demo_items = [
        BatchItem(custom_id="ex1", prompt="Give me 3 bullet points about the Moon."),
        BatchItem(custom_id="ex2", prompt="Translate 'Hello' to French.", system_prompt="Be literal."),
        BatchItem(custom_id="ex3", prompt="One sentence on why batching cuts cost."),
    ]
    out = run_chat_batch_and_get_results(demo_items, default_model="gpt-5-mini")
    for k, v in out.items():
        print(f"\n[{k}]\n{v}\n")
