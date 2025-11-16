from pathlib import Path

logs_dir = Path("logs")

for path in logs_dir.glob("*.txt"):
    name = path.name
    if name.startswith("quiz_responses_272k") and name.endswith("no_hallucination.txt"):
        new_name = name[:-len("no_hallucination.txt")] + "_no_hallucination.txt"
        new_path = path.with_name(new_name)
        print(f"Renaming: {path} -> {new_path}")
        path.rename(new_path)
