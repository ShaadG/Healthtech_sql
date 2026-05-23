# HEALTHTECH Data Repository Demo

A Python CLI tool that simulates a **HEALTHTECH Data Repository** — the SQL database at the core of an Enterprise Health Record platform. Built to demonstrate the technical skills required for a Technical Support Specialist role.

---

## What This Project Demonstrates

| HEALTHTECH Job Requirement | How This Project Shows It |
|---|---|
| Microsoft SQL Server / PostgreSQL | ANSI SQL schema + queries; PostgreSQL migration notes in `docs/setup.md` |
| Analytics, reports, vendor extracts | Named query runner + CSV export (`billing_extract`, `hl7_export`) |
| Troubleshoot and research SQL/database issues | `troubleshoot` command with 5 automated data validation checks |
| Creating and updating documentation | `docs/setup.md`, `docs/query_guide.md`, in-line `--help` on every command |
| Training customers on software | Query guide structured as a customer-facing reference |
| Implementing and supporting DR software | Full schema, seed data, and multi-command CLI mirroring DR support tasks |

---

## Quick Start

```bash
pip install -r requirements.txt
python cli.py setup
python cli.py query patient_census
python cli.py extract billing_extract
python cli.py troubleshoot
```

---

## CLI Reference

```
python cli.py setup              # Create DB schema + seed 50 sample records
python cli.py query <name>       # Run a named analytics query
python cli.py extract <name>     # Export a vendor extract to CSV
python cli.py troubleshoot       # Run all data validation checks
python cli.py list-queries       # Show all available query names
```

All commands accept `--start YYYY-MM-DD` and `--end YYYY-MM-DD` date filters.

---

## Project Structure

```
.
├── cli.py                          # CLI entrypoint (click)
├── db.py                           # SQLite connection + query runner
├── requirements.txt
├── schema/
│   ├── create_tables.sql           # Patients, Providers, Encounters, Labs, Orders
│   └── seed_data.sql               # 50 realistic sample records
├── queries/
│   ├── analytics/
│   │   ├── patient_census.sql
│   │   ├── lab_trends.sql
│   │   └── encounter_summary.sql
│   ├── vendor_extracts/
│   │   ├── billing_extract.sql     # Claims/billing flat file
│   │   └── hl7_export.sql          # HL7 ORU^R01 lab interface export
│   └── troubleshooting/
│       ├── data_validation.sql     # 5 automated data quality checks
│       └── orphan_records.sql      # Foreign key gap detection
└── docs/
    ├── setup.md                    # Installation + PostgreSQL migration guide
    └── query_guide.md              # Reference for all queries and extracts
```

---

## Tech Stack

- **Python 3.10+** with `click` (CLI) and `tabulate` (output formatting)
- **SQLite** (zero-install, standard library) — SQL syntax is PostgreSQL-compatible
- Raw SQL throughout — no ORM — matching how HEALTHTECH's Data Repository is actually queried

---

## See Also

- [Setup Guide](docs/setup.md)
- [Query Guide](docs/query_guide.md)
- [HEALTHTECH_DR_DEMO.md](HEALTHTECH_DR_DEMO.md) — full job-to-project intake form for this project
