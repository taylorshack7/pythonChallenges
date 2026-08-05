# Tech Service Dependency Analyzer

A Python + SQLite project that models a network of technical services, analyzes their dependency graph, and persists every analysis run to a relational database for historical reporting.

Given a set of services (each with its dependencies and past incident-resolution times), the tool lets you pick a starting service, runs eight graph and risk analyses against it, prints the results, and records both the run and its results in a normalized SQLite database.

---

## What It Does

From a chosen start service, the analyzer computes:

| Analysis | Description |
|---|---|
| **Depth First Search Order** | Order services are reached exploring each dependency chain to its end first |
| **Breadth First Search Order** | Order services are reached exploring level by level |
| **Number of Reachable Services** | Count of services reachable from the start |
| **Dependency Levels** | Minimum number of dependency hops to reach each service |
| **Shortest Path** | Shortest dependency path from the start to every reachable service |
| **Average Incident Times** | Mean incident-resolution time per reachable service |
| **Total Incident Times** | Combined incident time across all reachable services |
| **Highest Risk Service** | Service maximizing `(number of dependents) × (average incident time)` — blast radius times fragility |

Every run is timestamped and saved, so the database builds a history of analyses over time.

---

## Project Structure

| File | Purpose |
|---|---|
| `TechServiceDependencyAnalyzer_v2.py` | Main program: analysis logic + the console workflow that computes results and orchestrates persistence |
| `db.py` | Database layer: table creation and all inserts, split into three classes |
| `DependencyDictionary.py` | Single source of truth for the service data (the input dictionary) |
| `capstone.db` | The SQLite database (generated/updated on each run) |
| `vw_ServiceAnalysisResults.sql` | Saved reporting queries for the relational database |
| `Drawing 52.vsdx` | Entity Relationship Diagram (ERD) of the database schema |
| `sqlite3.exe` | Bundled SQLite command-line tool for querying the database |

---

## Architecture

The project is layered so each piece has one job and dependencies flow in one direction:

```
DependencyDictionary.py   (data: the source service dictionary)
          |
          v
TechServiceDependencyAnalyzer_v2.py   (compute: runs analyses, returns a results dict; orchestrates the run)
          |
          v
db.py   (persistence: knows how to write to SQLite, nothing about graph algorithms)
```

- **`analyze_services()`** stays pure: it validates input, computes the eight analyses, and **returns a dictionary** of results. It does not touch the database.
- **The console block** at the bottom of the analyzer is the orchestrator. It reads the user's choice, calls `analyze_services()`, then hands the results to `db.py` to persist.
- **`db.py`** receives its data as arguments (the service dictionary, the results dictionary). It never imports the analyzer, which keeps the import graph one-directional and avoids circular imports.

### The three database classes in `db.py`

- **`DatabaseInitializer`** — creates the five tables (`CREATE TABLE IF NOT EXISTS`).
- **`ServicesToSQL`** — seeds the reference data: services, dependencies, and incident times.
- **`AnalyzerToSQL`** — records each analysis run and its results.

---

## Database Schema

Five tables. See `Drawing 52.vsdx` for the visual ERD.

**Services** — the master list of services.
- `ID` (PK), `Name` (`UNIQUE NOT NULL`)

**ServiceDependencies** — which service depends on which (a self-referencing relationship; both columns point back to `Services`).
- `ID` (PK), `ServiceID` (FK → Services), `DependsOnServiceID` (FK → Services)
- `UNIQUE (ServiceID, DependsOnServiceID)` prevents duplicate dependency pairs

**IncidentTimes** — incident-resolution durations per service.
- `ID` (PK), `ServiceID` (FK → Services), `IncidentTime`

**ServiceAnalyzerRuns** — one row per analysis execution (an immutable event).
- `ID` (PK), `StartServiceId` (FK → Services), `DateCreated`

**ServiceAnalyzerResults** — one row per analysis output, tied to a run.
- `ID` (PK), `AnalysisRunId` (FK → ServiceAnalyzerRuns), `AnalysisType`, `Result`
- `UNIQUE (AnalysisRunId, AnalysisType)` prevents duplicate analysis types within a run
- `Result` stores JSON-serialized values (lists, dicts, numbers) so any analysis output fits one text column

### Key design decisions

- **Foreign keys are enforced.** `PRAGMA foreign_keys = ON` is set on every connection, since SQLite does not enforce foreign keys by default.
- **Invariants live in the schema, not just in code.** Uniqueness and referential integrity are enforced by constraints, so the database itself refuses bad data regardless of what the application does.
- **Two table philosophies:**
  - *Reference data* (`Services`, `ServiceDependencies`, `IncidentTimes`) is kept in sync with the source on each run — services and dependencies use `INSERT OR IGNORE` (insert-if-new), and incident rows are rebuilt (deleted and re-inserted).
  - *Event data* (`ServiceAnalyzerRuns`, `ServiceAnalyzerResults`) is append-only. Each run is a permanent historical record and is never rewritten.
- **Parent/child linkage** uses the inserted run's `lastrowid` so each result row references the run that produced it.
- **Re-run safe.** The program can be run repeatedly against the same database without duplicating reference data or crashing on unique constraints; each run adds a fresh set of results.

---

## How to Run

Requires Python 3 (standard library only — `sqlite3` and `json` are built in).

```bash
python TechServiceDependencyAnalyzer_v2.py
```

You will be prompted to choose a start service by number or name. The program then:
1. Runs the eight analyses and prints the results.
2. Creates the database tables if they do not exist.
3. Seeds the reference tables (services, dependencies, incidents).
4. Records the run and its results.
5. Prints confirmation.

The database is written to `capstone.db` in the project folder (the path is derived from the script location, so it works regardless of the current working directory).

---

## Querying the Database

Open `capstone.db` in **DB Browser for SQLite** (GUI) or the bundled command-line tool:

```bash
.\sqlite3 capstone.db
```

Saved reporting queries are in `vw_ServiceAnalysisResults.sql`, including:

- **Run results report** — joins `Services`, `ServiceAnalyzerRuns`, and `ServiceAnalyzerResults` to show, per run, the start service and every analysis output.
- **Dependency map** — a self-join on `Services` that resolves both `ServiceID` and `DependsOnServiceID` into readable service names.

Example — the dependency map with names instead of IDs:

```sql
SELECT B.Name AS ServiceName, C.Name AS DependsName
FROM ServiceDependencies A
JOIN Services B ON A.ServiceID = B.ID
JOIN Services C ON A.DependsOnServiceID = C.ID;
```

---

## Possible Future Enhancements

- **Multi-source ingestion** with real incident occurrence timestamps, enabling a true append-only incident history and retrospective without re-seeding.
- **Full dependency sync** (remove dependencies that no longer exist in the source, not just add new ones).
- **A single shared database connection** passed to all three classes, simplifying commit ordering and cross-connection visibility.
- **Saved SQL views** (`CREATE VIEW`) for the reporting queries so they can be queried like tables.
