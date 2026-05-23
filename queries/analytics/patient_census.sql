-- Patient Census Report
-- Shows active and discharged patients by facility and encounter type for a given date range.
-- Parameters: :start_date, :end_date

SELECT
    e.facility,
    e.encounter_type,
    COUNT(DISTINCT e.patient_id)                            AS unique_patients,
    COUNT(e.encounter_id)                                   AS total_encounters,
    SUM(CASE WHEN e.status = 'OPEN'   THEN 1 ELSE 0 END)   AS currently_admitted,
    SUM(CASE WHEN e.status = 'CLOSED' THEN 1 ELSE 0 END)   AS discharged,
    ROUND(AVG(
        CASE
            WHEN e.discharge_date IS NOT NULL
            THEN julianday(e.discharge_date) - julianday(e.admit_date)
        END
    ), 1)                                                   AS avg_los_days
FROM encounters e
WHERE e.admit_date BETWEEN :start_date AND :end_date
GROUP BY e.facility, e.encounter_type
ORDER BY e.facility, total_encounters DESC;
