"""
File Organizer
Scans a messy folder and moves every file into a named subfolder
based on its extension (Images, Documents, Data, etc.).
"""
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Map of category → list of extensions it owns
CATEGORIES: dict[str, list[str]] = {
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".pptx", ".ppt", ".odt", ".rtf", ".md"],
    "Data":      [".csv", ".xlsx", ".xls", ".json", ".xml", ".sql", ".tsv"],
    "Videos":    [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".m4v"],
    "Audio":     [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "Archives":  [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code":      [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rb"],
}

# Reverse lookup: extension → category
_EXT_MAP: dict[str, str] = {
    ext: cat for cat, exts in CATEGORIES.items() for ext in exts
}


def organize_folder(source_folder: str, dry_run: bool = False) -> dict:
    """
    Organize every file in *source_folder* into subfolders by type.

    Args:
        source_folder: Path to the folder you want to clean up.
        dry_run:       If True, nothing moves — just preview what *would* happen.

    Returns:
        {
          "moved":    [{"file": str, "from": str, "to": str}, ...],
          "summary":  {"Images": 3, "Documents": 2, ...},
          "skipped":  [str, ...],   # files already in a category folder
          "dry_run":  bool,
        }
    """
    source = Path(source_folder)
    if not source.exists():
        raise FileNotFoundError(f"Folder not found: {source_folder}")

    moved: list[dict] = []
    skipped: list[str] = []
    summary: dict[str, int] = defaultdict(int)

    # Collect only top-level files (not files inside subfolders we already made)
    top_level_files = [f for f in source.iterdir() if f.is_file()]

    for file in top_level_files:
        ext = file.suffix.lower()
        category = _EXT_MAP.get(ext, "Other")
        dest_dir = source / category
        dest_file = dest_dir / file.name

        if not dry_run:
            dest_dir.mkdir(exist_ok=True)
            # Avoid name collision — append timestamp
            if dest_file.exists():
                ts = datetime.now().strftime("%H%M%S%f")
                dest_file = dest_dir / f"{file.stem}_{ts}{file.suffix}"
            shutil.move(str(file), str(dest_file))

        moved.append({"file": file.name, "from": str(source), "to": str(dest_dir)})
        summary[category] += 1

    return {
        "moved": moved,
        "summary": dict(summary),
        "skipped": skipped,
        "dry_run": dry_run,
        "total": len(moved),
    }
