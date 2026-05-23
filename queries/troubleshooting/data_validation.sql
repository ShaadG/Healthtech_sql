-- Data Validation Checks
-- Runs a series of named checks against the Data Repository to identify
-- common data quality issues. Each check returns a row count — 0 means clean.

-- CHECK 1: Encounters missing primary diagnosis
SELECT
    'encounters_missing_dx'     AS check_name,
    COUNT(*)                    AS issue_count,
    'Encounters with no primary_dx_code assigned' AS description
FROM encounters
WHERE primary_dx_code IS NULL OR TRIM(primary_dx_code) = '';

-- CHECK 2: Lab results with no result value and status FINAL
SELECT
    'final_labs_missing_value'  AS check_name,
    COUNT(*)                    AS issue_count,
    'Final lab results where result_value is NULL' AS description
FROM lab_results
WHERE status = 'FINAL' AND result_value IS NULL;

-- CHECK 3: Discharge date before admit date
SELECT
    'discharge_before_admit'    AS check_name,
    COUNT(*)                    AS issue_count,
    'Encounters where discharge_date precedes admit_date' AS description
FROM encounters
WHERE discharge_date IS NOT NULL
  AND discharge_date < admit_date;

-- CHECK 4: Orders referencing non-existent encounters
SELECT
    'orphan_orders'             AS check_name,
    COUNT(*)                    AS issue_count,
    'Orders with no matching encounter record' AS description
FROM orders o
WHERE NOT EXISTS (
    SELECT 1 FROM encounters e WHERE e.encounter_id = o.encounter_id
);

-- CHECK 5: Patients with duplicate MRN (should be 0 due to UNIQUE constraint, but useful for migrations)
SELECT
    'duplicate_mrn'             AS check_name,
    COUNT(*) - COUNT(DISTINCT mrn) AS issue_count,
    'Patients sharing the same Medical Record Number' AS description
FROM patients;
