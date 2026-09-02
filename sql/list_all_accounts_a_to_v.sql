-- Full list of customer accounts with a LeaseID starting A through V,
-- collated one row per customer (matches /api/leases/account-report).

SELECT
    l.CustomerID,
    l.Customer,
    GROUP_CONCAT(DISTINCT l.`Lease#` ORDER BY l.`Lease#` SEPARATOR ', ') AS LeaseNumbers,
    SUM(l.AmountDue) AS Balance,
    MAX(l.LastPayDate) AS LastPayDate,
    SUM(cv.CollatV) AS TotalCollatV
FROM tbllease l
LEFT JOIN (
    SELECT LeaseID, SUM(CollatV) AS CollatV
    FROM tblcollatv
    GROUP BY LeaseID
) cv ON cv.LeaseID = l.LeaseID
WHERE UPPER(SUBSTRING(l.LeaseID, 1, 1)) BETWEEN 'A' AND 'V'
GROUP BY l.CustomerID, l.Customer
ORDER BY Balance DESC;
