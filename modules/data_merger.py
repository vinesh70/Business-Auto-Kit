"""
Data Merger
Combines multiple CSV or Excel files into one clean master file.
Handles different column orders, removes duplicates, and logs the merge.
"""
from pathlib import Path
import pandas as pd


def merge_csv_files(
    input_files: list[str],
    output_path: str,
    drop_duplicates: bool = True,
    sort_by: str | None = None,
) -> dict:
    """
    Merge a list of CSV/Excel files into a single output CSV.

    Args:
        input_files:     List of file paths (CSV or XLSX).
        output_path:     Where to save the merged result.
        drop_duplicates: Remove exact duplicate rows (default True).
        sort_by:         Optional column name to sort the result by.

    Returns:
        {
          "files_merged":  int,
          "rows_before":   int,
          "rows_after":    int,
          "duplicates_removed": int,
          "columns":       list[str],
          "output":        str,
        }
    """
    frames: list[pd.DataFrame] = []
    total_rows_before = 0

    for path in input_files:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if p.suffix.lower() in (".xlsx", ".xls"):
            df = pd.read_excel(p)
        else:
            df = pd.read_csv(p)

        df["_source_file"] = p.name   # track origin
        total_rows_before += len(df)
        frames.append(df)

    if not frames:
        raise ValueError("No valid files provided.")

    merged = pd.concat(frames, ignore_index=True)

    # Drop duplicates ignoring the tracking column
    if drop_duplicates:
        data_cols = [c for c in merged.columns if c != "_source_file"]
        before = len(merged)
        merged = merged.drop_duplicates(subset=data_cols)
        duplicates_removed = before - len(merged)
    else:
        duplicates_removed = 0

    if sort_by and sort_by in merged.columns:
        merged = merged.sort_values(sort_by).reset_index(drop=True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)

    return {
        "files_merged": len(frames),
        "rows_before": total_rows_before,
        "rows_after": len(merged),
        "duplicates_removed": duplicates_removed,
        "columns": list(merged.columns),
        "output": output_path,
    }
