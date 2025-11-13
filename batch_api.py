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
out = run_chat_batch_and_get_results(items, default_model="gpt-5-mini", problem_id="moon_001")
print(out["q1"])
"""

from __future__ import annotations

import json
import os
import tempfile
import time
import pathlib
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


# --------------------------- helpers ----------------------------------------
def _write_results_file(problem_id: str, results: Dict[str, str]) -> str:
    """
    Writes results as a readable text file:
        [custom_id]
        <assistant text>
    """
    out_dir = pathlib.Path("batch_responses")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{problem_id}.txt"

    
    from take_quiz_batch import get_unique_path
    out_path = get_unique_path(str(out_path))
    
    lines = []
    for cid, text in results.items():
        lines.append(f"[{cid}]\n{text}\n")
    content = "\n".join(lines)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(out_path)


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
def submit_chat_batch(
    items: List[BatchItem],
    *,
    default_model: str = "gpt-5-mini",
    completion_window: str = "24h",
    problem_id: Optional[str] = None,  # <-- pass-through id for logging
):
    """
    Creates a Batch job and returns the batch object (opaque dict-like).
    If problem_id is provided, it will be printed alongside the batch_id.
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
    if problem_id:
        print(f"✅ Submitted batch: problem_id={problem_id} (batch_id={batch.id})")
    else:
        print(f"✅ Submitted batch: (batch_id={batch.id})")
    return batch


def wait_for_batch(
    batch_id: str,
    *,
    poll_interval_seconds: float = 5.0,
    timeout_seconds: Optional[float] = None,
    verbose: bool = False,
    problem_id: Optional[str] = None,  # <-- include in progress logs
):
    """
    Polls until batch is in a terminal state; returns final batch object.
    """
    start = time.time()
    interval = poll_interval_seconds
    while True:
        batch = client.batches.retrieve(batch_id)
        if verbose:
            tag = f"problem_id={problem_id}, " if problem_id else ""
            print(f"[{tag}batch_id={batch.id}] status={batch.status}")
        if batch.status in {"completed", "failed", "expired", "cancelled"}:
            return batch
        if timeout_seconds is not None and (time.time() - start) > timeout_seconds:
            raise TimeoutError(f"Timed out waiting for batch {batch_id}.")
        time.sleep(interval)
        interval = min(interval * 1.5, 60.0)


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
    verbose: bool = True,
    problem_id: str,  # <-- REQUIRED: user-specified id for this run
) -> Dict[str, str]:
    """
    Submit → wait → fetch, all while tagging logs and the output filename with problem_id.
    """
    batch = submit_chat_batch(
        items,
        default_model=default_model,
        completion_window=completion_window,
        problem_id=problem_id,
    )

    print(f"⏳ Waiting for response... (problem_id={problem_id}, batch_id={batch.id})")
    final = wait_for_batch(
        batch.id,
        poll_interval_seconds=poll_interval_seconds,
        timeout_seconds=None,   # keep original behavior; customize if desired
        verbose=verbose,
        problem_id=problem_id,
    )

    print(f"ℹ️ Batch finished: status={final.status} (problem_id={problem_id}, batch_id={final.id})")

    # Helper to write a status-only file and return the stub dict
    def _return_status_stub(note: str) -> Dict[str, str]:
        stub = {
            "_batch_id": final.id,
            "_status": final.status,
            "_output_file_id": getattr(final, "output_file_id", None),
            "_error_file_id": getattr(final, "error_file_id", None),
            "_request_counts": getattr(final, "request_counts", None),
            "_note": note,
        }
        path = _write_results_file(
            problem_id,
            {"_batch_status": json.dumps(stub, ensure_ascii=False, indent=2)},
        )
        print(f"📄 Wrote batch status to: {path}")
        # Return a simpler (non-pretty-printed) JSON string as the value
        return {"_batch_status": json.dumps(stub)}

    # Case 1: batch did not complete
    if final.status != "completed":
        return _return_status_stub(
            "Batch did not complete successfully; no output_file_id to fetch."
        )

    # Case 2: batch says 'completed' but has no output_file_id
    if not getattr(final, "output_file_id", None):
        return _return_status_stub(
            "Batch completed but has no output_file_id; likely all requests failed. "
            "Check error_file_id and request_counts for details."
        )

    # Normal happy path: completed AND has output_file_id
    results = fetch_batch_results(final.id)
    path = _write_results_file(problem_id, results)
    print(f"📄 Saved results to: {path}")
    return results



# --------------------------- demo -------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    demo_items = [
        BatchItem(custom_id="ex1", prompt="Give me 3 bullet points about the Moon."),
        BatchItem(custom_id="ex2", prompt="Translate 'Hello' to French.", system_prompt="Be literal."),
        BatchItem(custom_id="ex3", prompt="One sentence on why batching cuts cost."),
    ]
    out = run_chat_batch_and_get_results(
        demo_items,
        default_model="gpt-5-mini",
        problem_id="demo_moon_translation_batch_v2",
        verbose=True,
    )
    for k, v in out.items():
        print(f"\n[{k}]\n{v}\n")
