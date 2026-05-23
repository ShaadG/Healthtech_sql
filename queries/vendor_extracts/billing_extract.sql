-- Billing Vendor Extract
-- Flat-file format for submission to billing/claims systems.
-- One row per encounter with patient demographics, provider NPI, and primary diagnosis.
-- Parameters: :start_date, :end_date

SELECT
    e.encounter_id                                  AS ENCOUNTER_ID,
    p.mrn                                           AS PATIENT_MRN,
    p.last_name                                     AS PATIENT_LAST,
    p.first_name                                    AS PATIENT_FIRST,
    p.dob                                           AS PATIENT_DOB,
    p.gender                                        AS PATIENT_GENDER,
    p.zip_code                                      AS PATIENT_ZIP,
    e.encounter_type                                AS VISIT_TYPE,
    e.admit_date                                    AS ADMIT_DATE,
    e.discharge_date                                AS DISCHARGE_DATE,
    COALESCE(
        CAST(julianday(e.discharge_date) - julianday(e.admit_date) AS INTEGER),
        0
    )                                               AS LOS_DAYS,
    e.primary_dx_code                               AS DX_CODE_PRIMARY,
    e.primary_dx_desc                               AS DX_DESC_PRIMARY,
    e.facility                                      AS FACILITY,
    pr.npi                                          AS PROVIDER_NPI,
    pr.last_name || ', ' || pr.first_name           AS PROVIDER_NAME,
    pr.specialty                                    AS PROVIDER_SPECIALTY
FROM encounters e
JOIN patients  p  ON p.patient_id  = e.patient_id
JOIN providers pr ON pr.provider_id = e.provider_id
WHERE e.status = 'CLOSED'
  AND e.admit_date BETWEEN :start_date AND :end_date
ORDER BY e.admit_date, e.encounter_id;
