from typing import List, Optional
import os
import re
from collections import Counter
from io import StringIO
import pandas as pd

"""
print2csv.py

Provides a single function `extract_and_save_tables` that:
- reads a .txt file,
- extracts up to 4 tabular blocks into pandas DataFrames,
- saves them as CSV files named "<model>_table1.csv" ... "<model>_table4.csv".

Heuristic parsing:
- Splits the text into blocks separated by two or more newlines.
- Tokenizes each block by commas, tabs, semicolons or whitespace.
- Keeps rows with the most common column count in the block.
- Detects a header row when the first row contains non-numeric tokens while subsequent rows are mostly numeric.
"""




def extract_and_save_tables(model: str, file_addr: str, out_dir: Optional[str] = None) -> List[pd.DataFrame]:
    """
    Load a text file, extract up to 4 tables, save them as CSVs, and return the DataFrames.

    Args:
        model: identifier used to name output CSVs (e.g. "gpt-4").
        file_addr: path to the input .txt file.
        out_dir: directory to write CSVs (defaults to current working directory).

    Returns:
        List of up to 4 pandas.DataFrame objects (empty DataFrames if fewer than 4 found).
    """
    if out_dir is None:
        out_dir = os.getcwd()
    os.makedirs(out_dir, exist_ok=True)

    with open(file_addr, "r", encoding="utf-8") as f:
        text = f.read()

    # Split text into blocks separated by at least one blank line
    blocks = re.split(r'(?:\r?\n){2,}', text)

    tables: List[pd.DataFrame] = []

    def tokenize_line(line: str) -> List[str]:
        # split by comma, tab, semicolon or any whitespace
        parts = [p for p in re.split(r'[,\t;]|\s+', line.strip()) if p != ""]
        return parts

    for block in blocks:
        if len(tables) >= 4:
            break

        lines = [ln for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            # skip blocks that are too short to be a table
            continue

        tokenized = [tokenize_line(ln) for ln in lines]
        if not tokenized:
            continue

        counts = [len(row) for row in tokenized]
        if not counts:
            continue

        # choose the most common column count to filter noisy lines
        mode_count = Counter(counts).most_common(1)[0][0]
        rows = [row for row in tokenized if len(row) == mode_count]
        if len(rows) < 2:
            continue  # not enough consistent rows

        # header detection: if first row has any non-numeric token and subsequent rows are mostly numeric
        def is_numeric_token(tok: str) -> bool:
            tok = tok.replace(",", "")  # allow thousands separators
            try:
                float(tok)
                return True
            except Exception:
                return False

        first_row = rows[0]
        numeric_in_rest = sum(1 for r in rows[1:] for tok in r if is_numeric_token(tok))
        total_in_rest = sum(len(r) for r in rows[1:]) or 1

        header_is_text = any(not is_numeric_token(tok) for tok in first_row) and (numeric_in_rest / total_in_rest) > 0.3

        if header_is_text:
            header = [h.strip() if h.strip() != "" else f"col{i}" for i, h in enumerate(first_row, start=1)]
            data_rows = rows[1:]
        else:
            # create generic column names
            header = [f"col{i}" for i in range(1, mode_count + 1)]
            data_rows = rows

        df = pd.DataFrame(data_rows, columns=header)

        # attempt to convert columns to numeric types where reasonable
        for col in df.columns:
            coerced = pd.to_numeric(df[col].str.replace(",", ""), errors="coerce")
            # if at least one value converted to numeric, use it (preserve non-convertible as NaN)
            if coerced.notna().sum() > 0:
                df[col] = coerced

        tables.append(df)

    # If fewer than 4 tables found, append empty DataFrames
    while len(tables) < 4:
        tables.append(pd.DataFrame())

    # sanitize model for filenames
    safe_model = re.sub(r'[^A-Za-z0-9_.-]+', '_', model)

    # Save to CSV files
    for i, df in enumerate(tables[:4], start=1):
        out_path = os.path.join(out_dir, f"{safe_model}_table{i}.csv")
        # ensure consistent CSV output even for empty DataFrame
        df.to_csv(out_path, index=False)

    return tables


# Example usage (commented out):
# dfs = extract_and_save_tables("my_model", "/path/to/input.txt", out_dir="output_csvs")
# for i, df in enumerate(dfs, 1):
#     print(f"Table {i}: {df.shape}")