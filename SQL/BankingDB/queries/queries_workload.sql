
-- name: Q1_customer_lookup_by_name_prefix
-- Find customers by name and count their accounts
WITH popular AS (
  SELECT substr(UPPER(TRIM(name)),1,1) AS pref
  FROM customer
  GROUP BY pref
  ORDER BY COUNT(*) DESC
  LIMIT 5
)
SELECT c.customer_id,
       c.name,
       COUNT(DISTINCT ac.account_id) AS num_accounts
FROM customer c
LEFT JOIN AccountCustomer ac ON ac.customer_id = c.customer_id
WHERE substr(UPPER(TRIM(c.name)),1,1) IN (SELECT pref FROM popular)
GROUP BY c.customer_id, c.name
ORDER BY c.name
LIMIT 10000;

-- name: Q2_customer_lookup_top5_initials
WITH popular AS (
  SELECT substr(UPPER(TRIM(name)),1,1) AS pref
  FROM customer
  GROUP BY pref
  ORDER BY COUNT(*) DESC
  LIMIT 5
)
SELECT c.customer_id,
       c.name,
       COUNT(DISTINCT ac.account_id) AS num_accounts
FROM customer c
LEFT JOIN AccountCustomer ac ON ac.customer_id = c.customer_id
WHERE substr(UPPER(TRIM(c.name)),1,1) IN (SELECT pref FROM popular)
GROUP BY c.customer_id, c.name
ORDER BY c.name;

-- name: Q3_all_customers_and_account_counts
SELECT c.customer_id,
       c.name,
       COUNT(DISTINCT ac.account_id) AS num_accounts
FROM customer c
LEFT JOIN AccountCustomer ac ON ac.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY c.name;

-- name: Q4_account_balance_point_in_time
SELECT t.account_id,
       ROUND(SUM(t.amount),2) AS balance_to_date
FROM Transactions t
WHERE t.account_id = (SELECT account_id FROM Account LIMIT 1)  -- pick one account; replace with specific id
  AND t.ts <= datetime('now')
GROUP BY t.account_id;

-- name: Q5_recent_activity_for_account
-- Show most recent transactions for one account in the last 30 days
SELECT t.account_id, t.txn_id, t.ts, t.merchant, t.amount
FROM Transactions t
WHERE t.account_id = (SELECT account_id FROM Account LIMIT 1)
  AND t.ts >= datetime('now','-30 days')
ORDER BY t.ts DESC
LIMIT 1000;

-- name: Q6_recent_activity_for_top_accounts_30d
-- Recent activity for the most active accounts in last 30 days
WITH hot AS (
  SELECT account_id
  FROM Transactions
  WHERE ts >= datetime('now','-30 days')
  GROUP BY account_id
  ORDER BY COUNT(*) DESC
  LIMIT 1000
)
SELECT t.account_id, t.txn_id, t.ts, t.merchant, t.amount
FROM Transactions t
WHERE t.account_id IN (SELECT account_id FROM hot)
  AND t.ts >= datetime('now','-30 days')
ORDER BY t.ts DESC
LIMIT 1000;

-- name: Q7_daily_txn_volume_by_branch
-- Group daily counts and amounts by branch using Account -> Branch
SELECT a.branch_id,
       date(t.ts) AS txn_date,
       COUNT(*)   AS txn_count,
       ROUND(SUM(t.amount),2) AS total_amount
FROM Transactions t
JOIN Account a ON a.account_id = t.account_id
WHERE t.ts >= date('now','-30 days')
GROUP BY a.branch_id, date(t.ts)
ORDER BY a.branch_id, txn_date;

-- name: Q8_credits_vs_debits
SELECT a.branch_id,
       date(t.ts) AS txn_date,
       COUNT(*) AS txn_count,
       ROUND(SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END),2) AS total_credits,
       ROUND(SUM(CASE WHEN t.amount < 0 THEN -t.amount ELSE 0 END),2) AS total_debits
FROM Transactions t
JOIN Account a ON a.account_id = t.account_id
WHERE t.ts >= date('now','-30 days')
GROUP BY a.branch_id, date(t.ts)
ORDER BY a.branch_id, txn_date;

-- name: Q9_top_customers_by_spend_last_90d
SELECT c.customer_id, c.name,
       ROUND(SUM(CASE WHEN t.amount < 0 THEN -t.amount ELSE 0 END),2) AS spend_90d
FROM customer c
JOIN AccountCustomer ac ON ac.customer_id = c.customer_id
JOIN Account a          ON a.account_id   = ac.account_id
JOIN Transactions t     ON t.account_id   = a.account_id
WHERE t.ts >= date('now','-90 days')
GROUP BY c.customer_id, c.name
ORDER BY spend_90d DESC
LIMIT 10000;

-- name: Q10_multi_branch_usage_30d
WITH windowed AS (
  SELECT c.customer_id, c.name, COUNT(DISTINCT a.branch_id) AS branches_window
  FROM customer c
  JOIN AccountCustomer ac ON ac.customer_id = c.customer_id
  JOIN Account a          ON a.account_id   = ac.account_id
  JOIN Transactions t     ON t.account_id   = a.account_id
  WHERE t.ts >= datetime('now','-30 days')
  GROUP BY c.customer_id, c.name
)
SELECT * FROM windowed
ORDER BY branches_window DESC, name
LIMIT 10000;

-- name: Q11_outstanding_loans_by_primary_branch
SELECT a.branch_id,
       COUNT(*) AS num_loans,
       ROUND(SUM(l.principal),2) AS total_principal
FROM Loan l
LEFT JOIN AccountCustomer ac ON ac.customer_id = l.customer_id AND ac.is_primary = 1
LEFT JOIN Account a          ON a.account_id   = ac.account_id
WHERE COALESCE(l.status,'active') = 'active'
GROUP BY a.branch_id
ORDER BY total_principal DESC;

-- name: Q12_ Average APR by loan type
SELECT loan_type, ROUND(AVG(rate_apr), 2) AS avg_apr
FROM Loan
GROUP BY loan_type
ORDER BY avg_apr DESC;

-- name: Q13_ Portfolio mix by principal
SELECT loan_type, ROUND(SUM(principal), 0) AS total_principal
FROM Loan
GROUP BY loan_type
ORDER BY total_principal DESC;
-- name: Q14_inactive_accounts_60d_by_branch
-- Accounts with no transactions in the last 60 days, summarized by branch
SELECT a.branch_id,
       COUNT(*) AS inactive_accounts
FROM Account a
LEFT JOIN (
  SELECT DISTINCT account_id
  FROM Transactions
  WHERE ts >= date('now','-60 days')
) recent ON recent.account_id = a.account_id
WHERE recent.account_id IS NULL
GROUP BY a.branch_id
ORDER BY inactive_accounts DESC;

-- name: Q15_avg_txn_amount_by_category_30d
-- Average absolute transaction amount and count by category (last 30 days)
SELECT COALESCE(category,'(unknown)') AS category,
       ROUND(AVG(ABS(amount)),2) AS avg_amount,
       COUNT(*) AS txn_count
FROM Transactions
WHERE ts >= date('now','-30 days')
GROUP BY COALESCE(category,'(unknown)')
ORDER BY txn_count DESC;

-- name: Q16_top_merchants_by_gross_volume_30d
-- Top merchants by gross (abs) volume in the last 30 days
SELECT COALESCE(merchant,'(unknown)') AS merchant,
       COUNT(*) AS txn_count,
       ROUND(SUM(ABS(amount)),2) AS gross_volume
FROM Transactions
WHERE ts >= date('now','-30 days')
GROUP BY COALESCE(merchant,'(unknown)')
ORDER BY gross_volume DESC
LIMIT 50;

-- name: Q17_branch_net_flow_by_week_90d
-- Weekly net flow (credits - debits) per branch over the last 90 days
SELECT a.branch_id,
       strftime('%Y-%W', t.ts) AS year_week,
       ROUND(SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END),2) AS total_credits,
       ROUND(SUM(CASE WHEN t.amount < 0 THEN -t.amount ELSE 0 END),2) AS total_debits,
       ROUND(SUM(t.amount),2) AS net_flow
FROM Transactions t
JOIN Account a ON a.account_id = t.account_id
WHERE t.ts >= date('now','-90 days')
GROUP BY a.branch_id, strftime('%Y-%W', t.ts)
ORDER BY year_week, a.branch_id;

-- name: Q18_top_customers_by_inflow_30d
-- Customers ranked by inbound credits in the last 30 days
SELECT c.customer_id,
       c.name,
       ROUND(SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END),2) AS inflow_30d
FROM customer c
JOIN AccountCustomer ac ON ac.customer_id = c.customer_id
JOIN Account a          ON a.account_id   = ac.account_id
JOIN Transactions t     ON t.account_id   = a.account_id
WHERE t.ts >= date('now','-30 days')
GROUP BY c.customer_id, c.name
ORDER BY inflow_30d DESC
LIMIT 10000;

-- name: Q19_card_status_by_brand
-- Card inventory by network brand and lifecycle status
SELECT COALESCE(brand,'(unknown)') AS brand,
       COALESCE(status,'(unknown)') AS status,
       COUNT(*) AS card_count
FROM Card
GROUP BY COALESCE(brand,'(unknown)'), COALESCE(status,'(unknown)')
ORDER BY brand, status;

-- name: Q20_loan_payment_day_distribution_active
-- Distribution of active loans by scheduled payment day (1–31)
SELECT payment_day,
       COUNT(*) AS loans_due
FROM Loan
WHERE COALESCE(status,'active') = 'active'
GROUP BY payment_day
ORDER BY payment_day;
