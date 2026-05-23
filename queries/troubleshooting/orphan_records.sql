-- Orphan Record Detection
-- Identifies records that are missing required parent relationships.
-- Run after data migrations or interface imports to catch referential integrity gaps.

-- Lab results with no matching patient
SELECT
    'lab_results'               AS table_name,
    'missing_patient'           AS issue_type,
    lr.result_id                AS record_id,
    lr.patient_id               AS broken_fk,
    lr.order_date               AS record_date
FROM lab_results lr
WHERE NOT EXISTS (
    SELECT 1 FROM patients p WHERE p.patient_id = lr.patient_id
)

UNION ALL

-- Encounters with no matching patient
SELECT
    'encounters',
    'missing_patient',
    e.encounter_id,
    e.patient_id,
    e.admit_date
FROM encounters e
WHERE NOT EXISTS (
    SELECT 1 FROM patients p WHERE p.patient_id = e.patient_id
)

UNION ALL

-- Encounters with no matching provider
SELECT
    'encounters',
    'missing_provider',
    e.encounter_id,
    e.provider_id,
    e.admit_date
FROM encounters e
WHERE NOT EXISTS (
    SELECT 1 FROM providers pr WHERE pr.provider_id = e.provider_id
)

UNION ALL

-- Orders with no matching patient
SELECT
    'orders',
    'missing_patient',
    o.order_id,
    o.patient_id,
    o.order_date
FROM orders o
WHERE NOT EXISTS (
    SELECT 1 FROM patients p WHERE p.patient_id = o.patient_id
)

ORDER BY table_name, issue_type, record_id;
