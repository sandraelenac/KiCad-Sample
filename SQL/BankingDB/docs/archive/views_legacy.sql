-- Current balance per account: opening_balance + sum(transactions.amount)
CREATE VIEW IF NOT EXISTS v_account_balance AS
SELECT
  a.account_id,
  a.customer_id,
  a.account_type,
  a.opened_at,
  a.opening_balance + COALESCE(SUM(t.amount), 0) AS current_balance
FROM accounts a
LEFT JOIN transactions t ON t.account_id = a.account_id
GROUP BY a.account_id;

-- Aggregate balances per customer
CREATE VIEW IF NOT EXISTS v_customer_balance AS
SELECT
  c.customer_id,
  c.full_name,
  COUNT(DISTINCT a.account_id) AS num_accounts,
  COALESCE(SUM(v.current_balance), 0) AS total_balance
FROM customers c
LEFT JOIN accounts a ON a.customer_id = c.customer_id
LEFT JOIN v_account_balance v ON v.account_id = a.account_id
GROUP BY c.customer_id;

-- Monthly statement helper (filters by year-month later)
CREATE VIEW IF NOT EXISTS v_monthly_statement AS
SELECT
  a.account_id,
  strftime('%Y-%m', t.ts) AS ym,
  COUNT(*) AS txn_count,
  ROUND(SUM(t.amount), 2) AS net_change
FROM accounts a
JOIN transactions t ON t.account_id = a.account_id
GROUP BY a.account_id, ym;
