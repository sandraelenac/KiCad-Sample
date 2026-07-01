"""
Data Loader
1. CLI prints in command termina
2. STAGING

"""
import csv
import argparse
import sqlite3
from pathlib import Path
import sys

# ----------------------------------------
# Command Line Interface (CLI) prints in command terminal
# ----------------------------------------
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--db",       type=str, default="bank.sqlite", help="SQLite DB path")
    p.add_argument("--ddl",      type=str, default="ddl/create_tables.sql", help="Schema SQL path")
    p.add_argument("--data_dir", type=str, default="data", help="Directory containing CSVs")

    # In-memory option (no CSV files)
    p.add_argument("--from-synth", action="store_true",
                   help="Generate and load data directly from synth_data (no CSV files).")
    p.add_argument("--customers", type=int, default=1000)
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--txns", type=int, default=60000)
    p.add_argument("--start_date", type=str, default=None)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()

def insert_many(conn, table, cols, rows):
    if not rows:
        return 0
    q = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})"
    conn.executemany(q, rows)
    return len(rows)

# ----------------------------------------
# STAGING. This is the data generated
# ----------------------------------------
STAGING_SCHEMAS = {
    "StgCustomer": """
        DROP TABLE IF EXISTS StgCustomer;
        CREATE TABLE StgCustomer(
          customer_id_ext TEXT, name TEXT, phone TEXT, id_number TEXT,
          line1 TEXT, line2 TEXT, city TEXT, state TEXT, postal_code TEXT, country TEXT,
          email TEXT, created_at TEXT
        );
    """,
    "StgBranch": """
        DROP TABLE IF EXISTS StgBranch;
        CREATE TABLE StgBranch(
          branch_code TEXT, routing_number TEXT, contact_info TEXT,
          line1 TEXT, line2 TEXT, city TEXT, state TEXT, postal_code TEXT, country TEXT
        );
    """,
    "StgAccount": """
        DROP TABLE IF EXISTS StgAccount;
        CREATE TABLE StgAccount(
          account_number TEXT, balance REAL, is_active INTEGER,
          branch_code TEXT, account_type_name TEXT,
          primary_customer_id_ext TEXT, joint_owner_ids TEXT,
          line1 TEXT, line2 TEXT, city TEXT, state TEXT, postal_code TEXT, country TEXT
        );
    """,
    "StgCard": """
      DROP TABLE IF EXISTS StgCard;
      CREATE TABLE StgCard(
        card_id TEXT, account_id TEXT, last4 TEXT, brand TEXT, status TEXT, activated_at TEXT
      );
    """,
    "StgTxn": """
      DROP TABLE IF EXISTS StgTxn;
      CREATE TABLE StgTxn(
        txn_id TEXT, account_id TEXT, ts TEXT, amount REAL,
        merchant TEXT, category TEXT, counterparty_account_id TEXT, description TEXT
      );
    """,
    "StgLoan": """
      DROP TABLE IF EXISTS StgLoan;
      CREATE TABLE StgLoan(
        loan_id TEXT,
        customer_id TEXT,
        principal REAL,
        rate_apr REAL,
        term_months INTEGER,
        start_date TEXT,
        status TEXT,
        payment_day INTEGER,
        loan_type TEXT
      );
    """,
}

def apply_schema(conn: sqlite3.Connection, ddl_path: Path):
    if not ddl_path.exists():
        raise FileNotFoundError(f"Schema file not found: {ddl_path}")
    with open(ddl_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

def create_staging(conn: sqlite3.Connection):
    cur = conn.cursor()
    for ddl in STAGING_SCHEMAS.values():
        cur.executescript(ddl)
    conn.commit()

def _get(rec, *keys, default=None):
    for k in keys:
        if k and k in rec and rec[k] not in (None, ""):
            return rec[k]
    return default

# ----------------------------------------
# Process the outputs of data generator
# -----------------------------------------
def load_customers_flexible(conn: sqlite3.Connection, csv_path: Path) -> int:
    if not csv_path.exists(): return 0
    rows = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cur = conn.cursor()
        sql = """
          INSERT INTO StgCustomer
          (customer_id_ext,name,phone,id_number,line1,line2,city,state,postal_code,country,email,created_at)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """
        for rec in reader:
            customer_id_ext = _get(rec, "customer_id_ext", "customer_id")
            name            = _get(rec, "name", "full_name")
            phone           = _get(rec, "phone")
            id_number       = _get(rec, "id_number")
            line1           = _get(rec, "line1", "address")
            line2           = _get(rec, "line2", default="")
            city            = _get(rec, "city")
            state           = _get(rec, "state")
            postal_code     = _get(rec, "postal_code", "zip")
            country         = _get(rec, "country", default="USA")
            email           = _get(rec, "email")
            created_at      = _get(rec, "created_at")
            if not (customer_id_ext or name or phone):  # skip empty
                continue
            cur.execute(sql, [customer_id_ext, name, phone, id_number, line1, line2,
                              city, state, postal_code, country, email, created_at])
            rows += 1
        conn.commit()
    return rows

def load_branches_flexible(conn: sqlite3.Connection, csv_path: Path) -> int:
    """
    Your headers: branch_id, name, city, state, institution_type
    Map to StgBranch canonical columns.
    """
    if not csv_path.exists(): return 0
    rows = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cur = conn.cursor()
        sql = """
          INSERT INTO StgBranch
            (branch_code, routing_number, contact_info, line1, line2, city, state, postal_code, country)
          VALUES (?,?,?,?,?,?,?,?,?)
        """
        for rec in reader:
            branch_code   = str(_get(rec, "branch_id"))
            contact_info  = _get(rec, "institution_type")
            routing_num   = None
            line1         = _get(rec, "line1", "name") or "Unknown Branch"
            line2         = ""
            city          = _get(rec, "city")
            state         = _get(rec, "state")
            postal_code   = "00000"
            country       = "USA"
            if not branch_code:
                continue
            cur.execute(sql, [branch_code, routing_num, contact_info, line1, line2,
                              city, state, postal_code, country])
            rows += 1
        conn.commit()
    return rows

def load_accounts_flexible(conn: sqlite3.Connection, csv_path: Path) -> int:
    """
    Your headers: account_id, customer_id, branch_id, account_type, status, opened_at, opening_balance
    Map to StgAccount canonical columns.
    """
    if not csv_path.exists(): return 0
    rows = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cur = conn.cursor()
        sql = """
          INSERT INTO StgAccount
          (account_number,balance,is_active,branch_code,account_type_name,
           primary_customer_id_ext,joint_owner_ids,line1,line2,city,state,postal_code,country)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        for rec in reader:
            account_number  = str(_get(rec, "account_number", "account_id"))
            balance         = _get(rec, "balance", "opening_balance", default=0.0)
            status          = (_get(rec, "is_active", "status", default="active") or "").lower()
            is_active       = 1 if status in ("active", "open", "opened") else 0
            branch_code     = str(_get(rec, "branch_code", "branch_id"))
            account_type    = _get(rec, "account_type_name", "account_type")
            primary_ext     = _get(rec, "primary_customer_id_ext", "customer_id")
            joint_ids       = _get(rec, "joint_owner_ids", default="")  # none in your file
            # address fields unused for accounts
            line1 = line2 = city = state = postal = country = ""
            if not account_number:
                continue
            cur.execute(sql, [account_number, balance, is_active, branch_code, account_type,
                              primary_ext, joint_ids, line1, line2, city, state, postal, country])
            rows += 1
        conn.commit()
    return rows

def load_generic_csv(conn: sqlite3.Connection, csv_path: Path, table: str, headers: list[str]) -> int:
    """Strict CSV loader: writes rows into a staging table with given columns."""
    if not csv_path.exists():
        return 0
    rows = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_headers = [h.strip() for h in (reader.fieldnames or [])]
        missing = [h for h in headers if h not in csv_headers]
        if missing:
            raise ValueError(f"{csv_path.name} missing columns: {missing}\nFound: {csv_headers}")
        placeholders = ",".join(["?"]*len(headers))
        sql = f"INSERT INTO {table} ({','.join(headers)}) VALUES ({placeholders})"
        cur = conn.cursor()
        for rec in reader:
            cur.execute(sql, [rec.get(h) for h in headers])
            rows += 1
        conn.commit()
    return rows

# ----------------------------------------
# Normalize
# ----------------------------------------
def populate(conn):
    cur = conn.cursor()

    # Useful uniques 
    cur.executescript("""
      CREATE UNIQUE INDEX IF NOT EXISTS uq_account_number    ON Account(account_number);
      CREATE UNIQUE INDEX IF NOT EXISTS uq_branch_code       ON Branch(branch_code);
      CREATE UNIQUE INDEX IF NOT EXISTS uq_account_type_name ON AccountType(name);
      CREATE UNIQUE INDEX IF NOT EXISTS uq_address_nk
        ON Address(line1, COALESCE(line2,''), city, state, postal_code, country);
    """)

    # 1) Addresses from customers + branches
    cur.executescript("""
      INSERT OR IGNORE INTO Address(line1,line2,city,state,postal_code,country)
      SELECT DISTINCT line1, COALESCE(line2,''), city, state, postal_code, COALESCE(country,'USA')
      FROM StgCustomer
      WHERE COALESCE(line1,'')<>'' AND COALESCE(city,'')<>'' AND COALESCE(state,'')<>'' AND COALESCE(postal_code,'')<>'';

      INSERT OR IGNORE INTO Address(line1,line2,city,state,postal_code,country)
      SELECT DISTINCT line1, COALESCE(line2,''), city, state, postal_code, COALESCE(country,'USA')
      FROM StgBranch
      WHERE COALESCE(line1,'')<>'' AND COALESCE(city,'')<>'' AND COALESCE(state,'')<>'' AND COALESCE(postal_code,'')<>'';
    """)

    # 2) Branch ( CSV branch_id as PK; set branch_code = branch_id)
    cur.executescript("""
      INSERT OR IGNORE INTO Branch(branch_id, address_id, branch_code, contact_info, routing_number)
      SELECT s.branch_code, a.address_id, s.branch_code, s.contact_info, NULLIF(s.routing_number,'')
      FROM StgBranch s
      LEFT JOIN Address a
        ON a.line1=s.line1 AND COALESCE(a.line2,'')=COALESCE(s.line2,'')
       AND a.city=s.city AND a.state=s.state
       AND a.postal_code=s.postal_code AND a.country=COALESCE(s.country,'USA');
    """)

    # 3) AccountType (map names to IDs)
    cur.executescript("""
      INSERT OR IGNORE INTO AccountType(name, description, interest_rate)
      SELECT DISTINCT account_type_name, NULL, 0.0
      FROM StgAccount
      WHERE COALESCE(account_type_name,'')<>'';
    """)

    # 4) Customer (use CSV customer_id as PK)
    cur.executescript("""
      INSERT OR IGNORE INTO Customer(customer_id, name, phone, id_number)
      SELECT DISTINCT customer_id_ext, name, phone, COALESCE(id_number, customer_id_ext)
      FROM StgCustomer
      WHERE COALESCE(customer_id_ext,'')<>'';
    """)

    # 5) CustomerAddress (primary home)
    cur.executescript("""
      INSERT OR IGNORE INTO CustomerAddress(customer_id, address_id, address_type, is_primary)
      SELECT s.customer_id_ext, a.address_id, 'home', 0
      FROM StgCustomer s
      JOIN Address a
        ON a.line1=s.line1 AND COALESCE(a.line2,'')=COALESCE(s.line2,'')
       AND a.city=s.city AND a.state=s.state
       AND a.postal_code=s.postal_code AND a.country=COALESCE(s.country,'USA');

      WITH first_home AS (
        SELECT customer_id, MIN(address_id) AS address_id
        FROM CustomerAddress
        WHERE address_type='home'
        GROUP BY customer_id
      )
      UPDATE CustomerAddress
         SET is_primary=1
       WHERE (customer_id, address_id, address_type) IN
             (SELECT customer_id, address_id, 'home' FROM first_home);
    """)

    # 6) Account (use CSV account_id as PK; branch_id is CSV branch_id; account_number = account_id)
    cur.executescript("""
      INSERT OR IGNORE INTO Account(account_id, branch_id, account_type_id, account_number, is_active, balance)
      SELECT
        s.account_number,                -- already mapped from CSV account_id
        s.branch_code,                   -- mapped from CSV branch_id
        t.account_type_id,               -- lookup by name
        s.account_number,                -- keep account_number = account_id
        COALESCE(s.is_active,1),
        COALESCE(s.balance,0.0)
      FROM StgAccount s
      LEFT JOIN AccountType t ON t.name = s.account_type_name
      WHERE COALESCE(s.account_number,'')<>'';
    """)

    # 7) AccountCustomer (owners; primary only—add joint parsing if you later include it)
    cur.executescript("""
      INSERT OR IGNORE INTO AccountCustomer(account_id, customer_id, is_primary)
      SELECT s.account_number, s.primary_customer_id_ext, 1
      FROM StgAccount s
      WHERE COALESCE(s.account_number,'')<>'' AND COALESCE(s.primary_customer_id_ext,'')<>'';
    """)

    # Cards (only where the account exists)
    cur.executescript("""
    INSERT OR IGNORE INTO Card(card_id, account_id, last4, brand, status, activated_at)
    SELECT c.card_id, c.account_id, c.last4, c.brand, c.status, c.activated_at
    FROM StgCard c
    WHERE COALESCE(c.card_id,'') <> ''
        AND EXISTS (SELECT 1 FROM Account a WHERE a.account_id = c.account_id);
    """)

    # Transactions 
    cur.executescript("""
    INSERT OR IGNORE INTO Transactions(
        txn_id, account_id, ts, amount, merchant, category, counterparty_account_id, description)
    SELECT
        t.txn_id,
        t.account_id,
        t.ts,
        t.amount,
        t.merchant,
        t.category,
        CASE
        WHEN t.counterparty_account_id IS NOT NULL
        AND t.counterparty_account_id <> ''
        AND EXISTS (SELECT 1 FROM Account a2 WHERE a2.account_id = t.counterparty_account_id)
        THEN t.counterparty_account_id
        ELSE NULL
        END,
        t.description
    FROM StgTxn t
    WHERE COALESCE(t.txn_id,'') <> ''
        AND EXISTS (SELECT 1 FROM Account a WHERE a.account_id = t.account_id);
    """)

    # ---------------------
    # Loans  (denormalized) version with text loan_type)
    # ---------------------
    # 1) Ensure staging has loan_type column
    cur.execute("PRAGMA table_info(StgLoan);")
    stg_cols = {r[1] for r in cur.fetchall()}
    if "loan_type" not in stg_cols:
        cur.execute("ALTER TABLE StgLoan ADD COLUMN loan_type TEXT")

    # 2) Fill missing loan_type values heuristically based on principal/term
    cur.executescript("""
        UPDATE StgLoan
        SET loan_type = CASE
            WHEN principal >= 150000 AND term_months >= 180 THEN 'mortgage'
            WHEN principal BETWEEN 8000 AND 60000 AND term_months BETWEEN 36 AND 72 THEN 'auto'
            WHEN principal BETWEEN 5000 AND 50000 AND term_months >= 60 THEN 'student'
            ELSE 'personal'
        END
        WHERE loan_type IS NULL OR TRIM(loan_type) = '';
    """)

    # 3) Ensure main Loan table has the text column
    cur.execute("PRAGMA table_info(Loan);")
    loan_cols = {r[1] for r in cur.fetchall()}
    if "loan_type" not in loan_cols:
        cur.execute("ALTER TABLE Loan ADD COLUMN loan_type TEXT")

    # 4) Backfill existing Loan rows that are missing text
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='LoanType'")
    if cur.fetchone():
        cur.executescript("""
            UPDATE Loan
            SET loan_type = (
                SELECT lt.name
                FROM LoanType lt
                WHERE lt.loan_type_id = Loan.loan_type_id
            )
            WHERE (loan_type IS NULL OR TRIM(loan_type) = '')
              AND loan_type_id IS NOT NULL;
        """)

    cur.executescript("""
        UPDATE Loan
        SET loan_type = (
            SELECT l.loan_type
            FROM StgLoan l
            WHERE l.loan_id = Loan.loan_id
        )
        WHERE (loan_type IS NULL OR TRIM(loan_type) = '')
          AND EXISTS (SELECT 1 FROM StgLoan l WHERE l.loan_id = Loan.loan_id);
    """)

    # 5) Insert new loans (ignore duplicates)
    cur.executescript("""
        INSERT OR IGNORE INTO Loan(
            loan_id, customer_id, principal, rate_apr, term_months,
            start_date, status, payment_day, loan_type
        )
        SELECT l.loan_id, l.customer_id, l.principal, l.rate_apr, l.term_months,
               l.start_date, l.status, l.payment_day, l.loan_type
        FROM StgLoan l
        WHERE COALESCE(l.loan_id,'') <> ''
          AND EXISTS (SELECT 1 FROM Customer c WHERE c.customer_id = l.customer_id);
    """)

    # 6) Create index for faster queries
    cur.execute("CREATE INDEX IF NOT EXISTS idx_loan_loan_type ON Loan(loan_type)")

    conn.commit()

def diagnose_orphans_prepopulate(conn: sqlite3.Connection):
    cur = conn.cursor()
    print("\nPopulate Schema. is there missing attributes missing from data_gen and schema?")

    # Cards --> Accounts
    bad_cards = cur.execute("""
        SELECT COUNT(*)
        FROM StgCard c
        LEFT JOIN StgAccount a ON a.account_number = c.account_id
        WHERE a.account_number IS NULL
    """).fetchone()[0]
    print(f"  StgCard.account_id missing in StgAccount: {bad_cards}")

    # Transactions -->  Accounts
    bad_txn_acct = cur.execute("""
        SELECT COUNT(*)
        FROM StgTxn t
        LEFT JOIN StgAccount a ON a.account_number = t.account_id
        WHERE a.account_number IS NULL
    """).fetchone()[0]
    print(f"  StgTxn.account_id missing in StgAccount: {bad_txn_acct}")

    # Transactions counterparty -->  Accounts
    bad_txn_cp = cur.execute("""
        SELECT COUNT(*)
        FROM StgTxn t
        LEFT JOIN StgAccount a ON a.account_number = t.counterparty_account_id
        WHERE COALESCE(t.counterparty_account_id,'') <> ''
          AND a.account_number IS NULL
    """).fetchone()[0]
    print(f"  StgTxn.counterparty_account_id missing in StgAccount: {bad_txn_cp}")

    # Loans -->  Customers
    bad_loans = cur.execute("""
        SELECT COUNT(*)
        FROM StgLoan l
        LEFT JOIN StgCustomer c ON c.customer_id_ext = l.customer_id
        WHERE c.customer_id_ext IS NULL
    """).fetchone()[0]
    print(f"  StgLoan.customer_id missing in StgCustomer: {bad_loans}")

    # Accounts -->  Branches
    bad_acct_branch = cur.execute("""
        SELECT COUNT(*)
        FROM StgAccount s
        LEFT JOIN StgBranch b ON b.branch_code = s.branch_code
        WHERE COALESCE(s.branch_code,'') <> '' AND b.branch_code IS NULL
    """).fetchone()[0]
    print(f"  StgAccount.branch_code missing in StgBranch: {bad_acct_branch}\n")

def integrity_checks(conn: sqlite3.Connection):
    cur = conn.cursor()
    print("Integrity checks:")
    for name, cnt in cur.execute("""
      SELECT 'acct_missing_branch', COUNT(*) FROM Account WHERE branch_id NOT IN (SELECT branch_id FROM Branch)
      UNION ALL
      SELECT 'acct_missing_type', COUNT(*) FROM Account WHERE account_type_id NOT IN (SELECT account_type_id FROM AccountType)
      UNION ALL
      SELECT 'ac_missing_customer', COUNT(*) FROM AccountCustomer WHERE customer_id NOT IN (SELECT customer_id FROM Customer)
      UNION ALL
      SELECT 'ac_missing_account', COUNT(*) FROM AccountCustomer WHERE account_id NOT IN (SELECT account_id FROM Account);
    """):
        print(f"  {name}: {cnt}")

    bad_primary = cur.execute("""
      SELECT COUNT(*) FROM (
        SELECT account_id, SUM(COALESCE(is_primary,0)) AS prim_count
        FROM AccountCustomer
        GROUP BY account_id
        HAVING prim_count <> 1
      );
    """).fetchone()[0]
    if bad_primary:
        print(f"  WARNING: {bad_primary} account(s) without exactly one primary owner")

# IF THERE ARE NO CSVs
def load_from_synth(conn: sqlite3.Connection, *, customers: int, days: int, txns: int, start_date: str|None, seed: int) -> dict:
    """
    Imports synth_data.generate(...) and loads its output directly into staging.
    Returns dict of row counts by staging table.
    """
    try:
        import synth_data as sd
    except ImportError as e:
        print("ERROR: Could not import synth_data. Make sure synth_data.py is on PYTHONPATH or in the same folder.", file=sys.stderr)
        raise

    if not hasattr(sd, "generate"):
        raise AttributeError("synth_data.py is missing generate(...). Add the function per patch instructions.")

    data = sd.generate(customers=customers, days=days, txns=txns, start_date=start_date, seed=seed)

    # Branches: (branch_id, name, city, state, institution_type) --> 
    # StgBranch(branch_code, routing_number, contact_info, line1, line2, city, state, postal_code, country)
    n_b = insert_many(conn, "StgBranch",
        ["branch_code", "routing_number", "contact_info", "line1", "line2", "city", "state", "postal_code", "country"],
        [(b_id, None, itype, name, "", city, state, "00000", "USA")
         for (b_id, name, city, state, itype) in data["branches"]])

    # Customers: (cust_id, name, email, phone, address, city, state, zip, created)
    n_c = insert_many(conn, "StgCustomer",
        ["customer_id_ext","name","phone","id_number","line1","line2","city","state","postal_code","country","email","created_at"],
        [(cid, name, phone, cid, addr, "", city, state, zipc, "USA", email, created)
         for (cid, name, email, phone, addr, city, state, zipc, created) in data["customers"]])

    # Accounts: (acct_id, cust_id, branch_id, atype, status, opened, opening_balance)
    n_a = insert_many(conn, "StgAccount",
        ["account_number","balance","is_active","branch_code","account_type_name","primary_customer_id_ext",
         "joint_owner_ids","line1","line2","city","state","postal_code","country"],
        [(aid,
          opening_balance,
          1 if (status or "").lower() in ("open", "active", "opened") else 0,
          bid,
          atype,
          cid,
          "",
          "", "", "", "", "", "")
         for (aid, cid, bid, atype, status, opened, opening_balance) in data["accounts"]])

    # Cards
    n_cards = insert_many(conn, "StgCard",
        ["card_id","account_id","last4","brand","status","activated_at"],
        data["cards"])

    # Loans
    n_loans = insert_many(conn, "StgLoan",
        ["loan_id","customer_id","principal","rate_apr","term_months","start_date","status","payment_day","loan_type"],
        data["loans"])

    # Transactions
    n_txn = insert_many(conn, "StgTxn",
        ["txn_id","account_id","ts","amount","merchant","category","counterparty_account_id","description"],
        data["txns"])

    conn.commit()
    return {"StgBranch": n_b, "StgCustomer": n_c, "StgAccount": n_a, "StgCard": n_cards, "StgLoan": n_loans, "StgTxn": n_txn}

def main():
    args = parse_args()
    db_path   = Path(args.db).expanduser().resolve()
    ddl_path  = Path(args.ddl).expanduser().resolve()
    data_dir  = Path(args.data_dir).expanduser().resolve()

    print("Resolved paths:")
    print(f"  DB       : {db_path}")
    print(f"  DDL      : {ddl_path}")
    print(f"  DATA_DIR : {data_dir}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    # 1) Apply schema + staging
    apply_schema(conn, ddl_path)
    create_staging(conn)

    if args.from_synth:
        print("\nLoading directly from synth_data.generate... (no CSV files were saved)")
        counts = load_from_synth(
            conn,
            customers=args.customers,
            days=args.days,
            txns=args.txns,
            start_date=args.start_date,
            seed=args.seed
        )
        for k, v in counts.items():
            print(f"{k:<12} : {v} rows")

        diagnose_orphans_prepopulate(conn)
        populate(conn)
        integrity_checks(conn)
        conn.close()
        print("Done.")
        return

    # CSV mode: require data_dir to exist
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    # 2) Load CSVs (flex)
    n_c = load_customers_flexible(conn, data_dir / "customers.csv")
    print(f"customers.csv  -->  StgCustomer : {n_c} rows")
    n_b = load_branches_flexible(conn, data_dir / "branches.csv")
    print(f"branches.csv   -->  StgBranch   : {n_b} rows")
    n_a = load_accounts_flexible(conn, data_dir / "accounts.csv")
    print(f"accounts.csv   -->  StgAccount  : {n_a} rows")

    n_cards = load_generic_csv(
        conn, data_dir / "cards.csv", "StgCard",
        ["card_id","account_id","last4","brand","status","activated_at"]
    )
    print(f"cards.csv       -->  StgCard    : {n_cards} rows")

    n_txn = load_generic_csv(
        conn, data_dir / "transactions.csv", "StgTxn",
        ["txn_id","account_id","ts","amount","merchant","category","counterparty_account_id","description"]
    )
    print(f"transactions.csv -->  StgTxn     : {n_txn} rows")

    n_loan = load_generic_csv(
        conn, data_dir / "loans.csv", "StgLoan",
        ["loan_id","customer_id","principal","rate_apr","term_months","start_date","status","payment_day","loan_type"]
    )
    print(f"loans.csv       -->  StgLoan    : {n_loan} rows")

    diagnose_orphans_prepopulate(conn)

    if (n_c + n_b + n_a + n_cards + n_txn + n_loan) == 0:
        print("No CSV rows loaded; check data directory and filenames.")
    else:
        populate(conn)
        integrity_checks(conn)

    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
