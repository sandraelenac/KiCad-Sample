---
--- RUN THIS AGAINST RAW DB .\DB_Schema_Operations\rawDB
---

PRAGMA foreign_keys=ON;
VACUUM INTO 'CHANGE_ME.sqlite'; --change the name of the file you this to save as

ATTACH DATABASE 'CHANGE_ME.sqlite' AS final; --change the name of the file you this to save as This has to match above

DROP TABLE IF EXISTS final.StgCustomer;
DROP TABLE IF EXISTS final.StgAccount;
DROP TABLE IF EXISTS final.StgBranch;
DROP TABLE IF EXISTS final.StgCard;
DROP TABLE IF EXISTS final.StgLoan;
DROP TABLE IF EXISTS final.StgTxn;
-- DROP TABLE IF EXISTS final.sqlite_sequence;
DROP TABLE IF EXISTS final.sqlite_stat1;

DELETE FROM final.sqlite_sequence; 
DETACH DATABASE final;