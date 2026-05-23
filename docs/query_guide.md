# Query Guide

All queries live in the `queries/` directory. They accept `--start` and `--end` date parameters (YYYY-MM-DD). Defaults to the past 365 days when omitted.

---

## Analytics Queries

### `patient_census`
**Purpose:** Daily/monthly census report by facility and encounter type.

```bash
python cli.py query patient_census
python cli.py query patient_census --start 2024-01-01 --end 2024-06-30
```

**Key columns:** facility, encounter_type, unique_patients, total_encounters, currently_admitted, avg_los_days

**Use in HEALTHTECH support:** Customers frequently request census data to staff units and report to administration. This query mirrors the DR tables queried for those standard reports.

---

### `lab_trends`
**Purpose:** Abnormal and critical lab rates by test — useful for quality and population health reporting.

```bash
python cli.py query lab_trends
```

**Key columns:** test_name, total_results, abnormal_count, critical_count, pending_count, abnormal_rate_pct

**Use in HEALTHTECH support:** Customers ask why certain lab flags appear in reports or extract files. This query surfaces the underlying data so you can confirm what the DR contains before troubleshooting interface issues.

---

### `encounter_summary`
**Purpose:** Provider-level encounter volume, patient counts, average LOS, and top diagnosis.

```bash
python cli.py query encounter_summary
```

**Key columns:** provider_name, specialty, total_encounters, unique_patients, avg_los_days, most_common_diagnosis

---

## Vendor Extracts

### `billing_extract`
**Purpose:** Flat CSV export for billing/claims systems. One row per closed encounter.

```bash
python cli.py extract billing_extract
python cli.py extract billing_extract --output /tmp/billing_jan2024.csv --start 2024-01-01 --end 2024-01-31
```

**Output file:** `exports/billing_extract.csv`

---

### `hl7_export`
**Purpose:** Structured lab result export for HL7 ORU^R01 interfaces and LIS systems.

```bash
python cli.py extract hl7_export
```

**Output file:** `exports/hl7_export.csv`

**Note:** The MESSAGE_TYPE column (`ORU^R01`) and SENDING_FACILITY fields are pre-populated to match HL7 2.x segment expectations. A real interface engine (Mirth, Rhapsody, Iguana) would consume this CSV and generate the actual HL7 message.

---

## Troubleshooting Queries

### `data_validation`
**Purpose:** Five automated checks for common data quality issues. Run via `troubleshoot` command.

```bash
python cli.py troubleshoot
```

**Checks:**
| Check | What it catches |
|---|---|
| `encounters_missing_dx` | Encounters with no ICD-10 code |
| `final_labs_missing_value` | FINAL lab results with NULL result_value |
| `discharge_before_admit` | Date logic errors from interface imports |
| `orphan_orders` | Orders with no matching encounter |
| `duplicate_mrn` | Patients sharing a Medical Record Number |

---

### `orphan_records`
**Purpose:** Finds records missing required foreign key relationships — common after data migrations or interface go-lives.

```bash
python cli.py query orphan_records
```

---

## Adding New Queries

1. Create `queries/<category>/<query_name>.sql`
2. Use `:start_date` and `:end_date` as named parameters
3. Run with `python cli.py query <query_name>`

The CLI automatically discovers all `.sql` files — no registration needed.
