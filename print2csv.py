from __future__ import annotations
import ast
import csv
import os
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

# print2csv.py


def parse_grades_file(path: str) -> List[List[Tuple[float, float, float, float]]]:
    """
    Load and parse a text file that contains a Python literal representing
    a matrix (list of lists) of 4-tuples of numbers.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"grades file not found: {path}")
    text = p.read_text()
    data = ast.literal_eval(text)
    if not isinstance(data, list):
        raise ValueError("parsed data is not a list")
    # Basic validation and normalization
    matrix: List[List[Tuple[float, float, float, float]]] = []
    for row in data:
        if not isinstance(row, (list, tuple)):
            raise ValueError("each row must be a list/tuple")
        parsed_row: List[Tuple[float, float, float, float]] = []
        for cell in row:
            if not (isinstance(cell, (list, tuple)) and len(cell) >= 4):
                raise ValueError("each cell must be a sequence with at least 4 numeric elements")
            # take first 4 elements and convert to float
            first4 = tuple(float(cell[i]) for i in range(4))
            parsed_row.append(first4)
        matrix.append(parsed_row)
    return matrix


def transpose_matrix(matrix: List[List[Tuple[float, float, float, float]]]
                     ) -> List[List[Tuple[float, float, float, float]]]:
    """
    Transpose a rectangular matrix (list of rows). Raises ValueError if rows differ in length.
    """
    if not matrix:
        return []
    row_count = len(matrix)
    col_count = len(matrix[0])
    for r in matrix:
        if len(r) != col_count:
            raise ValueError("cannot transpose matrix with rows of differing lengths")
    # transpose: new rows are columns of original
    return [[matrix[r][c] for r in range(row_count)] for c in range(col_count)]


def _write_matrix_csv(matrix: List[List[float]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        for row in matrix:
            writer.writerow(row)


def save_scores_to_csvs(model: str, raw_grades_addr: str, out_dir: str = "CSVs") -> dict:
    """
    Given a model name and a path to a .txt file containing a matrix of 4-tuples,
    extract the 1st, 2nd, 3rd and 4th elements of every tuple into four CSV files:
      - {out_dir}/{model}_total_scores.csv          (first element)
      - {out_dir}/{model}_direct_scores.csv         (second element)
      - {out_dir}/{model}_inferential_scores.csv    (third element)
      - {out_dir}/{model}_hallucinations_scores.csv (fourth element)

    Returns a dict with the produced file paths.
    """
    matrix = parse_grades_file(raw_grades_addr)

    # apply transpose
    matrix = transpose_matrix(matrix)

    # Build four matrices of floats with same shape
    totals: List[List[float]] = []
    directs: List[List[float]] = []
    inferentials: List[List[float]] = []
    hallucinations: List[List[float]] = []

    for row in matrix:
        totals.append([cell[0] for cell in row])
        directs.append([cell[1] for cell in row])
        inferentials.append([cell[2] for cell in row])
        hallucinations.append([cell[3] for cell in row])

    out_base = Path(out_dir)
    paths = {
        "total": out_base / f"{model}_total_scores.csv",
        "direct": out_base / f"{model}_direct_scores.csv",
        "inferential": out_base / f"{model}_inferential_scores.csv",
        "hallucinations": out_base / f"{model}_hallucinations_scores.csv",
    }

    _write_matrix_csv(totals, paths["total"])
    _write_matrix_csv(directs, paths["direct"])
    _write_matrix_csv(inferentials, paths["inferential"])
    _write_matrix_csv(hallucinations, paths["hallucinations"])

    # return string paths for convenience
    return {k: str(v) for k, v in paths.items()}

if __name__ == "__main__":
    save_scores_to_csvs(
        model="gpt-4o",
        raw_grades_addr="logs/grades_gpt-4o-mini.txt"
    )