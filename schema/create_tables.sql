-- HEALTHTECH Data Repository Demo Schema
-- Compatible with SQLite and PostgreSQL

CREATE TABLE IF NOT EXISTS patients (
    patient_id      INTEGER PRIMARY KEY,
    mrn             TEXT NOT NULL UNIQUE,           -- Medical Record Number
    last_name       TEXT NOT NULL,
    first_name      TEXT NOT NULL,
    dob             TEXT NOT NULL,                  -- ISO 8601: YYYY-MM-DD
    gender          TEXT CHECK(gender IN ('M','F','U')),
    zip_code        TEXT,
    created_at      TEXT DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS providers (
    provider_id     INTEGER PRIMARY KEY,
    npi             TEXT NOT NULL UNIQUE,           -- National Provider Identifier
    last_name       TEXT NOT NULL,
    first_name      TEXT NOT NULL,
    specialty       TEXT,
    department      TEXT
);

CREATE TABLE IF NOT EXISTS encounters (
    encounter_id    INTEGER PRIMARY KEY,
    patient_id      INTEGER NOT NULL REFERENCES patients(patient_id),
    provider_id     INTEGER NOT NULL REFERENCES providers(provider_id),
    encounter_type  TEXT CHECK(encounter_type IN ('INPATIENT','OUTPATIENT','ED','TELEHEALTH')),
    admit_date      TEXT NOT NULL,
    discharge_date  TEXT,
    primary_dx_code TEXT,                           -- ICD-10
    primary_dx_desc TEXT,
    facility        TEXT,
    status          TEXT CHECK(status IN ('OPEN','CLOSED','CANCELLED')) DEFAULT 'CLOSED'
);

CREATE TABLE IF NOT EXISTS lab_results (
    result_id       INTEGER PRIMARY KEY,
    encounter_id    INTEGER NOT NULL REFERENCES encounters(encounter_id),
    patient_id      INTEGER NOT NULL REFERENCES patients(patient_id),
    order_date      TEXT NOT NULL,
    result_date     TEXT,
    test_code       TEXT NOT NULL,                  -- LOINC code
    test_name       TEXT NOT NULL,
    result_value    TEXT,
    result_unit     TEXT,
    reference_range TEXT,
    abnormal_flag   TEXT CHECK(abnormal_flag IN ('H','L','C','N',NULL)), -- High/Low/Critical/Normal
    status          TEXT CHECK(status IN ('FINAL','PENDING','CORRECTED')) DEFAULT 'FINAL'
);

CREATE TABLE IF NOT EXISTS orders (
    order_id        INTEGER PRIMARY KEY,
    encounter_id    INTEGER NOT NULL REFERENCES encounters(encounter_id),
    patient_id      INTEGER NOT NULL REFERENCES patients(patient_id),
    order_date      TEXT NOT NULL,
    order_type      TEXT CHECK(order_type IN ('LAB','MEDICATION','RADIOLOGY','PROCEDURE')),
    order_code      TEXT,
    order_desc      TEXT NOT NULL,
    ordering_provider_id INTEGER REFERENCES providers(provider_id),
    status          TEXT CHECK(status IN ('ACTIVE','COMPLETED','CANCELLED','PENDING')) DEFAULT 'COMPLETED'
);
