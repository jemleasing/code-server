-- Run these one at a time and check the results.

-- 1. Does tblcollatv actually have non-null CollatV values at all?
SELECT COUNT(*) AS total_rows,
       COUNT(CollatV) AS non_null_collatv
FROM tblcollatv;

-- 2. Spot-check: do LeaseID values look the same in both tables, or is
--    there a formatting mismatch (whitespace, case, leading zeros, a
--    different prefix convention)?
SELECT l.LeaseID AS lease_LeaseID,
       cv.LeaseID AS collatv_LeaseID,
       cv.CollatV
FROM tbllease l
LEFT JOIN tblcollatv cv ON cv.LeaseID = l.LeaseID
LIMIT 20;

-- 3. If #2 shows collatv_LeaseID as NULL for most/all rows, the join key
--    is probably wrong. Try Lease# instead of LeaseID:
SELECT l.LeaseID,
       l.`Lease#` AS lease_number,
       cv.`Lease#` AS collatv_lease_number,
       cv.CollatV
FROM tbllease l
LEFT JOIN tblcollatv cv ON cv.`Lease#` = l.`Lease#`
LIMIT 20;

-- 4. Direct look at tblcollatv on its own, to see what its LeaseID /
--    Lease# values actually look like:
SELECT ID, LeaseID, `Lease#`, CollatV
FROM tblcollatv
WHERE CollatV IS NOT NULL
LIMIT 20;

-- 5. tblcollatv's AUTO_INCREMENT counter is unusually high for a small
--    per-lease table, which can mean it's stale/mostly abandoned. Check
--    whether it even has many rows, and how many of tbllease's accounts
--    it actually covers:
SELECT COUNT(*) AS collatv_row_count FROM tblcollatv;

SELECT COUNT(DISTINCT l.LeaseID) AS leases_total,
       COUNT(DISTINCT cv.LeaseID) AS leases_with_a_collatv_match
FROM tbllease l
LEFT JOIN tblcollatv cv ON cv.LeaseID = l.LeaseID;

-- 6. There are two other candidate tables in the schema with a
--    CollatV-style column. Check whether either of these is actually
--    populated and current, in case tblcollatv is the stale one:

--    6a. tblscorecard - keyed by Lease# only (no LeaseID column)
SELECT COUNT(*) AS total_rows,
       COUNT(CollatV) AS non_null_collatv
FROM tblscorecard;

SELECT l.LeaseID, l.`Lease#`, sc.CollatV
FROM tbllease l
LEFT JOIN tblscorecard sc ON sc.`Lease#` = l.`Lease#`
LIMIT 20;

--    6b. tbl_productsearcheditquery - has LeaseID, Lease#, AND
--        CustomerID, plus two candidate columns: collatV (varchar) and
--        collatV1 (double). This looks like it could be a cached/saved
--        report query rather than live data, so check both.
SELECT COUNT(*) AS total_rows,
       COUNT(collatV) AS non_null_collatv_text,
       COUNT(collatV1) AS non_null_collatv1_numeric
FROM tbl_productsearcheditquery;

SELECT l.LeaseID, l.CustomerID, l.`Lease#`,
       q.collatV, q.collatV1
FROM tbllease l
LEFT JOIN tbl_productsearcheditquery q ON q.LeaseID = l.LeaseID
LIMIT 20;
