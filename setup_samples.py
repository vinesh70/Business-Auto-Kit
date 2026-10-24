"""
setup_samples.py
Creates sample data in separate folders for each of the 5 demos.
Run this ONCE before starting the web app.
"""
import csv, random
from datetime import date, timedelta
from pathlib import Path

BASE   = Path(__file__).parent
SAMPLE = BASE / "sample_data"
random.seed(42)

# ─── Demo 1: File Organizer ───────────────────────────────────────────────────
D1 = SAMPLE / "demo1_organizer"
D1.mkdir(parents=True, exist_ok=True)

messy_files = {
    # Images
    "team_photo_2024.jpg":      "JPEG image data",
    "product_banner_v3.png":    "PNG image data",
    "company_logo.svg":         "<svg>logo</svg>",
    # Documents
    "Project_Proposal_Q1.docx": "Word document",
    "Client_Meeting_Notes.pdf": "PDF content",
    "Employee_Handbook.txt":    "Company policies and guidelines.",
    # Data
    "customers_export.csv":     "id,name,email\n1,Alice,alice@a.com",
    "inventory_jan.xlsx":       "Excel binary",
    "leads_pipeline.json":      '{"leads": [{"name":"Ravi","score":90}]}',
    # Videos
    "product_demo.mp4":         "MP4 video data",
    # Audio
    "team_standup.mp3":         "MP3 audio data",
    # Archives
    "website_backup_jan.zip":   "PK ZIP archive",
    "old_assets_v1.rar":        "RAR archive",
    # Code
    "send_weekly_report.py":    "import smtplib\n# automation script",
    "dashboard.html":           "<!DOCTYPE html><html>Dashboard</html>",
    # Other
    "random_notes.xyz":         "unknown file type",
}

for name, content in messy_files.items():
    f = D1 / name
    if not f.exists():
        f.write_text(content, encoding="utf-8")

print(f"✔  demo1_organizer/  — {len(messy_files)} mixed files created")


# ─── Demo 2: Data Merger ──────────────────────────────────────────────────────
D2 = SAMPLE / "demo2_merger"
D2.mkdir(parents=True, exist_ok=True)

PRODUCTS = ["Laptop Pro", "Wireless Mouse", "USB-C Hub",
            "Mechanical Keyboard", 'Monitor 27"', "Webcam HD", "External SSD"]
PERSONS  = ["Alice Sharma", "Ravi Mehta", "Priya Nair", "Sameer Khan", "Anita Joshi"]
REGIONS  = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"]
PRICES   = {"Laptop Pro": 45000, "Wireless Mouse": 1200, "USB-C Hub": 2500,
            "Mechanical Keyboard": 4500, 'Monitor 27"': 18000,
            "Webcam HD": 3800, "External SSD": 6500}

def rand_date(year, month):
    start = date(year, month, 1)
    return (start + timedelta(days=random.randint(0, 26))).isoformat()

for m_num, m_name in [(1, "sales_jan"), (2, "sales_feb"), (3, "sales_mar")]:
    rows = []
    for _ in range(30):
        p = random.choice(PRODUCTS)
        qty = random.randint(1, 5)
        rows.append([rand_date(2024, m_num), p, random.choice(PERSONS),
                     random.choice(REGIONS), qty, PRICES[p], qty * PRICES[p]])
    with open(D2 / f"{m_name}.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(
            [["date","product","salesperson","region","quantity","unit_price","total"]] + rows
        )

print("✔  demo2_merger/      — sales_jan, sales_feb, sales_mar CSVs created")


# ─── Demo 3: Data Cleaner ─────────────────────────────────────────────────────
D3 = SAMPLE / "demo3_cleaner"
D3.mkdir(parents=True, exist_ok=True)

messy_contacts = [
    ["name",              "email",                     "phone",            "city"],
    ["  priya mehta  ",   "priya.mehta@gmail.com",     "9876543210",       "mumbai"],
    ["RAVI SHARMA",       "RAVI.SHARMA@GMAIL.COM",     "+91-98765-43211",  "Delhi  "],
    ["anita joshi",       "anita.joshi@outlook.com",   "9123456789",       "BANGALORE"],
    ["  priya mehta  ",   "priya.mehta@gmail.com",     "9876543210",       "mumbai"],   # duplicate
    ["SAMEER KHAN",       "sameer.khan@yahoo.com",     "091-77889-90011",  "Hyderabad"],
    ["Rohan  Verma",      "ROHAN.VERMA@GMAIL.COM",     "8899001122",       "CHENNAI"],
    ["",                  "",                          "",                 ""],          # blank
    ["neha kapoor",       "neha@company.co.in",        "+917654321098",    "pune"],
    ["ANITA JOSHI",       "anita.joshi@outlook.com",   "9123456789",       "bangalore"],# duplicate
    ["vikram singh",      "vikram.singh@gmail.com",    "9000011112",       "JAIPUR  "],
    ["meena patel",       "Meena.Patel@Gmail.Com",     "91 84567 89012",   "Ahmedabad"],
    ["ROHAN VERMA",       "rohan.verma@gmail.com",     "8899001122",       "chennai"],  # duplicate
    ["kavita desai",      "kavita@designstudio.in",    "7766554433",       "  Mumbai"],
    ["",                  "ghost@example.com",         "",                 ""],          # mostly blank
]
with open(D3 / "messy_contacts.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(messy_contacts)

print("✔  demo3_cleaner/     — messy_contacts.csv created (duplicates, bad caps, messy phones)")


# ─── Demo 4: Report Generator ─────────────────────────────────────────────────
D4 = SAMPLE / "demo4_report"
D4.mkdir(parents=True, exist_ok=True)

all_rows = []
for m_num in [1, 2, 3]:
    p = D2 / f"sales_{['jan','feb','mar'][m_num-1]}.csv"
    with open(p, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        if not all_rows:
            all_rows.append(header)
        all_rows.extend(list(reader))

with open(D4 / "sales_data.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(all_rows)

print("✔  demo4_report/      — sales_data.csv created (90 rows, Jan–Mar combined)")


# ─── Demo 5: Email Automation ─────────────────────────────────────────────────
D5 = SAMPLE / "demo5_email"
D5.mkdir(parents=True, exist_ok=True)

email_contacts = [
    ["name",         "email",                     "company",          "industry",    "city"],
    ["Rahul Gupta",  "rahul.gupta@techcorp.in",   "TechCorp India",   "Software",    "Mumbai"],
    ["Priya Sharma", "priya.sharma@retail.com",   "Quick Retail",     "E-commerce",  "Delhi"],
    ["Amit Patel",   "amit.patel@finance.co",     "Prime Finance",    "Banking",     "Ahmedabad"],
    ["Neha Joshi",   "neha.joshi@startup.io",     "StartupHub",       "Technology",  "Bangalore"],
    ["Vivek Kumar",  "vivek.kumar@logistics.net", "FastLogix",        "Logistics",   "Pune"],
]
with open(D5 / "contacts.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(email_contacts)

print("✔  demo5_email/       — contacts.csv created (5 contacts for bulk email demo)")
print()
print("All sample data ready.  Run  'python app.py'  to start the web app.")
