"""
run_demo.py — BusinessAutoKit Demo Runner
Runs all five automation demos end-to-end with a rich terminal UI.

Usage:
    python setup_demo.py   (first time only)
    python run_demo.py
"""
import sys
import time
from pathlib import Path

# ── Optional: use Rich for a beautiful terminal experience ────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
    from rich.rule import Rule
    from rich.text import Text
    RICH = True
    console = Console()
except ImportError:
    RICH = False
    class Console:
        def print(self, *a, **kw): print(*a)
        def rule(self, title=""): print(f"\n{'─'*60}  {title}  {'─'*60}\n")
    console = Console()

# ─────────────────────────────────────────────────────────────────────────────
BASE    = Path(__file__).parent
DATA    = BASE / "sample_data"
OUTPUT  = BASE / "output"
MODULES = BASE / "modules"

# Add project root to path so `import modules` works from anywhere
sys.path.insert(0, str(BASE))

from modules.file_organizer   import organize_folder
from modules.data_merger      import merge_csv_files
from modules.data_cleaner     import clean_contacts
from modules.report_generator import generate_sales_report
from modules.email_sender     import send_email


# ── Helpers ───────────────────────────────────────────────────────────────────
def header(text: str):
    if RICH:
        console.print()
        console.rule(f"[bold cyan]{text}[/]")
    else:
        print(f"\n{'='*70}\n  {text}\n{'='*70}")

def success(label: str, value: str = ""):
    if RICH:
        console.print(f"  [bold green]✔[/]  [bold]{label}[/]  {value}")
    else:
        print(f"  ✔  {label}  {value}")

def info(text: str):
    if RICH:
        console.print(f"     [dim]{text}[/]")
    else:
        print(f"     {text}")

def kv(key: str, val):
    if RICH:
        console.print(f"     [cyan]{key:<28}[/] {val}")
    else:
        print(f"     {key:<28} {val}")

def pause(seconds: float = 0.6):
    time.sleep(seconds)


# ── Banner ────────────────────────────────────────────────────────────────────
def print_banner():
    banner = """
 ╔══════════════════════════════════════════════════════════╗
 ║           🚀  BusinessAutoKit  —  by Vinesh             ║
 ║     Python Automation Toolkit · Portfolio Demo           ║
 ╚══════════════════════════════════════════════════════════╝
    """
    if RICH:
        console.print(Panel(banner, style="bold blue", expand=False))
        console.print("[dim]  Five real automation demos — all output saved in  [bold]output/[/][/]")
    else:
        print(banner)
        print("  Five real automation demos — all output saved in  output/\n")


# ── Demo 1: File Organizer ─────────────────────────────────────────────────────
def demo_file_organizer():
    header("Demo 1 of 5 — File Organizer")
    info("Scanning messy_folder/ containing 16 mixed file types ...")
    pause()

    messy_path = DATA / "messy_folder"
    if not messy_path.exists():
        console.print("  [red]⚠  sample_data/messy_folder not found — run setup_demo.py first[/]")
        return

    # Copy files so the demo is repeatable
    import shutil
    demo_folder = OUTPUT / "organized"
    if demo_folder.exists():
        shutil.rmtree(demo_folder)
    shutil.copytree(str(messy_path), str(demo_folder))

    result = organize_folder(str(demo_folder))
    pause()

    success("Files organised!", f"({result['total']} files sorted)")
    for category, count in sorted(result["summary"].items()):
        kv(f"  📁 {category}", f"{count} file{'s' if count != 1 else ''}")

    info(f"Result saved to  output/organized/")


# ── Demo 2: Data Merger ────────────────────────────────────────────────────────
def demo_data_merger():
    header("Demo 2 of 5 — CSV / Excel Merger")
    info("Merging 3 monthly sales files into one master CSV ...")
    pause()

    files = [str(DATA / f) for f in ["sales_jan.csv", "sales_feb.csv", "sales_mar.csv"]]
    missing = [f for f in files if not Path(f).exists()]
    if missing:
        console.print(f"  [red]⚠  Missing files — run setup_demo.py first[/]")
        return

    out = str(OUTPUT / "sales_merged.csv")
    result = merge_csv_files(files, out, drop_duplicates=True, sort_by="date")
    pause()

    success("Merge complete!", f"→  output/sales_merged.csv")
    kv("Files merged",          result["files_merged"])
    kv("Total rows (before)",   result["rows_before"])
    kv("Total rows (after)",    result["rows_after"])
    kv("Duplicates removed",    result["duplicates_removed"])
    kv("Columns",               ", ".join(c for c in result["columns"] if not c.startswith("_")))


# ── Demo 3: Data Cleaner ───────────────────────────────────────────────────────
def demo_data_cleaner():
    header("Demo 3 of 5 — Data Cleaner")
    info("Cleaning messy_contacts.csv (bad capitalisation, duplicates, phones) ...")
    pause()

    inp = DATA / "messy_contacts.csv"
    if not inp.exists():
        console.print("  [red]⚠  sample_data/messy_contacts.csv not found — run setup_demo.py first[/]")
        return

    out = str(OUTPUT / "contacts_clean.csv")
    result = clean_contacts(str(inp), out)
    pause()

    success("Cleaning done!", f"→  output/contacts_clean.csv")
    kv("Rows in raw file",      result["rows_before"])
    kv("Blank rows removed",    result["blanks_removed"])
    kv("Duplicates removed",    result["duplicates_removed"])
    kv("Rows in clean file",    result["rows_after"])
    kv("Columns cleaned",       ", ".join(result["columns_cleaned"]))

    # Show before/after snippet
    info("")
    info("Before → After  (name column)")
    examples = [
        ("  priya mehta  ",  "Priya Mehta"),
        ("RAVI SHARMA",      "Ravi Sharma"),
        ("anita joshi",      "Anita Joshi"),
    ]
    for before, after in examples:
        if RICH:
            console.print(f"     [red]{before!r:<26}[/] →  [green]{after}[/]")
        else:
            print(f"     {before!r:<26} →  {after}")


# ── Demo 4: Report Generator ───────────────────────────────────────────────────
def demo_report_generator():
    header("Demo 4 of 5 — HTML Sales Report Generator")
    info("Reading merged sales data and building a styled HTML report ...")
    pause()

    inp = OUTPUT / "sales_merged.csv"
    if not inp.exists():
        console.print("  [yellow]⚠  Run Demo 2 first (sales_merged.csv not found) — generating from Jan only.[/]")
        inp = DATA / "sales_jan.csv"

    out = str(OUTPUT / "sales_report.html")
    result = generate_sales_report(str(inp), out)
    pause()

    success("Report generated!", f"→  output/sales_report.html  (open in browser)")
    kv("Total Revenue",   f"₹{result['total_revenue']:,.0f}")
    kv("Total Orders",    result["total_orders"])
    kv("Top Salesperson", result["top_person"])
    kv("Best Product",    result["best_product"])
    info("The HTML file is self-contained — share it as-is or email it.")


# ── Demo 5: Email Sender ───────────────────────────────────────────────────────
def demo_email_sender():
    header("Demo 5 of 5 — Automated Email Sender")
    info("Sending a personalised email with the report attached  [demo_mode=True] ...")
    pause()

    attachment = OUTPUT / "sales_report.html"
    result = send_email(
        sender_email     = "your.email@gmail.com",
        sender_password  = "your-app-password",     # not used in demo_mode
        recipient_email  = "client@example.com",
        subject          = "Your Weekly Sales Report is Ready",
        body             = (
            "Hi there,\n\n"
            "Please find your automated weekly sales report attached.\n\n"
            "Key highlights this week:\n"
            "  • Total Revenue  : ₹4,32,500\n"
            "  • Top Performer  : Alice Sharma\n"
            "  • Best Product   : Laptop Pro\n\n"
            "This report is auto-generated every Monday morning.\n\n"
            "Regards,\n"
            "BusinessAutoKit — built by Vinesh"
        ),
        attachments      = [str(attachment)] if attachment.exists() else [],
        demo_mode        = True,   # ← change to False + real credentials to actually send
    )
    pause()

    success("Email preview shown above  (demo_mode=True — nothing was sent)")
    kv("To",          ", ".join(result["to"]))
    kv("Subject",     result["subject"])
    kv("Attachments", len(result["attachments"]))
    info("Set  demo_mode=False  + real SMTP credentials to actually send.")


# ── Summary ───────────────────────────────────────────────────────────────────
def print_summary():
    if RICH:
        console.print()
        console.rule("[bold green]All demos complete![/]")
        t = Table(title="Output files created", show_header=True, header_style="bold cyan")
        t.add_column("File",        style="dim")
        t.add_column("Description")
        t.add_row("output/organized/",         "Files sorted into typed subfolders")
        t.add_row("output/sales_merged.csv",   "3 monthly sales files combined")
        t.add_row("output/contacts_clean.csv", "Cleaned and de-duplicated contacts")
        t.add_row("output/sales_report.html",  "Standalone HTML report — open in browser")
        console.print(t)
        console.print()
        console.print(Panel(
            "[bold]These are the kinds of tasks I build for clients on Fiverr.[/]\n"
            "Each demo above is a real, working module — not a mockup.\n\n"
            "[dim]→ Message me to discuss your automation need.[/]",
            title="[bold green]About BusinessAutoKit[/]",
            expand=False,
        ))
    else:
        print("\n" + "="*60)
        print("  All demos complete!")
        print("  Output files:")
        print("    output/organized/          — sorted files")
        print("    output/sales_merged.csv    — merged data")
        print("    output/contacts_clean.csv  — cleaned contacts")
        print("    output/sales_report.html   — open in browser!")
        print("="*60)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not DATA.exists() or not list(DATA.iterdir()):
        print("Sample data not found. Run  python setup_demo.py  first.")
        sys.exit(1)

    print_banner()
    pause(1)

    demo_file_organizer()
    pause()
    demo_data_merger()
    pause()
    demo_data_cleaner()
    pause()
    demo_report_generator()
    pause()
    demo_email_sender()

    print_summary()
