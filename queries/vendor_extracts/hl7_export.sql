-- HL7 Lab Result Export
-- Structured extract for downstream HL7 interfaces and lab information systems.
-- Includes patient context, ordering provider, and result details.
-- Parameters: :start_date, :end_date

SELECT
    lr.result_id                                    AS MESSAGE_ID,
    'ORU^R01'                                       AS MESSAGE_TYPE,
    p.mrn                                           AS PATIENT_ID,
    p.last_name                                     AS PATIENT_LAST,
    p.first_name                                    AS PATIENT_FIRST,
    p.dob                                           AS PATIENT_DOB,
    p.gender                                        AS PATIENT_SEX,
    lr.order_date                                   AS ORDER_DATE,
    lr.result_date                                  AS RESULT_DATE,
    lr.test_code                                    AS LOINC_CODE,
    lr.test_name                                    AS TEST_NAME,
    lr.result_value                                 AS RESULT_VALUE,
    lr.result_unit                                  AS RESULT_UNITS,
    lr.reference_range                              AS REFERENCE_RANGE,
    COALESCE(lr.abnormal_flag, 'N')                 AS ABNORMAL_FLAG,
    lr.status                                       AS RESULT_STATUS,
    pr.npi                                          AS ORDERING_PROVIDER_NPI,
    pr.last_name || '^' || pr.first_name            AS ORDERING_PROVIDER,
    e.facility                                      AS SENDING_FACILITY
FROM lab_results lr
JOIN patients  p  ON p.patient_id   = lr.patient_id
JOIN encounters e  ON e.encounter_id = lr.encounter_id
JOIN providers pr ON pr.provider_id  = e.provider_id
WHERE lr.order_date BETWEEN :start_date AND :end_date
  AND lr.status IN ('FINAL', 'CORRECTED')
ORDER BY lr.result_date, lr.result_id;
