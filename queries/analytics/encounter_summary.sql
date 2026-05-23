-- Encounter Summary by Provider
-- Summarizes encounter volume, diagnoses, and average length of stay per provider.
-- Parameters: :start_date, :end_date

SELECT
    p.last_name || ', ' || p.first_name  AS provider_name,
    p.specialty,
    p.department,
    COUNT(e.encounter_id)                AS total_encounters,
    COUNT(DISTINCT e.patient_id)         AS unique_patients,
    ROUND(AVG(
        CASE
            WHEN e.discharge_date IS NOT NULL
            THEN julianday(e.discharge_date) - julianday(e.admit_date)
        END
    ), 1)                                AS avg_los_days,
    -- Top diagnosis by volume for this provider
    (
        SELECT e2.primary_dx_desc
        FROM encounters e2
        WHERE e2.provider_id = p.provider_id
          AND e2.admit_date BETWEEN :start_date AND :end_date
        GROUP BY e2.primary_dx_desc
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )                                    AS most_common_diagnosis
FROM providers p
JOIN encounters e ON e.provider_id = p.provider_id
WHERE e.admit_date BETWEEN :start_date AND :end_date
GROUP BY p.provider_id, p.last_name, p.first_name, p.specialty, p.department
ORDER BY total_encounters DESC;
