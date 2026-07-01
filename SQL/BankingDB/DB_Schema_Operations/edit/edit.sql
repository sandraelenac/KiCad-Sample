PRAGMA foreign_keys = ON;

------------------------------------------------------------------------------
-- EDIT LOANS
------------------------------------------------------------------------------
UPDATE Loan
SET loan_type = (
  SELECT sl.loan_type
  FROM StgLoan sl
  WHERE sl.loan_id = Loan.loan_id
)
WHERE (loan_type IS NULL OR TRIM(loan_type) = '')
  AND EXISTS (SELECT 1 FROM StgLoan sl WHERE sl.loan_id = Loan.loan_id);

CREATE INDEX IF NOT EXISTS idx_loan_loan_type ON Loan(loan_type);

INSERT OR IGNORE INTO Loan(
  loan_id, customer_id, principal, rate_apr, term_months,
  start_date, status, payment_day, loan_type
)
SELECT l.loan_id, l.customer_id, l.principal, l.rate_apr, l.term_months,
       l.start_date, l.status, l.payment_day, l.loan_type
FROM StgLoan l
WHERE COALESCE(l.loan_id,'') <> ''
  AND EXISTS (SELECT 1 FROM Customer c WHERE c.customer_id = l.customer_id);

------------------------------------------------------------------------------
-- EDIT BRANCH
------------------------------------------------------------------------------
UPDATE Branch
SET routing_number = CASE branch_code
  WHEN 'B001' THEN 'UA1000001'
  WHEN 'B002' THEN 'UA1000002'
  WHEN 'B003' THEN 'UA1000003'
  WHEN 'B004' THEN 'UA1000004'
  WHEN 'B005' THEN 'UA1000005'
  ELSE routing_number
END
WHERE routing_number IS NULL OR TRIM(routing_number) = '';

------------------------------------------------------------------------------
-- EDIT ACCOUNTS
------------------------------------------------------------------------------


------------------------------------------------------------------------------
-- EDIT TRANSACTIONS
------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_txn_account ON Transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_txn_ts      ON Transactions(ts);

------------------------------------------------------------------------------
-- REMOVE STG TABLES (DATA GENERATED)
------------------------------------------------------------------------------
PRAGMA foreign_keys = OFF;   
BEGIN;
DROP TABLE IF EXISTS StgCustomer;
DROP TABLE IF EXISTS StgAccount;
DROP TABLE IF EXISTS StgBranch;
DROP TABLE IF EXISTS StgCard;
DROP TABLE IF EXISTS StgLoan;
DROP TABLE IF EXISTS StgTxn;
DROP TABLE IF EXISTS sqlite_stat1;

COMMIT;
PRAGMA foreign_keys = ON;