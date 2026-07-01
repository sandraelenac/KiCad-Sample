/*
Creates Tables from Data Loader
- ADDRESS
- BRANCH
- ACCOUNT TYPE
- CUSTOMER
- ACCOUNT
- ACCOUNT CUSTOMER
- CUSTOMER ADDRESS
- CARD
- TRANSACTIONS
- LOANS
- HELPFUL INDEXS
*/
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS AccountCustomer;
DROP TABLE IF EXISTS CustomerAddress;
DROP TABLE IF EXISTS Account;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS AccountType;
DROP TABLE IF EXISTS Branch;
DROP TABLE IF EXISTS Address;

CREATE TABLE Address (
  address_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  line1          TEXT NOT NULL,
  line2          TEXT,
  city           TEXT NOT NULL,
  state          TEXT NOT NULL,
  postal_code    TEXT NOT NULL,
  country        TEXT NOT NULL,
  latitude       REAL,
  longitude      REAL
);

-- Branch: PK is the CSV branch_id
CREATE TABLE Branch (
  branch_id      TEXT PRIMARY KEY,           
  address_id     INTEGER NOT NULL,
  branch_code    TEXT NOT NULL UNIQUE,            
  contact_info   TEXT,
  routing_number TEXT UNIQUE,
  FOREIGN KEY(address_id) REFERENCES Address(address_id)
);

-- AccountType:
CREATE TABLE AccountType (
  account_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name            TEXT NOT NULL UNIQUE,
  description     TEXT,
  interest_rate   REAL NOT NULL DEFAULT 0.0
);

-- Customer: PK customer_id 
CREATE TABLE Customer (
  customer_id   TEXT PRIMARY KEY,                 
  name          TEXT NOT NULL,
  phone         TEXT,
  id_number     TEXT     
);

-- Account: PK is the CSV account_id. keep account_number = account_id
CREATE TABLE Account (
  account_id       TEXT PRIMARY KEY,         
  branch_id        TEXT NOT NULL,
  account_type_id  INTEGER NOT NULL,
  account_number   TEXT NOT NULL UNIQUE,     
  is_active        INTEGER NOT NULL DEFAULT 1,
  balance          REAL NOT NULL DEFAULT 0.0,
  FOREIGN KEY(branch_id) REFERENCES Branch(branch_id),
  FOREIGN KEY(account_type_id) REFERENCES AccountType(account_type_id)
);
-- Account Cusomter:
CREATE TABLE AccountCustomer (
  account_id   TEXT NOT NULL,
  customer_id  TEXT NOT NULL,
  is_primary   INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (account_id, customer_id),
  FOREIGN KEY(account_id) REFERENCES Account(account_id),
  FOREIGN KEY(customer_id) REFERENCES Customer(customer_id)
);
-- Cusomter Address:
CREATE TABLE CustomerAddress (
  customer_id   TEXT NOT NULL,
  address_id    INTEGER NOT NULL,
  address_type  TEXT NOT NULL,
  is_primary    INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (customer_id, address_id, address_type),
  FOREIGN KEY(customer_id) REFERENCES Customer(customer_id),
  FOREIGN KEY(address_id) REFERENCES Address(address_id)
);

CREATE TABLE IF NOT EXISTS Card (
  card_id      TEXT PRIMARY KEY,         
  account_id   TEXT NOT NULL,
  last4        TEXT,
  brand        TEXT,
  status       TEXT,
  activated_at TEXT,
  FOREIGN KEY(account_id) REFERENCES Account(account_id)
);
-- Trasnactions:
CREATE TABLE Transactions (
    txn_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    ts TEXT,
    amount REAL,
    merchant TEXT,
    category TEXT,
    counterparty_account_id TEXT,
    description TEXT,
    FOREIGN KEY (account_id) REFERENCES Account(account_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Loan (
  loan_id      TEXT PRIMARY KEY,       
  customer_id  TEXT NOT NULL,
  principal    REAL NOT NULL,
  rate_apr     REAL NOT NULL,
  term_months  INTEGER NOT NULL,
  start_date   TEXT NOT NULL,
  status       TEXT NOT NULL,
  payment_day  INTEGER,
  FOREIGN KEY(customer_id) REFERENCES Customer(customer_id)
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

PRAGMA foreign_keys = ON;
