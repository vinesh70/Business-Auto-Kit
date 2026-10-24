"""
Email Sender
Sends personalised emails with optional file attachments via SMTP.
Supports Gmail, Outlook and any standard SMTP server.
Use DEMO_MODE=True to preview emails without actually sending them.
"""
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime


def send_email(
    sender_email: str,
    sender_password: str,
    recipient_email: str | list[str],
    subject: str,
    body: str,
    html_body: str | None = None,
    attachments: list[str] | None = None,
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 465,
    demo_mode: bool = True,
) -> dict:
    """
    Send an email (with optional attachments) via SMTP.

    Args:
        sender_email:     Your email address.
        sender_password:  App password (Gmail) or SMTP password.
        recipient_email:  One address or a list of addresses.
        subject:          Email subject line.
        body:             Plain-text email body.
        attachments:      List of file paths to attach (optional).
        smtp_host:        SMTP server — defaults to Gmail.
        smtp_port:        SSL port — defaults to 465.
        demo_mode:        If True, print preview and skip actual sending.

    Returns:
        {"sent": bool, "to": list, "subject": str, "attachments": list, "timestamp": str}
    """
    recipients = [recipient_email] if isinstance(recipient_email, str) else recipient_email
    attachments = attachments or []

    # Build the message object (always, even in demo mode)
    msg = EmailMessage()
    msg["From"]    = sender_email
    msg["To"]      = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    for path_str in attachments:
        p = Path(path_str)
        if not p.exists():
            raise FileNotFoundError(f"Attachment not found: {path_str}")
        msg.add_attachment(
            p.read_bytes(),
            maintype="application",
            subtype="octet-stream",
            filename=p.name,
        )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if demo_mode:
        # ─── DEMO — show what would be sent ───────────────────────────────
        border = "─" * 60
        print(f"\n{border}")
        print("  📧  EMAIL PREVIEW  (demo_mode=True — nothing was sent)")
        print(border)
        print(f"  From    : {sender_email}")
        print(f"  To      : {', '.join(recipients)}")
        print(f"  Subject : {subject}")
        if attachments:
            names = ", ".join(Path(a).name for a in attachments)
            print(f"  Attach  : {names}")
        print(border)
        print(body)
        print(border)
        return {"sent": False, "demo_mode": True, "to": recipients,
                "subject": subject, "attachments": attachments, "timestamp": timestamp}

    # ─── REAL SEND ────────────────────────────────────────────────────────
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

    return {"sent": True, "demo_mode": False, "to": recipients,
            "subject": subject, "attachments": attachments, "timestamp": timestamp}


# ── Convenience helpers ───────────────────────────────────────────────────────

def send_bulk_email(
    sender_email: str,
    sender_password: str,
    contacts: list[dict],
    subject_template: str,
    body_template: str,
    attachment: str | None = None,
    demo_mode: bool = True,
) -> list[dict]:
    """
    Send personalised emails to a list of contacts.

    Each contact dict may contain any keys; use {key} placeholders in
    subject_template and body_template.

    Example:
        contacts = [
            {"name": "Priya", "email": "priya@example.com", "company": "ABC Ltd"},
        ]
        subject_template = "Hello {name}, your report is ready"
        body_template    = "Hi {name},\\n\\nPlease find attached your report for {company}.\\n\\nRegards"
    """
    results = []
    for contact in contacts:
        subject = subject_template.format(**contact)
        body    = body_template.format(**contact)
        result  = send_email(
            sender_email=sender_email,
            sender_password=sender_password,
            recipient_email=contact["email"],
            subject=subject,
            body=body,
            attachments=[attachment] if attachment else [],
            demo_mode=demo_mode,
        )
        results.append(result)
    return results
