/*
Creates Tables from Generating CSVs 
*/
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS AccountCustomer;
DROP TABLE IF EXISTS CustomerAddress;
DROP TABLE IF EXISTS Account;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS AccountType;
DROP TABLE IF EXISTS Branch;
DROP TABLE IF EXISTS Address;

-- ===========================
--  Address Table
-- ===========================
CREATE TABLE Address (
  address_id   TEXT PRIMARY KEY,
  line1        TEXT NOT NULL,
  line2        TEXT,
  city         TEXT NOT NULL,
  state        TEXT NOT NULL,
  postal_code  TEXT NOT NULL,
  country      TEXT NOT NULL
);

-- ===========================
--  Customer Table
-- ===========================
CREATE TABLE Customer (
  customer_id  TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  phone        TEXT,
  id_number    TEXT,
  created_at   TEXT DEFAULT (datetime('now'))
);

-- ===========================
--  CustomerAddress (M:N)
-- ===========================
CREATE TABLE CustomerAddress (
  customer_id   TEXT NOT NULL,
  address_id    TEXT NOT NULL,
  address_type  TEXT NOT NULL,
  is_primary    BOOLEAN NOT NULL DEFAULT 0,
  PRIMARY KEY (customer_id, address_id, address_type),
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (address_id) REFERENCES Address(address_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- ===========================
--  Branch Table
-- ===========================
CREATE TABLE Branch (
  branch_id      TEXT PRIMARY KEY,
  address_id     TEXT NOT NULL,
  branch_code    TEXT NOT NULL UNIQUE,
  contact_info   TEXT,
  routing_number TEXT UNIQUE,
  FOREIGN KEY (address_id) REFERENCES Address(address_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ===========================
--  AccountType Table
-- ===========================
CREATE TABLE AccountType (
  account_type_id TEXT PRIMARY KEY,
  name            TEXT NOT NULL UNIQUE,
  description     TEXT,
  interest_rate   REAL NOT NULL DEFAULT 0.0
);

-- ===========================
--  Account Table
-- ===========================
CREATE TABLE Account (
  account_id       TEXT PRIMARY KEY,
  branch_id        TEXT NOT NULL,
  account_type_id  TEXT NOT NULL,
  account_number   TEXT NOT NULL UNIQUE,
  is_active        BOOLEAN NOT NULL DEFAULT 1,
  balance          REAL NOT NULL DEFAULT 0.0,
  created_at       TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (branch_id) REFERENCES Branch(branch_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (account_type_id) REFERENCES AccountType(account_type_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ===========================
--  AccountCustomer (M:N)
-- ===========================
CREATE TABLE AccountCustomer (
  account_id   TEXT NOT NULL,
  customer_id  TEXT NOT NULL,
  is_primary   BOOLEAN NOT NULL DEFAULT 0,
  PRIMARY KEY (account_id, customer_id),
  FOREIGN KEY (account_id) REFERENCES Account(account_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- ===========================
--  Transactions Table
-- ===========================
CREATE TABLE Transactions (
  txn_id                  TEXT PRIMARY KEY,
  account_id              TEXT NOT NULL,
  counterparty_account_id TEXT,
  txn_type                TEXT NOT NULL, -- e.g., 'deposit', 'withdrawal', 'transfer'
  ts                      TEXT NOT NULL DEFAULT (datetime('now')),
  amount                  REAL NOT NULL,
  merchant                TEXT,
  category                TEXT,
  description             TEXT,
  FOREIGN KEY (account_id) REFERENCES Account(account_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (counterparty_account_id) REFERENCES Account(account_id)
    ON UPDATE CASCADE ON DELETE SET NULL
);

-- ===========================
--  Loan Table
-- ===========================
CREATE TABLE Loan (
  loan_id      TEXT PRIMARY KEY,
  account_id   TEXT NOT NULL,
  principal    REAL NOT NULL,
  rate_apr     REAL NOT NULL,
  term_months  INTEGER NOT NULL,
  start_date   TEXT NOT NULL,
  status       TEXT NOT NULL,
  payment_day  TEXT,
  FOREIGN KEY (account_id) REFERENCES Account(account_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);


-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_account_branch        ON Account(branch_id);
CREATE INDEX IF NOT EXISTS idx_account_type          ON Account(account_type_id);
CREATE INDEX IF NOT EXISTS idx_acctcust_customer     ON AccountCustomer(customer_id);
CREATE INDEX IF NOT EXISTS idx_custaddr_customer     ON CustomerAddress(customer_id);
CREATE INDEX IF NOT EXISTS idx_branch_address        ON Branch(address_id);
CREATE INDEX IF NOT EXISTS idx_txn_account ON Transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_card_account ON Card(account_id);
CREATE INDEX IF NOT EXISTS idx_loan_customer ON Loan(customer_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_address_nk
  ON Address(line1, COALESCE(line2,''), city, state, postal_code, country);

