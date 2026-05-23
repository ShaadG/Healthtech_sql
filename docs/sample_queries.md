# Sample SQL Queries — HEALTHTECH Data Repository

Ten functional queries demonstrating core Data Repository support skills:
patient analytics, encounter reporting, lab monitoring, provider workload,
and data quality validation.

All queries run against `healthtech_dr.db` using SQLite syntax.

---

## Q1: Patient Breakdown by Gender + Average Age

```sql
SELECT gender,
       COUNT(*) AS total_patients,
       ROUND(AVG(strftime('%Y','now') - strftime('%Y', dob))) AS avg_age
FROM patients
GROUP BY gender
ORDER BY gender;
```

**Sample output:**

| gender | total_patients | avg_age |
|--------|---------------|---------|
| F      | 5             | 48      |
| M      | 5             | 74      |

**What it shows:** Basic demographic summary. Useful as a starting point for any
patient population report or census request.

---

## Q2: Encounter Volume by Type and Facility

```sql
SELECT facility, encounter_type,
       COUNT(*) AS total_encounters,
       SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) AS currently_open
FROM encounters
GROUP BY facility, encounter_type
ORDER BY total_encounters DESC;
```

**Sample output:**

| facility     | encounter_type | total_encounters | currently_open |
|--------------|---------------|-----------------|----------------|
| Main Campus  | INPATIENT      | 5               | 0              |
| Main Campus  | OUTPATIENT     | 5               | 0              |
| North Clinic | OUTPATIENT     | 4               | 1              |
| Heart Center | OUTPATIENT     | 2               | 0              |
| Main Campus  | ED             | 2               | 0              |
| South Clinic | OUTPATIENT     | 1               | 0              |
| Telehealth   | TELEHEALTH     | 1               | 0              |

**What it shows:** Facility-level census snapshot. The `currently_open` column
flags active encounters — useful for bed management and daily volume reports.

---

## Q3: Average Length of Stay — Inpatient Only

```sql
SELECT encounter_type,
       COUNT(*) AS encounters,
       ROUND(AVG(julianday(discharge_date) - julianday(admit_date)), 1) AS avg_los_days,
       MAX(CAST(julianday(discharge_date) - julianday(admit_date) AS INT)) AS max_los_days
FROM encounters
WHERE encounter_type = 'INPATIENT'
GROUP BY encounter_type;
```

**Sample output:**

| encounter_type | encounters | avg_los_days | max_los_days |
|---------------|-----------|-------------|-------------|
| INPATIENT      | 5         | 6.4         | 8           |

**What it shows:** Length-of-stay (LOS) analytics — a core metric in inpatient
reporting. Uses `julianday()` for precise day-difference calculation.

---

## Q4: Provider Workload — Encounters and Unique Patients

```sql
SELECT p.last_name || ', ' || p.first_name AS provider,
       p.specialty,
       COUNT(e.encounter_id)        AS total_encounters,
       COUNT(DISTINCT e.patient_id) AS unique_patients
FROM providers p
LEFT JOIN encounters e ON p.provider_id = e.provider_id
GROUP BY p.provider_id
ORDER BY total_encounters DESC;
```

**Sample output:**

| provider        | specialty          | total_encounters | unique_patients |
|-----------------|--------------------|-----------------|-----------------|
| Chen, Alice     | Internal Medicine  | 7               | 5               |
| Patel, Raj      | Cardiology         | 6               | 4               |
| Harris, Maria   | Hospitalist        | 4               | 3               |
| Thompson, Sara  | Emergency Medicine | 2               | 2               |
| Lee, James      | Laboratory         | 1               | 1               |

**What it shows:** Provider productivity report. `LEFT JOIN` ensures providers
with zero encounters still appear. `COUNT(DISTINCT)` separates visit volume
from unique patient load.

---

## Q5: Patients with Multiple Encounters — Readmission Risk

```sql
SELECT pt.last_name || ', ' || pt.first_name AS patient,
       pt.mrn,
       COUNT(e.encounter_id) AS visit_count,
       MIN(e.admit_date)     AS first_visit,
       MAX(e.admit_date)     AS last_visit
FROM patients pt
JOIN encounters e ON pt.patient_id = e.patient_id
GROUP BY pt.patient_id
HAVING COUNT(e.encounter_id) > 1
ORDER BY visit_count DESC, last_visit DESC;
```

**Sample output (top 4):**

| patient           | mrn     | visit_count | first_visit | last_visit |
|-------------------|---------|------------|------------|-----------|
| Martinez, Susan   | MRN-010 | 2          | 2024-03-20 | 2024-07-01 |
| Wilson, David     | MRN-009 | 2          | 2024-03-10 | 2024-06-20 |
| Davis, Elizabeth  | MRN-008 | 2          | 2024-03-05 | 2024-06-10 |
| Miller, William   | MRN-007 | 2          | 2024-02-20 | 2024-06-01 |

**What it shows:** Readmission identification using `HAVING`. A common clinical
operations query — flags patients who may need care coordination follow-up.

---

## Q6: Abnormal and Critical Lab Results

```sql
SELECT pt.mrn,
       pt.last_name || ', ' || pt.first_name AS patient,
       lr.test_name, lr.result_value, lr.result_unit,
       lr.reference_range,
       CASE lr.abnormal_flag
           WHEN 'C' THEN 'CRITICAL'
           WHEN 'H' THEN 'HIGH'
           WHEN 'L' THEN 'LOW'
           ELSE lr.abnormal_flag
       END AS flag,
       lr.status,
       lr.result_date
FROM lab_results lr
JOIN patients pt ON lr.patient_id = pt.patient_id
WHERE lr.abnormal_flag IN ('C', 'H', 'L')
ORDER BY
    CASE lr.abnormal_flag WHEN 'C' THEN 0 WHEN 'H' THEN 1 ELSE 2 END,
    lr.result_date DESC
LIMIT 10;
```

> **Note:** `abnormal_flag` uses single-character codes: `C` = Critical,
> `H` = High, `L` = Low, `N` = Normal.

**Sample output (top 4):**

| mrn     | patient         | test_name | result_value | result_unit | flag     | status |
|---------|-----------------|-----------|-------------|-------------|----------|--------|
| MRN-004 | Brown, Linda    | Glucose   | 245         | mg/dL       | CRITICAL | FINAL  |
| MRN-009 | Wilson, David   | NT-proBNP | 1850        | pg/mL       | HIGH     | FINAL  |
| MRN-007 | Miller, William | Creatinine| 2.6         | mg/dL       | HIGH     | FINAL  |
| MRN-005 | Jones, Michael  | INR       | 2.8         | ratio       | HIGH     | FINAL  |

**What it shows:** Critical value reporting — a patient safety priority in any
clinical data environment. `CASE` translates raw codes into readable labels.
Results are sorted with CRITICAL first.

---

## Q7: Open Orders by Type — Workflow Status Check

```sql
SELECT order_type, status,
       COUNT(*) AS total_orders
FROM orders
GROUP BY order_type, status
ORDER BY order_type, total_orders DESC;
```

**Sample output:**

| order_type | status    | total_orders |
|-----------|-----------|-------------|
| LAB        | COMPLETED | 13          |
| LAB        | PENDING   | 2           |
| MEDICATION | ACTIVE    | 5           |
| MEDICATION | COMPLETED | 2           |
| RADIOLOGY  | COMPLETED | 3           |

**What it shows:** Order workflow status snapshot. Useful for identifying
backlogs — e.g., 2 pending LAB orders and 5 active MEDICATION orders that
may need follow-up.

---

## Q8: Most Common ICD-10 Diagnosis Codes

```sql
SELECT primary_dx_code,
       primary_dx_desc,
       COUNT(*) AS encounter_count
FROM encounters
GROUP BY primary_dx_code
ORDER BY encounter_count DESC
LIMIT 8;
```

**Sample output:**

| primary_dx_code | primary_dx_desc                          | encounter_count |
|----------------|------------------------------------------|----------------|
| Z00.00         | Encounter for general adult examination  | 3              |
| E11.9          | Type 2 diabetes mellitus                 | 3              |
| N18.3          | Chronic kidney disease stage 3           | 2              |
| I50.9          | Heart failure, unspecified               | 2              |
| I25.10         | Atherosclerotic heart disease            | 2              |
| I10            | Essential hypertension                   | 2              |

**What it shows:** Diagnosis frequency analysis by ICD-10 code. Used for
population health reporting, quality metrics, and payer audits.

---

## Q9: Pending Lab Results — Turnaround Monitoring

```sql
SELECT lr.test_name,
       COUNT(*)        AS pending_count,
       MIN(lr.order_date) AS oldest_order
FROM lab_results lr
WHERE lr.status = 'PENDING'
GROUP BY lr.test_name
ORDER BY pending_count DESC;
```

**Sample output:**

| test_name | pending_count | oldest_order |
|-----------|--------------|-------------|
| HbA1c     | 2            | 2024-06-10  |

**What it shows:** Lab turnaround time (TAT) monitoring — identifies tests
sitting in PENDING status. A core data repository support task when clinical
staff escalate missing results.

---

## Q10: Data Quality — Open Encounters Missing Discharge

```sql
SELECT e.encounter_id, pt.mrn,
       pt.last_name || ', ' || pt.first_name AS patient,
       e.encounter_type, e.admit_date,
       e.discharge_date, e.status
FROM encounters e
JOIN patients pt ON e.patient_id = pt.patient_id
WHERE e.status = 'OPEN'
ORDER BY e.admit_date;
```

**Sample output:**

| encounter_id | mrn     | patient         | encounter_type | admit_date | discharge_date | status |
|-------------|---------|-----------------|---------------|-----------|---------------|--------|
| 20          | MRN-010 | Martinez, Susan | OUTPATIENT    | 2024-07-01 | 2024-07-01   | OPEN   |

**What it shows:** Data integrity validation — surfaces encounters still marked
OPEN that may have been missed during discharge reconciliation. A common
support ticket type in healthcare data environments.

---

## Running These Queries

**Via the CLI** (for named queries already in `queries/`):
```bash
.venv/bin/python cli.py query patient_census
.venv/bin/python cli.py query lab_trends
.venv/bin/python cli.py query encounter_summary
.venv/bin/python cli.py list-queries
```

**Directly against the database:**
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('healthtech_dr.db')
for row in conn.execute('SELECT mrn, last_name FROM patients LIMIT 5'):
    print(row)
"
```

**Or with any SQLite client** pointed at `healthtech_dr.db`.
