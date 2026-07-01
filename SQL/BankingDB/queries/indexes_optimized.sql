
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
PRAGMA cache_size = -200000;     -- ~200 MB 
PRAGMA mmap_size  = 30000000000; -- ~30 GB

-- 1) Name search / lookups (Q1, Q2, Q3)
CREATE INDEX IF NOT EXISTS idx_customer_name
ON customer(name);

-- 2) Join helpers (Q1–Q3, Q7–Q11)
CREATE INDEX IF NOT EXISTS idx_acctcust_cust
ON AccountCustomer(customer_id);

CREATE INDEX IF NOT EXISTS idx_acctcust_acct
ON AccountCustomer(account_id);

-- Primary-account resolution (Q11)
CREATE INDEX IF NOT EXISTS idx_acctcust_primary
ON AccountCustomer(customer_id, is_primary);

-- Branch lookups (Q7–Q10)
CREATE INDEX IF NOT EXISTS idx_account_branch
ON Account(branch_id);

-- 3) Time-windowed transaction workloads (Q4–Q10)
-- index for account + time filters, ordering by transactions
CREATE INDEX IF NOT EXISTS idx_txn_acct_ts
ON Transactions(account_id, ts);
-- filter by time window without account prefilter:
CREATE INDEX IF NOT EXISTS idx_txn_ts
ON Transactions(ts);

-- 4) Loans (Q11) — fast status filter + join back to customer
CREATE INDEX IF NOT EXISTS idx_loan_customer_status
ON Loan(customer_id, status);

-- 5) Cards 
CREATE INDEX IF NOT EXISTS idx_card_account
ON Card(account_id);

-- 6) Refresh statistics
ANALYZE;
