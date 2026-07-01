"""
PRINT_QUERIES.py
"""
import sqlite3
from textwrap import shorten
from pathlib import Path
import csv
import datetime
import argparse
import re

PRINT_QUERIES = {
    "Q7_daily_txn_volume_by_branch": """
    WITH recent AS (
        SELECT a.branch_id,
               date(t.ts) AS day,
               COUNT(*) AS txn_count,
               ROUND(SUM(t.amount), 2) AS total_amount
        FROM Transactions t
        JOIN Account a ON a.account_id = t.account_id
        WHERE date(t.ts) >= date('now', '-14 days')
        GROUP BY a.branch_id, date(t.ts)
    )
    SELECT branch_id, day, txn_count, total_amount
    FROM recent
    ORDER BY day ASC, branch_id ASC
    LIMIT 200;
    """,

    "Q11_outstanding_loans_by_primary_branch": """
    SELECT a.branch_id,
           COUNT(DISTINCT l.loan_id) AS num_loans,
           ROUND(SUM(l.principal), 2) AS total_principal
    FROM Loan l
    JOIN Customer c ON c.customer_id = l.customer_id
    JOIN AccountCustomer ac ON ac.customer_id = c.customer_id
    JOIN Account a ON a.account_id = ac.account_id
    WHERE l.status = 'active'
    GROUP BY a.branch_id
    ORDER BY total_principal DESC
    LIMIT 10;
    """,

    "Q15_avg_txn_amount_by_category_30d": """
    SELECT t.category,
           COUNT(*) AS txn_count,
           ROUND(AVG(ABS(t.amount)), 2) AS avg_amount
    FROM Transactions t
    WHERE date(t.ts) >= date('now', '-30 days')
    GROUP BY t.category
    ORDER BY txn_count DESC;
    """,

    "Q16_top_merchants_by_gross_volume_30d": """
    SELECT t.merchant,
           ROUND(SUM(ABS(t.amount)), 2) AS gross_volume,
           COUNT(*) AS txn_count
    FROM Transactions t
    WHERE date(t.ts) >= date('now', '-30 days')
    GROUP BY t.merchant
    ORDER BY gross_volume DESC
    LIMIT 10;
    """,

    "Q20_loan_payment_day_distribution_active": """
    SELECT payment_day,
           COUNT(*) AS num_loans
    FROM Loan
    WHERE status = 'active'
    GROUP BY payment_day
    ORDER BY payment_day;
    """,
}


def print_rows_to_console(name, cols, rows, max_width=28):
    print("=" * 80)
    print(f"{name}")
    print("-" * 80)
    header = " | ".join(cols)
    print(header)
    print("-" * len(header))
    for r in rows:
        out = []
        for v in r:
            s = "" if v is None else str(v)
            s = shorten(s, width=max_width, placeholder="…")
            out.append(s)
        print(" | ".join(out))
    print()


def write_rows_to_text(f, name, cols, rows):
    f.write("=" * 80 + "\n")
    f.write(f"{name}\n")
    f.write("-" * 80 + "\n")
    header = " | ".join(cols)
    f.write(header + "\n")
    f.write("-" * len(header) + "\n")
    for r in rows:
        line = " | ".join("" if v is None else str(v) for v in r)
        f.write(line + "\n")
    f.write("\n")


def write_rows_to_csv(path: Path, cols, rows):
    with path.open("w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow(cols)
        for r in rows:
            writer.writerow([("" if v is None else v) for v in r])


def infer_scale_suffix(outdir: Path) -> str:
    """
    Try to grab '1x', '3x', '5x', '8x', '10x' from the output dir name.
    If not found, fall back to empty string.
    """
    m = re.search(r"(\d+x)$", outdir.name)
    if m:
        return m.group(1)
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="SQLite DB path to read from")
    ap.add_argument("--outdir", required=True, help="Output directory, e.g. results/1x")
    args = ap.parse_args()

    db_path = Path(args.db)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    scale_suffix = infer_scale_suffix(outdir) 
    if scale_suffix:
        out_txt = outdir / f"print_set_results_{scale_suffix}.txt"
    else:
        out_txt = outdir / "print_set_results.txt"

    csv_dir = outdir / "printed_queries_csv"
    csv_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    with out_txt.open("w", encoding="utf-8") as tf:
        tf.write(f"Print set export generated at {datetime.datetime.now().isoformat()}\n")
        tf.write(f"Source DB: {db_path}\n\n")

        for name, sql in PRINT_QUERIES.items():
            try:
                cur.execute(sql)
                rows = cur.fetchall()
                if rows:
                    cols = rows[0].keys()
                else:
                    cols = [d[0] for d in cur.description] if cur.description else []

                # console
                print_rows_to_console(name, cols, rows)

                # text
                write_rows_to_text(tf, name, cols, rows)

                # csv per query
                safe_name = name.replace(" ", "_")
                csv_path = csv_dir / f"{safe_name}.csv"
                write_rows_to_csv(csv_path, cols, rows)

            except Exception as e:
                print("=" * 80)
                print(f"{name} -- ERROR: {e}")
                print("=" * 80)

                tf.write("=" * 80 + "\n")
                tf.write(f"{name} -- ERROR: {e}\n")
                tf.write("=" * 80 + "\n\n")

    conn.close()
    print(f"\nSaved combined text to   : {out_txt}")
    print(f"Saved per-query CSVs to  : {csv_dir}/")

if __name__ == "__main__":
    main()
