/*

*/
CREATE INDEX IF NOT EXISTS idx_txn_acct_ts ON transactions(account_id, ts);
CREATE INDEX IF NOT EXISTS idx_txn_ts ON transactions(ts);
CREATE INDEX IF NOT EXISTS idx_acct_customer ON accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_cards_account ON cards(account_id);
CREATE INDEX IF NOT EXISTS idx_loans_customer ON loans(customer_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity, entity_id, ts);
