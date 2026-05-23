-- Lab Result Trends
-- Shows abnormal lab rates by test and flags critical results.
-- Useful for quality reporting and identifying high-risk patient populations.
-- Parameters: :start_date, :end_date

SELECT
    lr.test_name,
    lr.result_unit,
    COUNT(*)                                                        AS total_results,
    SUM(CASE WHEN lr.abnormal_flag IN ('H','L') THEN 1 ELSE 0 END) AS abnormal_count,
    SUM(CASE WHEN lr.abnormal_flag = 'C'        THEN 1 ELSE 0 END) AS critical_count,
    SUM(CASE WHEN lr.status = 'PENDING'         THEN 1 ELSE 0 END) AS pending_count,
    ROUND(
        100.0 * SUM(CASE WHEN lr.abnormal_flag IN ('H','L','C') THEN 1 ELSE 0 END)
        / COUNT(*), 1
    )                                                               AS abnormal_rate_pct
FROM lab_results lr
WHERE lr.order_date BETWEEN :start_date AND :end_date
GROUP BY lr.test_name, lr.result_unit
ORDER BY critical_count DESC, abnormal_count DESC;
