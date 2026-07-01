'''
Random Generating Fake Data
'''
import argparse, os, random, csv
from datetime import datetime, timedelta, date
import math

random.seed(42) #this can be changed

"""
Fake input data that would be randomized in this code.
    1. First Name (11)
    2. Last Name (11)
    3. Cities (5) 
    4. Merchants (10)
    5. Categories (8)
    6. Bank Types (2)
    7. Loan Types (4)

# More can be added to these list below
"""
FIRST = ["Alex","Jordan","Taylor","Casey","Riley","Avery","Quinn","Kai","Hayden","Emerson","Parker"]
LAST  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez","Hernandez"]
CITIES = [("Los Angeles","CA"),("San Diego","CA"),("Phoenix","AZ"),("Seattle","WA"),("Portland","OR")]
MERCHANTS = ["Safeway","Target","Costco","Shell","Amazon","Uber","Lyft","In-N-Out","Starbucks","Southwest"]
CATEGORIES = ["groceries","gas","retail","travel","dining","ride-share","online","bills"]
BANKS_TYPES = ["bank", "credit_union"]
LOAN_TYPES = ["student", "auto", "mortgage", "personal"]

def rid(prefix, n=10):
    import random, string
    return prefix + "_" + "".join(random.choices(string.ascii_uppercase + string.digits, k=n))

def daterange(start: date, days: int):
    for i in range(days):
        yield start + timedelta(days=i)

def generate(customers=1000, days=30, txns=60000, start_date=None, seed=42):
    import random
    from datetime import datetime, timedelta

    random.seed(seed)

    # Branches
    branches = []
    branch_len = len(CITIES)
    for i in range(branch_len):
        city, state = CITIES[i % len(CITIES)]
        bank_type = random.choices(BANKS_TYPES, weights=[0.7, 0.3], k=1)[0]
        branches.append((f"B{i+1:03}", f"{city} Branch", city, state, bank_type))

    # Customers
    customers_rows = []
    for i in range(customers):
        fn = random.choice(FIRST); ln = random.choice(LAST)
        name  = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{i}@FAKEemail.com"
        phone = f"050-055-01{i%1000:03}"
        city, state = random.choice(CITIES)
        cust_id = rid("UA")
        customers_rows.append((
            cust_id, name, email, phone, f"{i+10} Easy St", city, state,
            f"{90000+i%1000}", datetime.utcnow().isoformat(timespec='seconds')
        ))

    # Accounts, Cards, Loans
    accounts, cards, loans = [], [], []
    for cust_id, *_ in customers_rows:
        branch_id, _, city, state, bank_type = random.choice(branches)
        n_accts = 1 + int(random.random() < 0.6) + int(random.random() < 0.2)  # 1–3
        acct_types = ["checking", "savings", "loan"]
        for k in range(n_accts):
            acct_id = rid("A")
            atype = acct_types[k]
            opened_at = datetime.utcnow().isoformat(timespec='seconds')
            opening_balance = round(random.uniform(200, 3000), 2) if atype=="checking" else round(random.uniform(100, 8000), 2)
            accounts.append((acct_id, cust_id, branch_id, atype, "open", opened_at, opening_balance))

            if atype=="checking" and random.random() < 0.7:
                last4 = f"{random.randint(0,9999):04}"
                brand = random.choice(["Visa","Mastercard","Amex","Discover"])
                cards.append((rid("CARD"), acct_id, last4, brand, "active", opened_at))

        if random.random() < 0.1:
            ltype = random.choices(LOAN_TYPES, weights=[0.25,0.30,0.15,0.30], k=1)[0]
            if ltype == "student":
                principal = round(random.uniform(5000, 50000), 2); rate = round(random.uniform(3.0, 7.0), 2); term = random.choice([60,84,120,180])
            elif ltype == "auto":
                principal = round(random.uniform(8000, 60000), 2); rate = round(random.uniform(3.0, 9.0), 2); term = random.choice([36,48,60,72])
            elif ltype == "mortgage":
                principal = round(random.uniform(150000, 800000), 2); rate = round(random.uniform(2.5, 6.5), 2); term = random.choice([180,240,300,360])
            else:
                principal = round(random.uniform(1000, 30000), 2); rate = round(random.uniform(6.0, 20.0), 2); term = random.choice([12,24,36,48,60])

            start = datetime.utcnow().date().isoformat()
            payment_day = random.randint(4, 24)
            loans.append((rid("L"), cust_id, principal, rate, term, start, "active", payment_day, ltype))

    # Transactions
    tx_rows = []
    n_txns = int(txns)
    per_day = max(1, n_txns // max(1, days))

    if start_date:
        start_d = datetime.fromisoformat(start_date).date()
    else:
        start_d = datetime.utcnow().date() - timedelta(days=days-1)

    accounts_only = [a[0] for a in accounts]

    for day_idx in range(days):
        day = start_d + timedelta(days=day_idx)

        for _ in range(per_day):
            acct = random.choice(accounts_only)
            if random.random() < 0.8:
                amt = -round(random.uniform(3.0, 120.0), 2)
                merch = random.choice(MERCHANTS); cat = random.choice(CATEGORIES)
                cp = None; desc = f"POS {merch}"
            else:
                amt = round(random.uniform(50.0, 3000.0), 2)
                merch = "ACH"; cat = "income"; cp = None; desc = "ACH deposit"
            ts = datetime.combine(day, datetime.min.time()) + timedelta(seconds=random.randint(9*3600, 21*3600))
            tx_rows.append((rid("T"), acct, ts.isoformat(sep=' '), amt, merch, cat, cp, desc))

        # transfer between accounts
        if random.random() < 0.2 and len(accounts_only) > 1:
            src, dst = random.sample(accounts_only, 2)
            amt = round(random.uniform(20, 400), 2)
            ts = datetime.combine(day, datetime.min.time()) + timedelta(seconds=random.randint(10*3600, 18*3600))
            tx_rows.append((rid("T"), src, ts.isoformat(sep=' '), -amt, "Transfer", "transfer", dst, "Transfer out"))
            tx_rows.append((rid("T"), dst, ts.isoformat(sep=' '), +amt, "Transfer", "transfer", src, "Transfer in"))


    return {
        "branches": branches,
        "customers": customers_rows,
        "accounts":  accounts,
        "cards":     cards,
        "loans":     loans,
        "txns":      tx_rows,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--customers", type=int, default=1000)
    ap.add_argument("--days", type=int, default=30, help="number of sequential days of activity")
    ap.add_argument("--txns", type=int, default=60000, help="approx number of transactions to emit")
    ap.add_argument("--start_date", type=str, default=None, help="YYYY-MM-DD (defaults to today-days+1)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    os.makedirs("data", exist_ok=True)

    data = generate(
        customers=args.customers,
        days=args.days,
        txns=args.txns,
        start_date=args.start_date,
        seed=args.seed
    )

    def write_csv(path, header, rows):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(header); w.writerows(rows)

    write_csv("data/branches.csv",     ["branch_id","name","city","state","institution_type"],          data["branches"])
    write_csv("data/customers.csv",    ["customer_id","full_name","email","phone","address","city","state","zip","created_at"], data["customers"])
    write_csv("data/accounts.csv",     ["account_id","customer_id","branch_id","account_type","status","opened_at","opening_balance"], data["accounts"])
    write_csv("data/cards.csv",        ["card_id","account_id","last4","brand","status","activated_at"], data["cards"])
    write_csv("data/loans.csv",        ["loan_id","customer_id","principal","rate_apr","term_months","start_date","status","payment_day","loan_type"], data["loans"])
    write_csv("data/transactions.csv", ["txn_id","account_id","ts","amount","merchant","category","counterparty_account_id","description"], data["txns"])

    print(f"Generated: {len(data['customers'])} customers, {len(data['accounts'])} accounts, {len(data['txns'])} transactions.")

if __name__ == "__main__":
    main()
