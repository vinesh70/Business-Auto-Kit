"""
BusinessAutoKit — Web Application
Run:  python app.py
Then: http://localhost:8000
"""
import json, os, shutil, sys, threading, time, webbrowser
from pathlib import Path
from pydantic import BaseModel

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).parent))
from modules.data_cleaner     import clean_contacts
from modules.data_merger      import merge_csv_files
from modules.file_organizer   import organize_folder
from modules.report_generator import generate_sales_report
from modules.email_sender     import send_email, send_via_resend, send_via_sendgrid

BASE   = Path(__file__).parent
SAMPLE = BASE / "sample_data"
OUTPUT = BASE / "output"
STATIC = BASE / "static"
OUTPUT.mkdir(exist_ok=True)

app = FastAPI(title="BusinessAutoKit")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
app.mount("/output", StaticFiles(directory=str(OUTPUT)), name="output")


@app.get("/")
def index():
    return FileResponse(str(STATIC / "index.html"))


# ─── Sample data ──────────────────────────────────────────────────────────────

@app.get("/api/sample/organizer")
def s_organizer():
    folder = SAMPLE / "demo1_organizer"
    if not folder.exists():
        raise HTTPException(400, detail="Run setup_samples.py first")
    files = [
        {"name": f.name, "ext": f.suffix.lower(), "size": f.stat().st_size}
        for f in sorted(folder.iterdir()) if f.is_file()
    ]
    return {"files": files, "count": len(files)}


@app.get("/api/sample/merger")
def s_merger():
    out = {}
    for name in ["sales_jan", "sales_feb", "sales_mar"]:
        p = SAMPLE / "demo2_merger" / f"{name}.csv"
        if p.exists():
            df = pd.read_csv(p)
            out[name] = {"rows": len(df), "columns": list(df.columns),
                         "preview": df.head(5).to_dict(orient="records")}
    if not out:
        raise HTTPException(400, detail="Run setup_samples.py first")
    return out


@app.get("/api/sample/cleaner")
def s_cleaner():
    p = SAMPLE / "demo3_cleaner" / "messy_contacts.csv"
    if not p.exists():
        raise HTTPException(400, detail="Run setup_samples.py first")
    df = pd.read_csv(p, dtype=str).fillna("")
    return {"rows": len(df), "columns": list(df.columns), "preview": df.to_dict(orient="records")}


@app.get("/api/sample/report")
def s_report():
    p = SAMPLE / "demo4_report" / "sales_data.csv"
    if not p.exists():
        raise HTTPException(400, detail="Run setup_samples.py first")
    df = pd.read_csv(p)
    return {
        "rows": len(df), "columns": list(df.columns),
        "preview": df.head(6).to_dict(orient="records"),
        "total_revenue": float(df["total"].astype(float).sum()),
    }


@app.get("/api/sample/email")
def s_email():
    p = SAMPLE / "demo5_email" / "contacts.csv"
    if not p.exists():
        raise HTTPException(400, detail="Run setup_samples.py first")
    df = pd.read_csv(p, dtype=str).fillna("")
    return {"rows": len(df), "columns": list(df.columns), "preview": df.to_dict(orient="records")}


# ─── Run demos ────────────────────────────────────────────────────────────────

@app.post("/api/run/organizer")
def run_organizer():
    src  = SAMPLE / "demo1_organizer"
    dest = OUTPUT / "organized"
    if not src.exists():
        raise HTTPException(400, detail="Run setup_samples.py first")
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(str(src), str(dest))
    result = organize_folder(str(dest))
    tree = {
        item.name: sorted(f.name for f in item.iterdir() if f.is_file())
        for item in sorted(dest.iterdir()) if item.is_dir()
    }
    # Size by category
    size_by_cat = {}
    total_size  = 0
    for cat_dir in dest.iterdir():
        if cat_dir.is_dir():
            cat_size = sum(f.stat().st_size for f in cat_dir.iterdir() if f.is_file())
            size_by_cat[cat_dir.name] = cat_size
            total_size += cat_size
    # Duplicate detection by filename stem across categories
    seen_stems: dict = {}
    duplicates: list = []
    for cat_dir in dest.iterdir():
        if cat_dir.is_dir():
            for f in cat_dir.iterdir():
                if f.is_file():
                    stem = f.stem.lower()
                    if stem in seen_stems:
                        duplicates.append(f.name)
                    else:
                        seen_stems[stem] = f.name
    return {
        **result, "tree": tree,
        "size_by_category": size_by_cat,
        "total_size": total_size,
        "duplicates": duplicates,
    }


@app.post("/api/run/merger")
def run_merger():
    fnames = ["sales_jan.csv", "sales_feb.csv", "sales_mar.csv"]
    files  = [str(SAMPLE / "demo2_merger" / f) for f in fnames]
    if not all(Path(f).exists() for f in files):
        raise HTTPException(400, detail="Run setup_samples.py first")
    out = str(OUTPUT / "sales_merged.csv")
    # Per-file stats before merging
    per_file_stats = []
    for fname in fnames:
        p   = SAMPLE / "demo2_merger" / fname
        df_f = pd.read_csv(p)
        revenue = float(df_f["total"].astype(float).sum()) if "total" in df_f.columns else 0
        nulls   = int(df_f.isnull().sum().sum())
        per_file_stats.append({
            "name":    fname.replace(".csv", "").replace("sales_", "").capitalize(),
            "rows":    len(df_f),
            "revenue": revenue,
            "nulls":   nulls,
        })
    result = merge_csv_files(files, out, drop_duplicates=True, sort_by="date")
    df   = pd.read_csv(out)
    cols = [c for c in df.columns if not c.startswith("_")]
    return {
        **result,
        "preview": df[cols].head(10).to_dict(orient="records"),
        "columns": cols,
        "per_file_stats": per_file_stats,
    }


@app.post("/api/run/cleaner")
def run_cleaner():
    inp = SAMPLE / "demo3_cleaner" / "messy_contacts.csv"
    if not inp.exists():
        raise HTTPException(400, detail="Run setup_samples.py first")
    messy = pd.read_csv(inp, dtype=str).fillna("")
    out = str(OUTPUT / "contacts_clean.csv")
    result = clean_contacts(str(inp), out)
    clean = pd.read_csv(out, dtype=str).fillna("")
    return {**result, "before": messy.to_dict(orient="records"), "after": clean.to_dict(orient="records")}


@app.post("/api/run/report")
def run_report():
    inp = SAMPLE / "demo4_report" / "sales_data.csv"
    if not inp.exists():
        fallback = OUTPUT / "sales_merged.csv"
        inp = fallback if fallback.exists() else None
    if inp is None:
        raise HTTPException(400, detail="Run setup_samples.py first")
    out    = str(OUTPUT / "sales_report.html")
    result = generate_sales_report(str(inp), out)
    return {**result, "report_url": "/output/sales_report.html"}


@app.post("/api/run/email")
def run_email():
    p = SAMPLE / "demo5_email" / "contacts.csv"
    if not p.exists():
        raise HTTPException(400, detail="Run setup_samples.py first")
    contacts = pd.read_csv(p, dtype=str).fillna("").to_dict(orient="records")[:5]
    results = []
    for c in contacts:
        r = send_email(
            sender_email    = "vinesh@businessautokit.com",
            sender_password = "demo",
            recipient_email = c.get("email", ""),
            subject         = f"Your Weekly Report is Ready, {c.get('name','there')}!",
            body            = (
                f"Hi {c.get('name','there')},\n\n"
                f"Your automated report for {c.get('company','your company')} is ready.\n\n"
                "Highlights this week:\n"
                "  • Revenue up 12% vs last week\n"
                "  • 5 new enquiries received\n"
                "  • Best product: Laptop Pro\n\n"
                "This email is auto-generated every Monday morning.\n\n"
                "Regards,\nVinesh | BusinessAutoKit"
            ),
            demo_mode=True,
        )
        results.append({
            "to": c.get("email"), "name": c.get("name"),
            "company": c.get("company",""), "subject": r["subject"],
        })
    return {"emails_prepared": len(results), "results": results}


@app.get("/api/download/{filename}")
def download(filename: str):
    safe = Path(filename).name
    f = OUTPUT / safe
    if not f.exists():
        raise HTTPException(404)
    return FileResponse(str(f), filename=safe)


# ─── Email config ─────────────────────────────────────────────────────────────

EMAIL_CFG = BASE / "email_config.json"

class EmailConfigIn(BaseModel):
    sender_email: str
    sender_password: str
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465

class SendTestIn(BaseModel):
    recipient_email: str

def _load_cfg() -> dict:
    if EMAIL_CFG.exists():
        return json.loads(EMAIL_CFG.read_text(encoding="utf-8"))
    return {"configured": False}

@app.get("/api/config/email")
def get_email_config():
    cfg       = _load_cfg()
    sg_key    = os.environ.get("SENDGRID_API_KEY") or cfg.get("sendgrid_api_key")
    resend_key= os.environ.get("RESEND_API_KEY")   or cfg.get("resend_api_key")
    api_active = bool(sg_key or resend_key)
    provider   = "SendGrid" if sg_key else ("Resend" if resend_key else None)
    return {
        "configured":    cfg.get("configured", False) or api_active,
        "sender_email":  cfg.get("sender_email", ""),
        "resend_active": api_active,
        "provider":      provider,
    }

@app.post("/api/config/email")
def save_email_config(data: EmailConfigIn):
    cfg = {"configured": True, "sender_email": data.sender_email,
           "sender_password": data.sender_password,
           "smtp_host": data.smtp_host, "smtp_port": data.smtp_port}
    EMAIL_CFG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return {"success": True, "sender_email": data.sender_email}

@app.post("/api/send-test-email")
def send_test_email(data: SendTestIn):
    cfg = _load_cfg()
    if not cfg.get("configured"):
        raise HTTPException(400, detail="Email not configured. Fill in your Gmail settings first.")
    plain = (
        "Hi there!\n\n"
        "This email was sent automatically by Python — a live demo from BusinessAutoKit.\n\n"
        "What you just witnessed:\n"
        "  ✅  Python reading a contacts list (CSV/Excel)\n"
        "  ✅  Auto-filling names and subjects from a spreadsheet\n"
        "  ✅  Sending personalised emails via Gmail SMTP (SSL)\n"
        "  ✅  Can run on a schedule — daily, weekly, or on a trigger\n\n"
        "This is exactly the kind of automation I build for clients on Fiverr.\n"
        "Whether it's 1 email or 5,000 — the script handles it all.\n\n"
        "Regards,\nVinesh\nPython Automation Developer | Fiverr\nAWS Certified | LangGraph | AI Automation"
    )
    html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F1F5F9;padding:40px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

  <!-- Header -->
  <tr><td style="background:linear-gradient(135deg,#4F46E5 0%,#7C3AED 100%);border-radius:16px 16px 0 0;padding:44px 40px 36px;text-align:center;">
    <div style="font-size:42px;margin-bottom:10px;">🚀</div>
    <h1 style="color:#ffffff;margin:0;font-size:26px;font-weight:800;letter-spacing:-0.03em;">BusinessAutoKit</h1>
    <p style="color:#C4B5FD;margin:8px 0 0;font-size:13px;font-weight:500;letter-spacing:0.04em;text-transform:uppercase;">Python Automation · Live Demo</p>
  </td></tr>

  <!-- Body -->
  <tr><td style="background:#ffffff;padding:40px;">
    <h2 style="color:#1E293B;font-size:20px;font-weight:700;margin:0 0 8px;letter-spacing:-0.02em;">This email was just sent by Python. ⚡</h2>
    <p style="color:#64748B;font-size:14px;line-height:1.7;margin:0 0 28px;">You are looking at a fully automated email, generated and delivered in real time — no manual work, no copy-paste, just code running on a schedule.</p>

    <!-- Automation steps -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
      <tr><td style="background:#F8FAFF;border:1px solid #E0E7FF;border-radius:12px;padding:24px;">
        <p style="color:#4F46E5;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin:0 0 16px;">What happened in the background</p>
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td width="28" style="vertical-align:top;padding-bottom:14px;"><span style="display:inline-block;background:#D1FAE5;color:#059669;border-radius:50%;width:22px;height:22px;text-align:center;font-size:12px;line-height:22px;font-weight:700;">1</span></td>
            <td style="padding-bottom:14px;padding-left:10px;"><span style="color:#1E293B;font-size:13.5px;font-weight:600;">Read contacts list</span><br><span style="color:#64748B;font-size:12.5px;">Python loaded your CSV — name, email, company, all in one go</span></td>
          </tr>
          <tr>
            <td width="28" style="vertical-align:top;padding-bottom:14px;"><span style="display:inline-block;background:#D1FAE5;color:#059669;border-radius:50%;width:22px;height:22px;text-align:center;font-size:12px;line-height:22px;font-weight:700;">2</span></td>
            <td style="padding-bottom:14px;padding-left:10px;"><span style="color:#1E293B;font-size:13.5px;font-weight:600;">Personalised each email</span><br><span style="color:#64748B;font-size:12.5px;">Subject, greeting and body auto-filled from the spreadsheet data</span></td>
          </tr>
          <tr>
            <td width="28" style="vertical-align:top;padding-bottom:14px;"><span style="display:inline-block;background:#D1FAE5;color:#059669;border-radius:50%;width:22px;height:22px;text-align:center;font-size:12px;line-height:22px;font-weight:700;">3</span></td>
            <td style="padding-bottom:14px;padding-left:10px;"><span style="color:#1E293B;font-size:13.5px;font-weight:600;">Sent via Gmail SMTP (SSL)</span><br><span style="color:#64748B;font-size:12.5px;">Secure encrypted connection — same as any professional email tool</span></td>
          </tr>
          <tr>
            <td width="28" style="vertical-align:top;"><span style="display:inline-block;background:#D1FAE5;color:#059669;border-radius:50%;width:22px;height:22px;text-align:center;font-size:12px;line-height:22px;font-weight:700;">4</span></td>
            <td style="padding-left:10px;"><span style="color:#1E293B;font-size:13.5px;font-weight:600;">Runs on a schedule</span><br><span style="color:#64748B;font-size:12.5px;">Set it once — Python sends every Monday at 9 AM automatically</span></td>
          </tr>
        </table>
      </td></tr>
    </table>

    <!-- Stats row -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
      <tr>
        <td width="33%" style="text-align:center;background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:16px 8px;">
          <div style="font-size:24px;font-weight:800;color:#059669;">500+</div>
          <div style="font-size:11px;color:#64748B;margin-top:3px;">emails per run</div>
        </td>
        <td width="4%"></td>
        <td width="33%" style="text-align:center;background:#EEF2FF;border:1px solid #C7D2FE;border-radius:10px;padding:16px 8px;">
          <div style="font-size:24px;font-weight:800;color:#4F46E5;">&lt; 2 min</div>
          <div style="font-size:11px;color:#64748B;margin-top:3px;">to send 1,000 emails</div>
        </td>
        <td width="4%"></td>
        <td width="33%" style="text-align:center;background:#FFF7ED;border:1px solid #FED7AA;border-radius:10px;padding:16px 8px;">
          <div style="font-size:24px;font-weight:800;color:#EA580C;">100%</div>
          <div style="font-size:11px;color:#64748B;margin-top:3px;">personalised, not bulk</div>
        </td>
      </tr>
    </table>

    <p style="color:#64748B;font-size:13.5px;line-height:1.7;margin:0 0 24px;">This is exactly what I build for clients — email automation, data pipelines, Excel/PDF report generators, WhatsApp bots and more. <strong style="color:#1E293B;">If you need this for your business, I'm one message away.</strong></p>

    <!-- CTA -->
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr><td align="center">
        <a href="https://www.fiverr.com" style="display:inline-block;background:linear-gradient(135deg,#4F46E5,#7C3AED);color:#ffffff;text-decoration:none;font-size:14px;font-weight:700;padding:14px 36px;border-radius:10px;letter-spacing:-0.01em;">Hire Vinesh on Fiverr &rarr;</a>
      </td></tr>
    </table>
  </td></tr>

  <!-- Footer -->
  <tr><td style="background:#F8FAFC;border:1px solid #E2E8F0;border-top:none;border-radius:0 0 16px 16px;padding:28px 40px;text-align:center;">
    <p style="color:#94A3B8;font-size:12px;margin:0 0 6px;"><strong style="color:#475569;">Vinesh</strong> &nbsp;·&nbsp; Python Automation Developer &nbsp;·&nbsp; Fiverr</p>
    <p style="color:#CBD5E1;font-size:11px;margin:0;">AWS Certified &nbsp;·&nbsp; LangGraph &nbsp;·&nbsp; AI Automation &nbsp;·&nbsp; B.Tech IT · Mumbai</p>
    <p style="color:#E2E8F0;font-size:10px;margin:16px 0 0;">You received this because someone requested a live demo from BusinessAutoKit.</p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""
    subject     = "You just received an automated email — BusinessAutoKit Demo 🚀"
    from_addr   = cfg.get("sender_email", "")
    sg_key      = os.environ.get("SENDGRID_API_KEY") or cfg.get("sendgrid_api_key")
    resend_key  = os.environ.get("RESEND_API_KEY")   or cfg.get("resend_api_key")
    try:
        if sg_key:
            # Best for hosted: SendGrid — supports single-sender verification, no custom domain needed
            send_via_sendgrid(sg_key, from_addr, data.recipient_email, subject, html, plain)
        elif resend_key:
            # Alternative: Resend (requires verified domain for arbitrary from-address)
            send_via_resend(resend_key, from_addr, data.recipient_email, subject, html, plain)
        else:
            # Local fallback: Gmail SMTP
            send_email(
                sender_email    = cfg["sender_email"],
                sender_password = cfg["sender_password"],
                recipient_email = data.recipient_email,
                subject         = subject,
                body            = plain,
                html_body       = html,
                smtp_host       = cfg.get("smtp_host", "smtp.gmail.com"),
                smtp_port       = cfg.get("smtp_port", 465),
                demo_mode       = False,
            )
        return {"sent": True, "to": data.recipient_email,
                "message": f"Email delivered to {data.recipient_email}!",
                "subject": subject}
    except Exception as e:
        raise HTTPException(500, detail=f"Send failed: {e}")


# ─── Report export ────────────────────────────────────────────────────────────

def _report_csv():
    p = SAMPLE / "demo4_report" / "sales_data.csv"
    if p.exists():
        return p
    fb = OUTPUT / "sales_merged.csv"
    if fb.exists():
        return fb
    return None

@app.get("/api/export/pdf")
def export_pdf():
    from modules.report_exporter import generate_pdf
    src = _report_csv()
    if src is None:
        raise HTTPException(400, detail="Run the Report demo first.")
    out = str(OUTPUT / "sales_report.pdf")
    generate_pdf(str(src), out)
    return FileResponse(out, filename="sales_report.pdf", media_type="application/pdf")

@app.get("/api/export/pptx")
def export_pptx():
    from modules.report_exporter import generate_pptx
    src = _report_csv()
    if src is None:
        raise HTTPException(400, detail="Run the Report demo first.")
    out = str(OUTPUT / "sales_report.pptx")
    generate_pptx(str(src), out)
    return FileResponse(
        out, filename="sales_report.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")


if __name__ == "__main__":
    port     = int(os.environ.get("PORT", 8000))
    is_local = not os.environ.get("RENDER")
    print("\n" + "═"*52)
    print(f"  🚀  BusinessAutoKit  is  starting on port {port} ...")
    if is_local:
        print(f"  👉  Open:  http://localhost:{port}")
    print("═"*52 + "\n")
    if is_local:
        def _open():
            time.sleep(1.5)
            webbrowser.open(f"http://localhost:{port}")
        threading.Thread(target=_open, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
