"""
BENCHMARK.PY
"""
import argparse
import csv
import sqlite3
import time
from pathlib import Path
from statistics import mean

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True, help="Path to SQLite database")
    p.add_argument("--sql", required=True, help="Path to workload SQL (semicolon-separated or -- name: lines)")
    p.add_argument("--runs", type=int, default=5, help="Number of timed runs (per query)")
    p.add_argument("--warmup", type=int, default=1, help="Number of warm-up executions (per query, not timed)")
    p.add_argument("--mode", choices=["baseline", "optimized"], default="baseline")
    p.add_argument("--outdir", default="results", help="Directory to write results")
    return p.parse_args()

def load_queries(sql_path: Path):
    """
    Supports two formats:

    1) Plain semicolon-separated SQL:
       SELECT ...; SELECT ...;

    2) Named blocks with lines starting with -- name: Q1_title
       -- name: Q1_customer_lookup_by_name_prefix
       SELECT ...
       ;
       -- name: Q2_...

    Returns list of (qid, qname, sql).
    """
    text = sql_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    queries = []
    cur_name = None
    buf = []

    def flush():
        nonlocal cur_name, buf
        sql = "\n".join(buf).strip().rstrip(";")
        if sql:
            qid = f"Q{len(queries)+1}"
            qname = cur_name or qid
            queries.append((qid, qname, sql))
        buf = []
        cur_name = None
    # Detect named style
    named_present = any(l.strip().lower().startswith("-- name:") for l in lines)

    if named_present:
        for l in lines:
            ls = l.strip()
            if ls.lower().startswith("-- name:"):
                # start of a new named query
                if buf:
                    flush()
                cur_name = ls.split(":", 1)[1].strip()
                continue
            buf.append(l)
            if ls.endswith(";"):
                flush()
        if buf:
            flush()
    else:
        # split by semicolon
        acc = []
        for l in lines:
            acc.append(l)
            if l.strip().endswith(";"):
                buf = acc
                flush()
                acc = []
        if acc:
            buf = acc
            flush()

    # Normalize IDs
    norm = []
    for i, (_, qname, sql) in enumerate(queries, start=1):
        norm.append((f"Q{i}", qname, sql))
    return norm

def run_query(cx: sqlite3.Connection, sql: str):
    cur = cx.execute(sql)
    rows = cur.fetchall()
    return len(rows)

def ensure_outdir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def main():
    args = parse_args()
    db_path = Path(args.db).resolve()
    sql_path = Path(args.sql).resolve()
    outdir = Path(args.outdir) / (f"x1" if "base" in db_path.name else Path(f"x{_infer_scale(db_path.name)}"))
    if _infer_scale(db_path.name) is None:
        outdir = Path(args.outdir)
    ensure_outdir(outdir)
    queries = load_queries(sql_path)

    # Output file
    mode_dir = outdir / args.mode
    ensure_outdir(mode_dir)
    out_csv = mode_dir / "results.csv"

    # SQLite connection
    cx = sqlite3.connect(str(db_path))
    cx.execute("PRAGMA foreign_keys = ON")

    results = []  # rows for CSV
    for qid, qname, qsql in queries:
        # Warm-ups (not timed)
        for _ in range(max(0, args.warmup)):
            try:
                run_query(cx, qsql)
            except Exception:
                raise

        # Timed runs
        times = []
        rows_seen = None
        for _ in range(max(1, args.runs)):
            t0 = time.perf_counter()
            cnt = run_query(cx, qsql)
            t1 = time.perf_counter()
            times.append(t1 - t0)
            rows_seen = cnt

        avg_s = mean(times)
        min_s = min(times)
        max_s = max(times)

        # Print avg, min, & max times
        print(f"{qname:<36} avg={avg_s:.6f}s  min={min_s:.6f}s  max={max_s:.6f}s  rows={rows_seen}")

        results.append({
            "query_id": qid,
            "query_name": qname,
            "rows": rows_seen,
            "avg_s": f"{avg_s:.6f}",
            "min_s": f"{min_s:.6f}",
            "max_s": f"{max_s:.6f}",
            "mode": args.mode,
            "runs": args.runs,
            "warmup": args.warmup,
        })

    # Write CSV
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "query_id", "query_name", "rows",
            "avg_s", "min_s", "max_s",
            "mode", "runs", "warmup"
        ])
        w.writeheader()
        w.writerows(results)

    print(f"\nWrote {out_csv}")

def _infer_scale(db_name: str):
    name = db_name.lower()
    if "base" in name or name.endswith(".sqlite") and "x" not in name:
        return 1
    # find pattern _xN
    import re
    m = re.search(r"_x(\d+)\.sqlite", name)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None

if __name__ == "__main__":
    main()
