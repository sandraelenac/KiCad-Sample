#
# EXECUTE ALL
#       Basline & Optimization (1x), & Upscaling (3, 5, 8, 10)

import subprocess
from pathlib import Path

# --- Paths ---
base = Path(__file__).resolve().parent
rawdb_dir = base / "DB_Schema_Operations" / "rawDB"
ddl_path = base / "DB_Schema_Operations" / "ddl" / "create_tables.sql"
edit_sql = base / "DB_Schema_Operations" / "edit" / "edit.sql"
#final_sql = base / "DB_Schema_Operations" / "edit" / "finalDB.sql"
benchmark_sql = base / "queries" / "queries_workload.sql"
print_set_py = base / "queries" / "print_queries.py" 

# Scaling factors 
scales = [1, 3, 5, 8, 10]
# Ensure rawDB exists
rawdb_dir.mkdir(parents=True, exist_ok=True) 

for scale in scales:
    db_name = f"bank_x{scale}.sqlite" if scale > 1 else "bank_base.sqlite"
    db_path = rawdb_dir / db_name

    print(f"\n{'='*80}")
    label = "BASELINE (1×)" if scale == 1 else f"SCALE {scale}×"
    print(f"[RUNNING {label}] → {db_path.name}")
    print(f"{'='*80}\n")

    if db_path.exists():
        print(f"[CLEAN] Removing existing database: {db_path}")
        db_path.unlink() # delete existing DB file

    # ----------------------------------------
    # STEP 1: Generate and Load Data
    # ----------------------------------------
    subprocess.run([
        "python", str(base / "DB_Schema_Operations" / "etl" / "load_sqlite.py"),
        "--db", str(db_path),
        "--ddl", str(ddl_path),
        "--from-synth",
        "--customers", str(1000 * scale),
        "--days", "30",
        "--txns", str(100000 * scale),
        "--seed", "42"
    ], check=True)

    # ----------------------------------------
    # STEP 2: Apply edit.sql to DB
    # ----------------------------------------
    print(f"\n[STEP 2] Applying edit.sql to {db_name}")
    edit_p  = edit_sql.as_posix()
    #final_p = final_sql.as_posix()
    sqlite_input = f'.read "{edit_p}"'# \n.read "{final_p}"\n'
    subprocess.run(["sqlite3", str(db_path)], input=sqlite_input.encode("utf-8"))

    # ----------------------------------------
    # STEP 3: Creating Final DB
    # ----------------------------------------
    final_db = base / (f"FinalBankDB_x{scale}.sqlite" if scale > 1 else "FinalBankDB.sqlite")
    print(f"\n[STEP 3] Copying {db_name} → {final_db.name}...")
    final_db.write_bytes(db_path.read_bytes())

    # per-scale results folder: results/1x, results/3x, ...
    outdir = base / "results" / f"x{scale}"

    # ------------------------------------------------------------------
    # STEP 4: baseline
    # ------------------------------------------------------------------
    print(f"\n[STEP 4] Executing baseline for {label}...")
    subprocess.run([
        "python", str(base / "queries" / "benchmark.py"),
        "--db", str(final_db),
        "--sql", str(benchmark_sql),
        "--runs", "5",
        "--warmup", "1",
        "--mode", "baseline",
        "--outdir", str(outdir)
    ], check=True)

    # ------------------------------------------------------------------
    # STEP 5: optimized
    # ------------------------------------------------------------------
    print(f"\n[STEP 5] Executing optimized for {label}...")
    subprocess.run([
        "python", str(base / "queries" / "benchmark.py"),
        "--db", str(final_db),
        "--sql", str(benchmark_sql),
        "--runs", "5",
        "--warmup", "1",
        "--mode", "optimized",
        "--outdir", str(outdir)
    ], check=True)

    # ------------------------------------------------------------------
    # STEP 6: print Queries
    # ------------------------------------------------------------------
    print(f"\n[STEP 6] Exporting print-set results for {label} to {outdir} ...")
    subprocess.run([
        "python", str(print_set_py),
        "--db", str(final_db),
        "--outdir", str(outdir)
    ], check=True)

    print(f"\n✅ Completed STEPS 1 through 5 for {label}!\n")

print("\n🎯 All runs (1×, 3×, 5×, 8×, 10×) completed successfully!")
