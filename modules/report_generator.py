"""
Report Generator
Reads a sales CSV and produces a polished, standalone HTML report
with summary cards, top-performer table, monthly bar chart and product breakdown.
No external dependencies beyond pandas — the HTML is self-contained.
"""
from pathlib import Path
from datetime import datetime
import pandas as pd


# ── HTML template (uses .format() so {{ }} escapes real braces) ───────────────

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sales Report — {period}</title>
<style>
  :root {{
    --bg:#F0F4FF;--card:#fff;--primary:#4F46E5;--violet:#7C3AED;
    --success:#059669;--warn:#D97706;--text:#1E293B;--muted:#64748B;--border:#E2E8F0;
  }}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:'Segoe UI',Arial,sans-serif;background:var(--bg);color:var(--text);padding:24px;}}
  header{{
    background:linear-gradient(135deg,#4F46E5 0%,#7C3AED 100%);
    color:#fff;padding:32px 36px;border-radius:16px;margin-bottom:28px;
    box-shadow:0 8px 32px rgba(79,70,229,.3);
  }}
  header h1{{font-size:1.9rem;font-weight:800;letter-spacing:-.03em;}}
  header p {{font-size:.95rem;opacity:.8;margin-top:6px;}}
  .kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:28px;}}
  .kpi{{
    background:var(--card);border-radius:12px;padding:20px 22px;
    box-shadow:0 2px 12px rgba(0,0,0,.06);
    border-top:3px solid var(--primary);position:relative;overflow:hidden;
  }}
  .kpi.green{{border-color:var(--success);}}
  .kpi.orange{{border-color:var(--warn);}}
  .kpi.violet{{border-color:var(--violet);}}
  .kpi-label{{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:8px;}}
  .kpi-value{{font-size:1.9rem;font-weight:800;color:var(--text);letter-spacing:-.04em;line-height:1;}}
  .kpi-sub  {{font-size:.8rem;color:var(--muted);margin-top:5px;}}
  section{{background:var(--card);border-radius:12px;padding:24px;box-shadow:0 2px 12px rgba(0,0,0,.06);margin-bottom:22px;}}
  section h2{{font-size:1.05rem;font-weight:700;margin-bottom:18px;padding-bottom:10px;border-bottom:2px solid var(--border);display:flex;align-items:center;gap:8px;}}
  table{{width:100%;border-collapse:collapse;font-size:.88rem;}}
  th{{background:#F8FAFC;text-align:left;padding:10px 14px;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);border-bottom:2px solid var(--border);}}
  td{{padding:10px 14px;border-bottom:1px solid var(--border);}}
  tr:last-child td{{border-bottom:none;}}
  tr:hover td{{background:#F8FAFF;}}
  .rank-1 td:first-child::before{{content:"🥇 ";}}
  .rank-2 td:first-child::before{{content:"🥈 ";}}
  .rank-3 td:first-child::before{{content:"🥉 ";}}
  .badge{{display:inline-block;border-radius:20px;padding:2px 10px;font-size:.75rem;font-weight:700;}}
  .badge-blue{{background:#EEF2FF;color:var(--primary);}}
  .badge-green{{background:#D1FAE5;color:var(--success);}}
  .badge-red{{background:#FEE2E2;color:#DC2626;}}
  .bar-cell{{display:flex;align-items:center;gap:8px;}}
  .bar-track{{flex:1;max-width:120px;height:6px;background:#E2E8F0;border-radius:3px;overflow:hidden;}}
  .bar-fill{{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--primary),var(--violet));}}
  .chart-wrap{{padding:4px 0;}}
  .chart-row{{display:flex;align-items:center;gap:10px;margin-bottom:12px;}}
  .chart-month{{width:70px;font-size:.82rem;font-weight:600;color:var(--muted);text-align:right;flex-shrink:0;}}
  .chart-bar-track{{flex:1;height:22px;background:#F1F5F9;border-radius:6px;overflow:hidden;position:relative;}}
  .chart-bar-fill{{
    height:100%;border-radius:6px;
    background:linear-gradient(90deg,#4F46E5,#7C3AED);
    display:flex;align-items:center;padding-left:8px;
    font-size:.75rem;font-weight:700;color:#fff;
    transition:width .6s ease;
  }}
  .chart-growth{{width:60px;text-align:right;font-size:.78rem;font-weight:700;flex-shrink:0;}}
  .growth-pos{{color:var(--success);}}
  .growth-neg{{color:#DC2626;}}
  footer{{text-align:center;color:var(--muted);font-size:.8rem;margin-top:24px;}}
  .forecast-box{{
    background:linear-gradient(135deg,#F0FDF4,#ECFDF5);
    border:1.5px solid #A7F3D0;border-radius:10px;padding:14px 18px;
    margin-top:16px;display:flex;align-items:center;gap:12px;
  }}
  .forecast-icon{{font-size:24px;}}
  .forecast-label{{font-size:.8rem;font-weight:600;color:var(--muted);}}
  .forecast-val{{font-size:1.3rem;font-weight:800;color:var(--success);}}
</style>
</head>
<body>

<header>
  <h1>📊 Sales Performance Report</h1>
  <p>Period: {period} &nbsp;·&nbsp; Generated: {generated_on} &nbsp;·&nbsp; Built with BusinessAutoKit</p>
</header>

<div class="kpi-grid">
  <div class="kpi">
    <div class="kpi-label">Total Revenue</div>
    <div class="kpi-value">₹{total_revenue:,.0f}</div>
    <div class="kpi-sub">{total_orders} orders · ₹{avg_order:,.0f} avg</div>
  </div>
  <div class="kpi green">
    <div class="kpi-label">Best Product</div>
    <div class="kpi-value" style="font-size:1.2rem">{best_product}</div>
    <div class="kpi-sub">₹{best_product_revenue:,.0f} revenue</div>
  </div>
  <div class="kpi orange">
    <div class="kpi-label">Top Salesperson</div>
    <div class="kpi-value" style="font-size:1.2rem">{top_person}</div>
    <div class="kpi-sub">₹{top_person_revenue:,.0f} revenue</div>
  </div>
  <div class="kpi violet">
    <div class="kpi-label">Next Month Forecast</div>
    <div class="kpi-value" style="font-size:1.2rem">₹{forecast_amount:,.0f}</div>
    <div class="kpi-sub">based on trend</div>
  </div>
</div>

<section>
  <h2>📅 Monthly Revenue Trend</h2>
  <div class="chart-wrap">
    {monthly_chart}
  </div>
</section>

<section>
  <h2>🏆 Salesperson Leaderboard</h2>
  <table>
    <thead><tr><th>#</th><th>Name</th><th>Orders</th><th>Revenue</th><th>Avg/Order</th><th>Share</th></tr></thead>
    <tbody>{salesperson_rows}</tbody>
  </table>
</section>

<section>
  <h2>📦 Product Breakdown</h2>
  <table>
    <thead><tr><th>Product</th><th>Units</th><th>Revenue</th><th>Share</th></tr></thead>
    <tbody>{product_rows}</tbody>
  </table>
</section>

<footer>Auto-generated by <strong>BusinessAutoKit</strong> · Built by Vinesh · {generated_on}</footer>
</body>
</html>"""


def generate_sales_report(input_csv: str, output_html: str) -> dict:
    if not Path(input_csv).exists():
        raise FileNotFoundError(f"File not found: {input_csv}")

    df = pd.read_csv(input_csv, parse_dates=["date"])
    df["total"]    = pd.to_numeric(df["total"],    errors="coerce").fillna(0)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)

    total_revenue = float(df["total"].sum())
    total_orders  = int(len(df))
    avg_order     = total_revenue / max(total_orders, 1)

    # ── Salesperson leaderboard ───────────────────────────────────────────────
    sp = (
        df.groupby("salesperson")
          .agg(orders=("total", "count"), revenue=("total", "sum"))
          .sort_values("revenue", ascending=False)
          .reset_index()
    )
    sp["avg"] = sp["revenue"] / sp["orders"].clip(lower=1)
    top_person         = str(sp.iloc[0]["salesperson"])
    top_person_revenue = float(sp.iloc[0]["revenue"])

    rank_cls = ["rank-1", "rank-2", "rank-3"]
    sp_rows = ""
    for i, row in sp.iterrows():
        cls   = rank_cls[i] if i < 3 else ""
        share = row["revenue"] / total_revenue * 100
        sp_rows += (
            f'<tr class="{cls}">'
            f'<td>{i+1}</td><td>{row["salesperson"]}</td>'
            f'<td>{int(row["orders"])}</td>'
            f'<td>₹{row["revenue"]:,.0f}</td>'
            f'<td>₹{row["avg"]:,.0f}</td>'
            f'<td><span class="badge badge-blue">{share:.1f}%</span></td>'
            f'</tr>\n'
        )

    # ── Product breakdown ─────────────────────────────────────────────────────
    prod = (
        df.groupby("product")
          .agg(units=("quantity", "sum"), revenue=("total", "sum"))
          .sort_values("revenue", ascending=False)
          .reset_index()
    )
    best_product         = str(prod.iloc[0]["product"])
    best_product_revenue = float(prod.iloc[0]["revenue"])
    max_prod_rev         = float(prod["revenue"].max())

    prod_rows = ""
    for _, row in prod.iterrows():
        share = row["revenue"] / total_revenue * 100
        bar_w = int(row["revenue"] / max_prod_rev * 100)
        prod_rows += (
            f'<tr><td>{row["product"]}</td>'
            f'<td>{int(row["units"])}</td>'
            f'<td><div class="bar-cell">'
            f'₹{row["revenue"]:,.0f}'
            f'<div class="bar-track"><div class="bar-fill" style="width:{bar_w}%"></div></div>'
            f'</div></td>'
            f'<td><span class="badge badge-blue">{share:.1f}%</span></td>'
            f'</tr>\n'
        )

    # ── Monthly trend ─────────────────────────────────────────────────────────
    df["month"] = df["date"].dt.to_period("M")
    monthly = (
        df.groupby("month")
          .agg(orders=("total", "count"), revenue=("total", "sum"))
          .sort_index()
          .reset_index()
    )
    max_rev = float(monthly["revenue"].max())

    monthly_chart = ""
    monthly_data  = []
    for i, row in monthly.iterrows():
        rev     = float(row["revenue"])
        bar_pct = int(rev / max_rev * 100)
        growth  = None
        if i > 0:
            prev = float(monthly.iloc[i - 1]["revenue"])
            if prev > 0:
                growth = round((rev - prev) / prev * 100, 1)

        if growth is None:
            g_html  = '<span style="color:#94A3B8;font-size:.75rem">First month</span>'
            g_label = "First month"
        else:
            sign  = "+" if growth >= 0 else ""
            cls   = "growth-pos" if growth >= 0 else "growth-neg"
            g_html  = f'<span class="{cls}">{sign}{growth}%</span>'
            g_label = f"{sign}{growth}%"

        monthly_chart += (
            f'<div class="chart-row">'
            f'<span class="chart-month">{str(row["month"])}</span>'
            f'<div class="chart-bar-track">'
            f'<div class="chart-bar-fill" style="width:{bar_pct}%">'
            f'₹{rev:,.0f}</div></div>'
            f'<span class="chart-growth">{g_html}</span>'
            f'</div>\n'
        )
        monthly_data.append({
            "month":      str(row["month"]),
            "revenue":    rev,
            "orders":     int(row["orders"]),
            "growth_pct": growth,
        })

    period = f"{str(monthly['month'].iloc[0])} → {str(monthly['month'].iloc[-1])}"

    # ── Forecast (simple linear from last 2 months) ───────────────────────────
    if len(monthly_data) >= 2:
        last_rev = monthly_data[-1]["revenue"]
        prev_rev = monthly_data[-2]["revenue"]
        gr = (last_rev - prev_rev) / prev_rev if prev_rev > 0 else 0
        forecast_amount = round(last_rev * (1 + gr))
    else:
        forecast_amount = round(monthly_data[-1]["revenue"]) if monthly_data else 0

    # ── Structured data for the API response ─────────────────────────────────
    product_data = [
        {
            "product":   str(row["product"]),
            "units":     int(row["units"]),
            "revenue":   float(row["revenue"]),
            "share_pct": round(row["revenue"] / total_revenue * 100, 1),
        }
        for _, row in prod.iterrows()
    ]

    leaderboard = [
        {
            "name":      str(row["salesperson"]),
            "orders":    int(row["orders"]),
            "revenue":   float(row["revenue"]),
            "avg_order": float(row["avg"]),
        }
        for _, row in sp.iterrows()
    ]

    # ── Render and save HTML ──────────────────────────────────────────────────
    html = _HTML.format(
        period=period,
        generated_on=datetime.now().strftime("%d %b %Y, %I:%M %p"),
        total_revenue=total_revenue,
        total_orders=total_orders,
        avg_order=avg_order,
        best_product=best_product,
        best_product_revenue=best_product_revenue,
        top_person=top_person,
        top_person_revenue=top_person_revenue,
        forecast_amount=forecast_amount,
        monthly_chart=monthly_chart,
        salesperson_rows=sp_rows,
        product_rows=prod_rows,
    )

    Path(output_html).parent.mkdir(parents=True, exist_ok=True)
    Path(output_html).write_text(html, encoding="utf-8")

    return {
        "output":              output_html,
        "period":              period,
        "total_revenue":       total_revenue,
        "total_orders":        total_orders,
        "avg_order":           avg_order,
        "top_person":          top_person,
        "top_person_revenue":  top_person_revenue,
        "best_product":        best_product,
        "best_product_revenue":best_product_revenue,
        "forecast_amount":     forecast_amount,
        "monthly_data":        monthly_data,
        "product_data":        product_data,
        "leaderboard":         leaderboard,
    }
