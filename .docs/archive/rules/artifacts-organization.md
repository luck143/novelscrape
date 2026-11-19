# Artifacts Organization Rule

## Purpose

This rule establishes the standard location and structure for all reports, logs, and plan files generated during project work to prevent pollution of the project directory.

## Rule Statement

**All reports, logs, and plan files MUST be created in the `.kilocode/artifacts/` directory with proper subdirectories.**

## Directory Structure

```
.kilocode/
└── artifacts/
    ├── logs/           # Runtime logs, execution logs, debug logs
    ├── reports/        # Test reports, analysis reports, status reports
    └── plans/          # Project plans, implementation plans, design docs
```

## File Placement Guidelines

### Logs Directory (`.kilocode/artifacts/logs/`)

**Purpose:** Runtime logs, execution logs, debug logs, and any output from command execution.

**Examples:**
- `scraper_execution_2026-01-01.log`
- `test_results_2026-01-01.log`
- `debug_output.log`
- `error_log.txt`

**When to use:**
- Any log files generated during script execution
- Test output logs
- Debug information dumps
- Error logs

### Reports Directory (`.kilocode/artifacts/reports/`)

**Purpose:** Test reports, analysis reports, status reports, and summary documents.

**Examples:**
- `test_report_2026-01-01.md`
- `scraper_analysis.md`
- `status_summary.md`
- `performance_report.md`

**When to use:**
- Test results and summaries
- Analysis of code or systems
- Status reports on tasks
- Performance benchmarks
- Any report-style documentation

### Plans Directory (`.kilocode/artifacts/plans/`)

**Purpose:** Project plans, implementation plans, design documents, and strategic documents.

**Examples:**
- `implementation_plan.md`
- `feature_design.md`
- `architecture_plan.md`
- `roadmap.md`

**When to use:**
- Implementation plans for features
- Design documents
- Architecture plans
- Roadmaps and timelines
- Strategic planning documents

## Naming Conventions

### Date-Based Naming
For files that are time-sensitive or generated periodically:
- Format: `{name}_{YYYY-MM-DD}.{ext}`
- Example: `test_report_2026-01-01.md`

### Descriptive Naming
For static or reference documents:
- Format: `{descriptive_name}.{ext}`
- Example: `scraper_analysis.md`

### Log Naming
For log files with timestamps:
- Format: `{name}_{YYYY-MM-DD_HH-MM-SS}.{ext}`
- Example: `scraper_execution_2026-01-01_15-30-00.log`

## What NOT to Put in Project Root

**DO NOT create these files in the project root:**
- `test_report.txt`
- `execution.log`
- `plan.md`
- `analysis.md`
- `debug.log`
- `summary.txt`
- Any temporary or generated files

**These files MUST go in `.kilocode/artifacts/` instead.**

## Exceptions

**User-facing documentation** may remain in project root for easy access:
- `README.md` - Main project documentation for GitHub
- `usage.md` - User guide and command examples (also in `.kilocode/docs/usage.txt`)
- Other user-facing documentation files as needed

## Examples

### Correct Usage

```python
# Correct: Log file in artifacts/logs
log_path = '.kilocode/artifacts/logs/scraper_execution.log'
with open(log_path, 'w') as f:
    f.write(log_content)

# Correct: Report file in artifacts/reports
report_path = '.kilocode/artifacts/reports/test_report.md'
with open(report_path, 'w') as f:
    f.write(report_content)

# Correct: Plan file in artifacts/plans
plan_path = '.kilocode/artifacts/plans/implementation_plan.md'
with open(plan_path, 'w') as f:
    f.write(plan_content)
```

### Incorrect Usage

```python
# Incorrect: Log file in project root
log_path = 'execution.log'  # ❌ WRONG

# Incorrect: Report file in project root
report_path = 'test_report.md'  # ❌ WRONG

# Incorrect: Plan file in project root
plan_path = 'plan.md'  # ❌ WRONG
```

## Command Execution

When using `execute_command` tool, redirect output to artifacts directories:

```python
# Correct: Redirect to logs directory
execute_command(
    command='python test_script.py > .kilocode/artifacts/logs/test_output.log 2>&1',
    cwd='d:/pypro/novelscrape'
)
```

## File Creation

When creating any report, log, or plan file:

1. **Determine the type:** Log, Report, or Plan
2. **Choose the subdirectory:** `logs/`, `reports/`, or `plans/`
3. **Use descriptive naming:** Follow naming conventions
4. **Create in artifacts:** Full path should be `.kilocode/artifacts/{type}/{filename}`

## Enforcement

This rule is **mandatory** and must be followed for all file creation operations:

- Reports → `.kilocode/artifacts/reports/`
- Logs → `.kilocode/artifacts/logs/`
- Plans → `.kilocode/artifacts/plans/`

**Exceptions:** User-facing documentation (like `usage.txt`) may remain in project root for easy access. Any reports, logs, or plans found in the project root should be moved to the appropriate artifacts subdirectory.

## Benefits

1. **Clean Project Directory:** Keeps the main project directory focused on source code
2. **Easy Cleanup:** Artifacts can be easily identified and cleaned up
3. **Organized History:** All generated files are in one place with proper categorization
4. **Git-Friendly:** Artifacts can be `.gitignore`'d or selectively committed
5. **Clear Separation:** Distinguishes between source code and generated content

## Related Rules

- See `.kilocode/rules/memory-bank/` for project documentation rules
- See `.gitignore` for files that should not be committed to version control
