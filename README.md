# BusinessAutoKit — Python Automation Toolkit

> A portfolio project by **Vinesh** demonstrating five real-world business automation scripts built in Python.

---

## What this project shows

| # | Demo | What it does | Module |
|---|------|-------------|--------|
| 1 | **File Organizer** | Scans a folder full of mixed files and moves every file into the right subfolder (Images, Documents, Data, Code…) automatically | `modules/file_organizer.py` |
| 2 | **Data Merger** | Reads three monthly sales CSVs, stacks them, removes any duplicates, and saves one clean master file | `modules/data_merger.py` |
| 3 | **Data Cleaner** | Fixes bad capitalisation, extra spaces, inconsistent phone formats and duplicate rows in a messy contacts spreadsheet | `modules/data_cleaner.py` |
| 4 | **Report Generator** | Builds a beautiful, self-contained HTML sales report with summary cards, a leaderboard and a monthly trend table | `modules/report_generator.py` |
| 5 | **Email Sender** | Sends personalised emails with attachments via SMTP; supports bulk sending with name templates | `modules/email_sender.py` |

---

## Quick start

```
pip install -r requirements.txt
python setup_demo.py     ← creates sample data (run once)
python run_demo.py       ← runs all five demos
```

Open `output/sales_report.html` in your browser to see the generated report.

---

## Project structure

```
BusinessAutoKit/
├── run_demo.py          ← Entry point — runs all demos
├── setup_demo.py        ← Generates sample / test data
├── requirements.txt
│
├── modules/
│   ├── file_organizer.py
│   ├── data_merger.py
│   ├── data_cleaner.py
│   ├── report_generator.py
│   └── email_sender.py
│
├── sample_data/         ← created by setup_demo.py
│   ├── messy_folder/    (16 mixed file types)
│   ├── sales_jan.csv
│   ├── sales_feb.csv
│   ├── sales_mar.csv
│   └── messy_contacts.csv
│
└── output/              ← all results land here
    ├── organized/
    ├── sales_merged.csv
    ├── contacts_clean.csv
    └── sales_report.html
```

---

## Using individual modules in your own script

```python
# Organise a folder
from modules.file_organizer import organize_folder
result = organize_folder("C:/Downloads/MyFolder")
print(result["summary"])   # {'Images': 5, 'Documents': 3, ...}

# Merge CSVs
from modules.data_merger import merge_csv_files
result = merge_csv_files(
    ["jan.csv", "feb.csv", "mar.csv"],
    output_path="merged.csv",
    sort_by="date"
)

# Clean messy data
from modules.data_cleaner import clean_contacts
result = clean_contacts("raw_contacts.csv", "clean_contacts.csv")
print(f"Removed {result['duplicates_removed']} duplicates")

# Generate HTML report
from modules.report_generator import generate_sales_report
generate_sales_report("sales.csv", "report.html")

# Send an email (set demo_mode=False for real sending)
from modules.email_sender import send_email
send_email(
    sender_email    = "you@gmail.com",
    sender_password = "your-app-password",
    recipient_email = "client@example.com",
    subject         = "Weekly Report",
    body            = "Hi, please find your report attached.",
    attachments     = ["report.html"],
    demo_mode       = True,   # ← preview only
)
```

---

## About the author

Hi, I am **Vinesh** — a B.Tech IT engineer from Mumbai. I build Python automation and AI tools that save small businesses hours of repetitive work every week.

- Certified: **AWS Cloud Practitioner**, **Google Gemini**, **Claude AI**
- Experience: multi-agent AI (LangGraph), automation scripts, data pipelines
- Fiverr: fast delivery, clear English, clean code with comments

**Ready to automate your workflow?** Message me on Fiverr and describe what you want automated — I will tell you honestly whether it fits the package and how long it will take.
