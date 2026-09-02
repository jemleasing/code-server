-- tbl_b_tickets holds ALL ticket types (parking, red-light camera, tolls),
-- not just EZPass. Run these to see what actually distinguishes EZPass
-- toll violations in your data, then adjust the WHERE clause in
-- get_ezpass_violations() in main.py if needed.

-- 1. What values actually show up in Agency and Authority?
SELECT DISTINCT Agency, Authority, COUNT(*) AS cnt
FROM tbl_b_tickets
GROUP BY Agency, Authority
ORDER BY cnt DESC;

-- 2. Does TollBill# reliably separate toll transactions from other
--    ticket types? (Expect it to be populated for tolls, blank/null
--    for parking or camera tickets.)
SELECT
    CASE WHEN `TollBill#` IS NOT NULL AND `TollBill#` != '' THEN 'has TollBill#' ELSE 'no TollBill#' END AS bucket,
    Agency,
    COUNT(*) AS cnt
FROM tbl_b_tickets
GROUP BY bucket, Agency
ORDER BY cnt DESC;

-- 3. Spot-check: pull 20 rows that match the current filter used in
--    get_ezpass_violations(), to eyeball whether they look right.
SELECT TicketID, Lease#, Agency, Authority, `TollBill#`, DateTimeOfViolation, ViolationDescription
FROM tbl_b_tickets
WHERE DateTimeOfViolation >= NOW() - INTERVAL 180 DAY
  AND (
      (`TollBill#` IS NOT NULL AND `TollBill#` != '')
      OR Agency LIKE '%EZ%'
      OR Authority LIKE '%EZ%PASS%'
  )
LIMIT 20;
