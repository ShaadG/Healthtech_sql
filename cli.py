"""HEALTHTECH Data Repository Demo CLI"""

import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import click

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

import db


def _print_table(columns: list[str], rows: list[tuple], fmt: str = "rounded_outline") -> None:
    if not rows:
        click.echo("  (no results)")
        return
    if HAS_TABULATE:
        click.echo(tabulate(rows, headers=columns, tablefmt=fmt))
    else:
        # Minimal fallback if tabulate not installed
        widths = [max(len(str(c)), max((len(str(r[i])) for r in rows), default=0))
                  for i, c in enumerate(columns)]
        sep = "  ".join("-" * w for w in widths)
        click.echo("  ".join(str(c).ljust(w) for c, w in zip(columns, widths)))
        click.echo(sep)
        for row in rows:
            click.echo("  ".join(str(v).ljust(w) for v, w in zip(row, widths)))


def _default_dates() -> tuple[str, str]:
    today = date.today()
    return (today - timedelta(days=730)).isoformat(), today.isoformat()


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _validate_date(value: str | None, label: str) -> str | None:
    if value is None:
        return None
    if not _DATE_RE.match(value):
        raise click.BadParameter(f"'{value}' is not a valid date. Use YYYY-MM-DD.", param_hint=label)
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise click.BadParameter(f"'{value}' is not a valid date. Use YYYY-MM-DD.", param_hint=label)
    return value


@click.group()
def cli():
    """HEALTHTECH Data Repository Demo Tool

    Simulates a healthcare SQL Data Repository with analytics queries,
    vendor extracts, and data validation — mirroring HEALTHTECH DR workflows.
    """


@cli.command()
def setup():
    """Create the database schema and load sample patient data."""
    click.echo("Setting up HEALTHTECH DR demo database...")
    db.setup_database()
    click.secho("  Database created: healthtech_dr.db", fg="green")
    click.secho("  Schema:  patients, providers, encounters, lab_results, orders", fg="green")
    click.secho("  Seeded:  10 patients | 5 providers | 20 encounters | 30 labs | 25 orders", fg="green")
    click.echo("\nRun 'python cli.py query patient_census' to see census data.")


@cli.command()
@click.argument("name")
@click.option("--start", default=None, help="Start date YYYY-MM-DD (default: 1 year ago)")
@click.option("--end",   default=None, help="End date YYYY-MM-DD (default: today)")
def query(name: str, start: str, end: str):
    """Run a named analytics query and print results.

    NAME is the SQL filename without extension. Examples:

    \b
        patient_census
        lab_trends
        encounter_summary
    """
    if not db.DB_PATH.exists():
        click.secho("Database not found. Run 'python cli.py setup' first.", fg="red")
        sys.exit(1)

    start = _validate_date(start, "--start") or _default_dates()[0]
    end   = _validate_date(end,   "--end")   or _default_dates()[1]

    click.echo(f"\nQuery: {name}  |  {start} → {end}\n")
    try:
        columns, rows = db.run_named_query(name, {"start_date": start, "end_date": end})
    except (FileNotFoundError, ValueError) as e:
        click.secho(str(e), fg="red")
        sys.exit(1)

    _print_table(columns, rows)
    click.echo(f"\n  {len(rows)} row(s) returned.")


@cli.command()
@click.argument("name")
@click.option("--start",  default=None, help="Start date YYYY-MM-DD")
@click.option("--end",    default=None, help="End date YYYY-MM-DD")
@click.option("--output", default=None, help="Output CSV path (default: exports/<name>.csv)")
def extract(name: str, start: str, end: str, output: str):
    """Export a vendor extract query to CSV.

    NAME examples:

    \b
        billing_extract
        hl7_export
    """
    if not db.DB_PATH.exists():
        click.secho("Database not found. Run 'python cli.py setup' first.", fg="red")
        sys.exit(1)

    start = _validate_date(start, "--start") or _default_dates()[0]
    end   = _validate_date(end,   "--end")   or _default_dates()[1]
    out_path = Path(output) if output else Path("exports") / f"{name}.csv"

    try:
        count = db.export_to_csv(name, {"start_date": start, "end_date": end}, out_path)
    except (FileNotFoundError, ValueError) as e:
        click.secho(str(e), fg="red")
        sys.exit(1)

    click.secho(f"  Exported {count} rows to {out_path}", fg="green")


@cli.command()
def troubleshoot():
    """Run all data validation checks and report pass/fail status."""
    if not db.DB_PATH.exists():
        click.secho("Database not found. Run 'python cli.py setup' first.", fg="red")
        sys.exit(1)

    click.echo("\nRunning Data Repository validation checks...\n")

    columns, rows = db.run_named_query("data_validation", {})

    passed = 0
    failed = 0
    for row in rows:
        check_name, issue_count, description = row[0], int(row[1]), row[2]
        if issue_count == 0:
            click.secho(f"  PASS  {check_name}", fg="green")
            passed += 1
        else:
            click.secho(f"  FAIL  {check_name}  ({issue_count} issue(s))  — {description}", fg="red")
            failed += 1

    click.echo(f"\nResults: {passed} passed, {failed} failed out of {passed + failed} checks.")

    if failed:
        click.echo("\nTo investigate orphan records, run:")
        click.echo("  python cli.py query orphan_records")


@cli.command("list-queries")
def list_queries():
    """List all available named queries."""
    queries = db.list_queries()
    click.echo("\nAvailable queries:\n")
    for q in queries:
        click.echo(f"  {q}")
    click.echo()


if __name__ == "__main__":
    cli()
