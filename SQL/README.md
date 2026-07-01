# ECE501C-BankingDB

- **Authors:** Alexander Gomes, Dominic Telles, Sandra Castrejon
- **University:** The University of Arizona  
- **Course:** ECE501 - Data Management
- **Instructor:** Bo Liu 

---
## Table of Contents
- [Project Overview](#project-overview)
- [Database Schema](#banking-schema)
- [Entity-Relationship Model](#entity-relationship-model)
- [Setup Instructions](#setup-intructions)
    - [Prerequisities](#prerequisites)
    - [Python Libraries Used](#python-libraries-used)
- [Project Execution](#project-execution)
- [Project Details](#project-details)
    - [1. Generate Synthetic Data](#1-generate-synthetic-data-synth_datapy)
    - [2. Create Database & Load Data](#2-create-database--load-data)
    - [3. Banking Database](#3-banking-database)
- [Banking DB Experiments](#banking-db-experiments-baseline--optimization--upscaling)
  - [Experiment Support Files](#experiment-support-files)
  - [Experiment 1](#experiment-1-baseline-queries)
  - [Experiment 2](#experiment-2-optimization-queries)
  - [Experiment 3](#experiments-3-upscaling-sample-sizes)
    - [Upscaling Data by 3x](#upscaling-sample-sizes-by-3x-baseline-query-results)
    - [Upscaling Data by 5x](#upscaling-sample-sizes-by-5x-baseline-query-results)
    - [Upscaling Data by 8x](#upscaling-sample-sizes-by-8x-baseline-query-results)
    - [Upscaling Data by 10x](#upscaling-sample-sizes-by-10x-baseline-query-results)
  - [User-Defined Upscaling](#upscaling-sample-sizes-by-user-generated)

## Project Overview
This project impletns a **Banking Database System** designed to build a bank database (DB) and evaluate based on schema design, query optimization, and SQL anomaly detection. 

## Banking Schema 
![Banking Schema Diagram](docs/imgs/BankingSchmea-V2.png)

## Entity-Relationship Model
![Banking ER Model](docs/imgs/BankERmodel.png)

## Setup Intructions
### Prerequisites
- **Python 3.8** or higher
- **SQLite3** installed and accessible in PATH

### Python Libraries Used
| Library | Purpose |
|----------|----------|
| **sqlite3** | Interact with SQLite databases |
| **pandas** | Handle CSV and tabular data |
| **numpy** | Generate randomized numeric data |
| **argparse** | Parse command-line arguments |
| **os / pathlib** | File and directory operations |
| **time / datetime / random** | Generate timestamps and random synthetic data |

Instal libiaries:
``` bash
pip install pandas numpy sqlite3
```

## Project Execution
Run the `run_all.py` to run this entire project.

``` powershell
python .\run_all.py
```
> [!WARNING]
> **DO NOT ADD/PUSH ANY `.sqlite` DB GENERATED FROM `RUN_ALL.PY` TO GIT. THESE FILES ARE TOO LARGE**

## Project Details
### 1. Generate Synthetic Data ('synth_data.py)
The purpose of the **synth_data.py** that this python script generates synthetic banking data used to populate a DB for this project.  This script creates realistic (fake) customer, account, tranaction, loan, and card data so that  his data can be used to run and be evaluated throughout this project. 

### 2. Create Database & Load Data
A DB was created from the CSV's files above using Data Defininiton Language (DDL) scripts.
A data loader script was created called **load_sqlite.py** located in the **etl** folder. The **load_sqlite.py** is to take the CSV files produced from **Step 1** and create a SQLite a 'blank' DB. 

#### DDL scripts: create_tables.sql
- `**DB_Schema_Aperations\ddl\create_tables.sql**` — Defines the schema and integrity: tables, primary keys, foreign keys, and `CHECK`/`UNIQUE` constraints. 

---
**load_sqlite.py** creates the SQLite database using the schema DDL (create_tables.sql), and bulk‐loads the generated CSVs from data/ into the tables with PRAGMA foreign_keys=ON. It standardizes types/timestamps, enforces PK/FK constraints and indexes defined in the DDL, and prints a clear ingest summary. Executing the loader first, **load_sqlite.py**, creates the empty schema inside **bank.sqlite** by executing **create_tables.sql**. Because SQLite stores both schema and data in a single file, **bank.sqlite** is the DB.

> [!WARNING]
> **Only use this if** `bank.sqlite` already exists in `.\DB_Schema_Operations\rawDB\`.
```powershell
# Dry-run (preview only)
Remove-Item -LiteralPath '.\DB_Schema_Operations\rawDB\bank.sqlite' -WhatIf

# Safe delete: only if the file exists
if (Test-Path -LiteralPath '.\DB_Schema_Operations\rawDB\bank.sqlite') {
  Remove-Item -LiteralPath '.\DB_Schema_Operations\rawDB\bank.sqlite' -Force
} else {
  Write-Host 'bank.sqlite not found at .\DB_Schema_Operations\rawDB\'
}
```

``` bash
python .\DB_Schema_Operations\etl\load_sqlite.py --db .\DB_Schema_Operations\rawDB\bank.sqlite --ddl .\DB_Schema_Operations\ddl\create_tables.sql --from-synth --customers 1000 --days 30 --txns 60000 --seed 42
```

### 3. Banking Database
**bank.sqlite** is the raw Databse with Banking Schema and Raw CSV's files generated. To filter out the Raw Data and to only display the schema the following bash must be performed:

```bash
@"
.read .\DB_Schema_Operations\edit\edit.sql
.read .\DB_Schema_Operations\edit\finalDB.sql
"@ | sqlite3 .\DB_Schema_Operations\rawDB\bank.sqlite
```

This Produces the finalized Banking Database called ***FinalBankDB.sqlite***

![Banking DB Simulation Flowchart](docs/imgs/BankingDB_flowchart.png)

---
# Banking DB Experiments: Baseline → Optimization → Upscaling
Each Experiment: Baseline, Optimization, and Upscaling will be evaluated with the following Queries:

- **Q1**: Lists customers whose names start with common initials and counts how many accounts each has.
- **Q2**: Same as Q1 but restricted to the top five initials by frequency in the dataset.
- **Q3**: Returns every customer with the number of accounts linked to them.
- **Q4**: Computes the ledger balance for one account by summing all its transactions up to now.
- **Q5**: Shows the most recent transactions in the last 30 days for a single demo account
- **Q6**: Shows recent (30-day) transactions for the most active accounts, ordered newest first.
- **Q7**: Aggregates daily transaction counts and net amounts per branch over the last 30 days.
- **Q8**: Splits daily branch totals into credits and debits over the last 30 days.
- **Q9**: Ranks customers by spend (outflows) in the last 90 days and returns the top results.
- **Q10**: Counts how many distinct branches each customer used in the last 30 days and lists the top dispersers.
- **Q11**: Sums active loan counts and principal by the customer’s primary branch.
- **Q12**: Calculates the average APR across all active loans, grouped by loan type.
- **Q13**: Aggregates the total outstanding principal amount by loan type to show the bank’s portfolio mix.
- **Q14**: Identifies accounts that have had no transactions in the past 60 days, summarized by branch.
- **Q15**: Computes the average transaction amount and total transaction count by category for the past 30 days.
- **Q16**: Lists the top merchants by total absolute transaction volume within the last 30 days.
- **Q17**: Calculates each branch’s weekly net cash flow (credits minus debits) over the past 90 days.
- **Q18**: Ranks customers by total inbound credits (inflows) during the last 30 days.
- **Q19**: Counts the number of cards grouped by network brand (Visa, Mastercard) and lifecycle status (active, inactive).
- **Q20**: Displays the distribution of active loans by their scheduled payment day (1–31).

---
## Experiment Support Files
Located in the `queries` folder

|Support Files|
|--------------------|
| `queries_workload.sql`|
| `indexes_optimized.sql`|
| `benchmark.py`|
| `print_queries.py`|

### queries_workload.sql
**queries_workload.sql** is the standard set of labeled SQL queries (Q1–Q20) that we run against the Banking DB to measure performance, correctness, and scalability. It represents “typical” banking access patterns: customer lookups, account/transaction history, branch-level summaries, and loan/card portfolio views.
- **Customer lookups**: Q1 - Q3
- **Trasnactional Analytics**: Q4 - Q10, Q15 - Q18
- **Loan & Card Portfolio**: Q11 - Q13, Q19 - Q20

### indexes_optimized.sql
**indexes_optimized.sql** was created to adjust the baseline queries for an optimial results. It is a a SQL script that creates additional indexes on the Banking Database tables after the bank schema and data have been loaded. The bank schema is designed to be correct and normalized, but not necessarily fast for analytical or mixed workloads. This script adds the "Optimization" performance on top of the schema.

### benchmark.py
**benchmark.py** was created to run the names queries in the **queries_workload.sql** (baseline) and **indexes_optimized.sql** (optimized); averages the runtime for both optmized and baseline and saves results the results for both.

The benchmarking script was executed in baseline mode and once in optimized mode—to evaluate query performance before and after indexing improvements. The command parameters specify the database file (*bank.sqlite*), the SQL workload (*queries_workload.sql*), and the output directory (results). A warmup value of 1 was used to allow SQLite to load necessary data into cache before measurements began, ensuring consistent timing conditions. Each workload was then run five times (--runs 5) to capture stable performance metrics and minimize the impact of random fluctuations.The baseline mode represents the unindexed schema, while the optimized mode includes additional indexes and tuning for query efficiency. Comparing these two configurations provides insight into how indexing affects query latency and overall system performance.

### print_queries.py
**print_queries.py** is a script used to run a set of SQL workload queries (Q7, Q11, Q15, Q16, Q20) against the project’s SQLite databases and save the results. It is mainly used to capture query outputs for reports and validation without having to do so manually each time.

---
## Experiment 1: Baseline Queries
**Objective**: Measure the raw query latencies on the unindexed database with default SQLite settings to establish a fair performance reference. This defines the “baseline” for all comparisons.

``` bash
python .\queries\benchmark.py --db .\FinalBankDB.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode baseline --outdir results  
```
### Baseline Query Results
- **Output**: `.results\baseline\results.csv` 

## Experiment 2: Optimization Queries
**Objective**: Apply targeted indexes and PRAGMAs, then re-measure the same workload to quantify speedups and any regressions. The goal is to show how design choices improve latency and efficiency.

``` bash
python .\queries\benchmark.py --db .\FinalBankDB.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode optimized --outdir results
```
### Optimization Query Results
- **Output**: `.results\optimized\results.csv` 

---

## Experiments 3: Upscaling Sample Sizes
**Objective**: Increase dataset size (customers/accounts/transactions) and repeat baseline vs optimized runs to evaluate how performance and speedups scale with data volume. This demonstrates robustness and the cost/benefit of optimizations at larger scales.

### Upscaling Sample Sizes by 3x 
Customer is set to `3,000` 

Transactions is set to `300,000` 
``` bash
python .\DB_Schema_Operations\etl\load_sqlite.py --db .\DB_Schema_Operations\rawDB\bank_x3.sqlite --ddl .\DB_Schema_Operations\ddl\create_tables.sql --from-synth --customers 1000 --days 30 --txns 300000 --seed 42

# Check the finalDB.sql name (lines 6 & 8)
@"
.read .\DB_Schema_Operations\edit\edit.sql
.read .\DB_Schema_Operations\edit\finalDB.sql
"@ | sqlite3 .\DB_Schema_Operations\rawDB\bank_x3.sqlite

#Execute Baeline & Optmization Modes
python .\queries\benchmark.py --db .\FinalBankDB_x3.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode baseline --outdir .\results\3x  
python .\queries\benchmark.py --db .\FinalBankDB_x3.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode optimized --outdir .\results\3x
python .\queries\print_queries.py --db .\FinalBankDB_x3.sqlite --outdir .\results\x3
```
- **Final DB**: `FinalBankDB_x3.sqlite`
- **Baseline Query Results Output**: `.results\x3\baseline\results.csv` 
- **Optimization Query Results Output**: `.results\x3\optimized\results.csv` 
---

### Upscaling Sample Sizes by 5x 
Customer is set to `5,000` 

Transactions is set to `500,000` 
``` bash
python .\DB_Schema_Operations\etl\load_sqlite.py --db .\DB_Schema_Operations\rawDB\bank_x5.sqlite --ddl .\DB_Schema_Operations\ddl\create_tables.sql --from-synth --customers 5000 --days 30 --txns 500000 --seed 42

# Check the finalDB.sql name (lines 6 & 8)
@"
.read .\DB_Schema_Operations\edit\edit.sql
.read .\DB_Schema_Operations\edit\finalDB.sql
"@ | sqlite3 .\DB_Schema_Operations\rawDB\bank_x5.sqlite

#Execute Baeline & Optmization Modes
python .\queries\benchmark.py --db .\FinalBankDB_x5.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode baseline --outdir .\results\5x 
python .\queries\benchmark.py --db .\FinalBankDB_x5.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode optimized --outdir .\results\5x
python .\queries\print_queries.py --db .\FinalBankDB_x5.sqlite --outdir .\results\x5
```
- **Final DB**: `FinalBankDB_x5.sqlite`
- **Baseline Query Results Output**: `.results\x5\baseline\results.csv` 
- **Optimization Query Results Output**: `.results\x5\optimized\results.csv` 
---

### Upscaling Sample Sizes by 8x 
Customer is set to `8,000` 

Transactions is set to `800,000` 
``` bash
python .\DB_Schema_Operations\etl\load_sqlite.py --db .\DB_Schema_Operations\rawDB\bank_x8.sqlite --ddl .\DB_Schema_Operations\ddl\create_tables.sql --from-synth --customers 8000 --days 30 --txns 800000 --seed 42

# Check the finalDB.sql name (lines 6 & 8)
@"
.read .\DB_Schema_Operations\edit\edit.sql
.read .\DB_Schema_Operations\edit\finalDB.sql
"@ | sqlite3 .\DB_Schema_Operations\rawDB\bank_x8.sqlite

#Execute Baeline & Optmization Modes
python .\queries\benchmark.py --db .\FinalBankDB_x8.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode baseline --outdir .\results\8x 
python .\queries\benchmark.py --db .\FinalBankDB_x8.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode optimized --outdir .\results\8x
python .\queries\print_queries.py --db .\FinalBankDB_x8.sqlite --outdir .\results\x8
```
- **Final DB**: `FinalBankDB_x8.sqlite`
- **Baseline Query Results Output**: `.results\x8\baseline\results.csv` 
- **Optimization Query Results Output**: `.results\x8\optimized\results.csv` 
---

### Upscaling Sample Sizes by 10x Baseline Query Results
Customer is set to `10,000` 

Transactions is set to `1,000,000` 
``` bash
python .\DB_Schema_Operations\etl\load_sqlite.py --db .\DB_Schema_Operations\rawDB\bank_x10.sqlite --ddl .\DB_Schema_Operations\ddl\create_tables.sql --from-synth --customers 10000 --days 30 --txns 1000000 --seed 42

# Check the finalDB.sql name (lines 6 & 8)
@"
.read .\DB_Schema_Operations\edit\edit.sql
.read .\DB_Schema_Operations\edit\finalDB.sql
"@ | sqlite3 .\DB_Schema_Operations\rawDB\bank_x10.sqlite

#Execute Baeline & Optmization Modes
python .\queries\benchmark.py --db .\FinalBankDB_x10.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode baseline --outdir .\results\10x 
python .\queries\benchmark.py --db .\FinalBankDB_x10.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode optimized --outdir .\results\10x
python .\queries\print_queries.py --db .\FinalBankDB_x10.sqlite --outdir .\results\x10
```
- **Final DB**: `FinalBankDB_x10.sqlite`
- **Baseline Query Results Output**: `.results\x10\baseline\results.csv` 
- **Optimization Query Results Output**: `.results\x10\optimized\results.csv` 
---

## Upscaling Sample Sizes by USER GENERATED
Customer and Transaction is set to `User Input` 

> [!WARNING]
> **CHANGE_MEE is the same name used in `DB_Schema_Operations\edit\finalDB.sql`

``` bash
python .\DB_Schema_Operations\etl\load_sqlite.py --db .\DB_Schema_Operations\rawDB\CHANGE_ME.sqlite --ddl .\DB_Schema_Operations\ddl\create_tables.sql --from-synth --customers ENTER_NUM --days 30 --txns ENTER_NUM --seed 42

# Check the finalDB.sql name (lines 6 & 8)
@"
.read .\DB_Schema_Operations\edit\edit.sql
.read .\DB_Schema_Operations\edit\finalDB.sql
"@ | sqlite3 .\DB_Schema_Operations\rawDB\CHANGE_ME.sqlite

# CHANGE_MEE is the output from finalDB.sql, these should match
python .\queries\benchmark.py --db .\CHANGE_MEE.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode baseline --outdir .\results\CHANGE_ME  
python .\queries\benchmark.py --db .\CHANGE_MEE.sqlite --sql .\queries\queries_workload.sql --runs 5 --warmup 1 --mode optimized --outdir .\results\CHANGE_NAME_OF_RESULTS
```
- **Final DB**: `CHANGE_MEE.sqlite`
- **Baseline Query Results Output**: `.results\CHANGE_NAME_OF_RESULTS\baseline\results.csv` 
- **Optimization Query Results Output**: `.results\CHANGE_NAME_OF_RESULTS\optimized\results.csv` 
---
