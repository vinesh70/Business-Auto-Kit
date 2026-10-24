"""
Data Cleaner
Fixes common problems in messy spreadsheet data and returns quality metrics.
"""
import re
from pathlib import Path
import pandas as pd


# ── Fixers ────────────────────────────────────────────────────────────────────

def _fix_name(val: str) -> str:
    return str(val).strip().title() if pd.notna(val) and str(val).strip() else ""


def _fix_email(val: str) -> str:
    return str(val).strip().lower() if pd.notna(val) and str(val).strip() else ""


def _fix_phone(val) -> str:
    if pd.isna(val) or str(val).strip() in ("", "nan"):
        return ""
    digits = re.sub(r"\D", "", str(val))
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    if len(digits) == 10:
        return f"+91-{digits[:5]}-{digits[5:]}"
    return str(val).strip()


def _fix_city(val: str) -> str:
    return str(val).strip().title() if pd.notna(val) and str(val).strip() else ""


def _is_valid_email(val: str) -> bool:
    return bool(re.match(r"^[\w.+\-]+@[\w\-]+\.[a-z]{2,}$", str(val), re.I))


_HANDLERS = {
    "name":  _fix_name,
    "email": _fix_email,
    "phone": _fix_phone,
    "city":  _fix_city,
}


# ── Issue analyser (runs on RAW data before cleaning) ────────────────────────

def _count_issues(df: pd.DataFrame) -> dict:
    col_lower = {c.lower(): c for c in df.columns}
    issues = {}

    if "name" in col_lower:
        c = col_lower["name"]
        issues["ALL_CAPS names"] = int(
            df[c].dropna().apply(
                lambda x: bool(str(x).strip()) and str(x).strip().isupper() and len(str(x).strip()) > 1
            ).sum()
        )

    if "email" in col_lower:
        c = col_lower["email"]
        issues["Uppercase emails"] = int(
            df[c].dropna().apply(
                lambda x: bool(re.search(r"[A-Z]", str(x)))
            ).sum()
        )
        issues["Invalid email format"] = int(
            df[c].dropna().apply(
                lambda x: not _is_valid_email(x) if str(x).strip() else False
            ).sum()
        )

    if "phone" in col_lower:
        c = col_lower["phone"]
        issues["Non-standard phones"] = int(
            df[c].dropna().apply(
                lambda x: not bool(re.match(r"^\+91-\d{5}-\d{5}$", str(x).strip()))
                          and str(x).strip() != ""
            ).sum()
        )

    ws_count = 0
    for col in df.columns:
        ws_count += int(
            df[col].dropna().apply(
                lambda x: str(x) != str(x).strip()
            ).sum()
        )
    if ws_count:
        issues["Extra whitespace"] = ws_count

    issues["Duplicate rows"]  = int(df.duplicated().sum())
    issues["Blank/empty rows"] = int(df.isnull().all(axis=1).sum())

    return {k: v for k, v in issues.items() if v > 0}


def _quality_score(df: pd.DataFrame, issues: dict) -> int:
    total_cells = df.size
    if total_cells == 0:
        return 100
    total_issues = sum(issues.values())
    score = max(0, round(100 - (total_issues / total_cells * 100)))
    return min(100, score)


# ── Main cleaner ──────────────────────────────────────────────────────────────

def clean_contacts(input_path: str, output_path: str, drop_duplicates: bool = True) -> dict:
    if not Path(input_path).exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    df_raw = pd.read_csv(input_path, dtype=str).fillna("")
    rows_before = len(df_raw)

    issues_before = _count_issues(df_raw)
    score_before  = _quality_score(df_raw, issues_before)

    df = df_raw.copy()
    col_lower = {c.lower(): c for c in df.columns}
    cleaned_cols = []

    for key, handler in _HANDLERS.items():
        if key in col_lower:
            actual = col_lower[key]
            df[actual] = df[actual].apply(lambda x: handler(x) if x else "")
            cleaned_cols.append(actual)

    for col in df.columns:
        if col not in cleaned_cols:
            df[col] = df[col].apply(lambda x: str(x).strip())

    df.replace("", pd.NA, inplace=True)
    df.dropna(how="all", inplace=True)
    blanks_removed = rows_before - len(df)
    df.fillna("", inplace=True)

    if drop_duplicates:
        before_dedup = len(df)
        df.drop_duplicates(inplace=True)
        duplicates_removed = before_dedup - len(df)
    else:
        duplicates_removed = 0

    df.reset_index(drop=True, inplace=True)

    issues_after = _count_issues(df)
    score_after  = _quality_score(df, issues_after)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    return {
        "rows_before":         rows_before,
        "rows_after":          len(df),
        "blanks_removed":      blanks_removed,
        "duplicates_removed":  duplicates_removed,
        "columns_cleaned":     cleaned_cols,
        "output":              output_path,
        "issues_found":        issues_before,
        "total_issues":        sum(issues_before.values()),
        "quality_before":      score_before,
        "quality_after":       score_after,
    }
