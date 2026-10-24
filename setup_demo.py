"""
setup_demo.py
Creates all sample data needed to run the five automation demos.
Run this ONCE before running run_demo.py.
"""
import csv
import os
import random
from pathlib import Path
from datetime import date, timedelta

BASE = Path(__file__).parent
DATA = BASE / "sample_data"
DATA.mkdir(exist_ok=True)
(BASE / "output").mkdir(exist_ok=True)

# ─── 1. Create a messy folder for the File Organizer demo ─────────────────────
MESSY = DATA / "messy_folder"
MESSY.mkdir(exist_ok=True)

messy_files = [
    # Images
    "team_photo.jpg", "product_banner.png", "logo_v2.svg",
    # Documents
    "Project_Proposal.docx", "Meeting_Notes.pdf", "Q1_Goals.txt",
    # Data
    "customers_export.csv", "inventory.xlsx", "leads_2024.json",
    # Code
    "send_report.py", "dashboard.html", "styles.css",
    # Archives
    "old_backup.zip", "assets_v1.rar",
    # Misc
    "Thumbs.db", "random_file.xyz",
]
for name in messy_files:
    f = MESSY / name
    if not f.exists():
        f.write_text(f"Sample content for {name}\n")

print("✔  Created  sample_data/messy_folder/  with 16 mixed files")


# ─── 2. Sales CSVs for Jan, Feb, Mar (Data Merger + Report demos) ─────────────
PRODUCTS = ["Laptop Pro", "Wireless Mouse", "USB-C Hub", "Mechanical Keyboard",
            "Monitor 27\"", "Webcam HD", "External SSD"]
SALESPERSONS = ["Alice Sharma", "Ravi Mehta", "Priya Nair",
                "Sameer Khan", "Anita Joshi"]
REGIONS = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"]

def random_date(year: int, month: int) -> str:
    first = date(year, month, 1)
    last  = date(year, month, 28)
    return (first + timedelta(days=random.randint(0, (last-first).days))).isoformat()

random.seed(42)  # reproducible data
for month_num, month_name in enumerate(["sales_jan", "sales_feb", "sales_mar"], start=1):
    rows = []
    for _ in range(30):
        product    = random.choice(PRODUCTS)
        salesperson= random.choice(SALESPERSONS)
        region     = random.choice(REGIONS)
        qty        = random.randint(1, 5)
        prices     = {"Laptop Pro": 45000, "Wireless Mouse": 1200, "USB-C Hub": 2500,
                      "Mechanical Keyboard": 4500, 'Monitor 27"': 18000,
                      "Webcam HD": 3800, "External SSD": 6500}
        unit_price = prices[product]
        total      = qty * unit_price
        rows.append([
            random_date(2024, month_num), product, salesperson,
            region, qty, unit_price, total
        ])

    csv_path = DATA / f"{month_name}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "product", "salesperson", "region",
                         "quantity", "unit_price", "total"])
        writer.writerows(rows)

print("✔  Created  sample_data/sales_jan.csv, sales_feb.csv, sales_mar.csv")


# ─── 3. Messy contacts CSV for Data Cleaner demo ──────────────────────────────
messy_contacts = [
    ["name",               "email",                       "phone",           "city"],
    ["  priya mehta  ",    "priya.mehta@gmail.com",       "9876543210",      "mumbai"],
    ["RAVI SHARMA",        "RAVI.SHARMA@GMAIL.COM",       "+91-98765-43211", "Delhi  "],
    ["anita joshi",        "anita.joshi@outlook.com",     "9123456789",      "BANGALORE"],
    ["  priya mehta  ",    "priya.mehta@gmail.com",       "9876543210",      "mumbai"],  # duplicate
    ["SAMEER KHAN",        "sameer.khan@yahoo.com",       "091-77889-90011", "Hyderabad"],
    ["Rohan  Verma",       "ROHAN.VERMA@GMAIL.COM",       "8899001122",      "CHENNAI"],
    ["",                   "",                            "",                ""],        # blank row
    ["neha kapoor",        "neha@company.co.in",          "+917654321098",   "pune"],
    ["ANITA JOSHI",        "anita.joshi@outlook.com",     "9123456789",      "bangalore"],  # duplicate
    ["vikram singh",       "vikram.singh@gmail.com",      "9000011112",      "JAIPUR  "],
    ["meena patel",        "Meena.Patel@Gmail.Com",       "91 84567 89012",  "Ahmedabad"],
    ["ROHAN VERMA",        "rohan.verma@gmail.com",       "8899001122",      "chennai"],  # duplicate
    ["kavita desai",       "kavita@designstudio.in",      "7766554433",      "  Mumbai"],
    ["",                   "ghost@example.com",           "",                ""],        # mostly blank
]
csv_path = DATA / "messy_contacts.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(messy_contacts)

print("✔  Created  sample_data/messy_contacts.csv  (with duplicates, bad formatting)")


# ─── 4. Sample report attachment for Email demo ────────────────────────────────
sample_report = DATA / "weekly_summary.txt"
sample_report.write_text(
    "WEEKLY SALES SUMMARY\n"
    "====================\n"
    "Week of 2024-01-22\n\n"
    "Total Revenue   : ₹4,32,500\n"
    "Orders Processed: 47\n"
    "Top Product     : Laptop Pro\n"
    "Top Salesperson : Alice Sharma\n\n"
    "Generated by BusinessAutoKit.\n",
    encoding="utf-8",
)
print("✔  Created  sample_data/weekly_summary.txt  (email attachment sample)")
print()
print("All sample data ready.  Run  'python run_demo.py'  to start the demos.")
