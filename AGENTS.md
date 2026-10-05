# Project Guidance

## Scope

These instructions apply to the entire `jmbsc-collection-report` project.

`main.py` is the single source of application logic. `collection.csv` is the
input artifact, and `monthly_collection.jpg` is generated output.

You are not allowed to modify README.md contents before line 70.
Only change README.md pass after line 70 onwards. 

## Current Report Logic

- Keep user-editable settings near the beginning of `main.py`. The current
  settings are `INPUT_CSV`, `OUTPUT_IMAGE`, `DATE_COL`, `PATTERN`, and
  `BAR_COLOR`.
- Resolve input files from the project root. Prefer `collection.csv`; if it is
  missing, use the only root-level CSV. If no CSV exists, stop clearly. If
  several fallback CSV files exist, list them and tell the user to delete the
  extras so that only one remains.
- Read the CSV as strings before parsing individual fields.
- Immediately validate that the selected CSV contains `DATE_COL`,
  `Doc Amount`, and `Description 2`. On failure, stop without a traceback and
  clearly show the filename, found headers first, missing headers second, and
  instructions to re-export from SQL Accounting ERP with the full
  required-header list.
  Treat an empty file as a header-validation failure with the same required
  list in its clear shell message.
- Include a receipt when `Description 2` contains at least one of these terms,
  case-insensitively: `MAINTENANCE FEE`, `SINKING FUND`, `FIRE INSURANCE`,
  `LATE PAYMENT INTEREST`, or the whole word `LPI`.
- Use `DATE_COL` for reporting dates. It defaults to `Doc Date`; `Post Date` is
  the supported alternative.
- Report the 12 complete calendar months immediately before the current month.
  The current, incomplete month is excluded.
- Parse `Doc Amount` after removing thousands separators, group matching rows
  by calendar month, and sum the entire receipt amount.
- Calculate average monthly collection as the mean of the grouped monthly
  totals actually displayed in the chart. If no months are displayed, use
  `RM 0.00`.
- Produce a two-panel black-background figure: a monthly bar chart with
  magenta bars, RM-formatted axes, and value labels on top, plus a bordered KPI
  panel showing `Average Monthly Collection` below. Keep compact vertical
  spacing between the panels while leaving room for rotated month labels. Use
  compact panel typography: size 10 for the label and size 20 for its RM value.
  Add the small credit `Software by Armesh Singh` at the extreme bottom-right
  of the figure, immediately below the average panel without a large blank
  area. Save it as a JPEG, then show it with the Qt GUI.

## Data Caveats

- The exported CSV currently has an extra unnamed document-number column: the
  `Doc No` column contains `+`, while the receipt number is in the unnamed
  column. The report does not currently use either column.
- The CSV ends with a `Count = ...` summary row. Do not accidentally include
  that row as a receipt or add its amount to transaction totals.
- Blank or non-matching `Description 2` values are intentionally excluded by
  the current filter. Review them explicitly before changing that behavior.
- Months without matching rows are currently omitted from the grouped result
  and chart; they are not automatically displayed as zero-value months and do
  not contribute zeroes to the displayed-month average.
- Exact row counts, totals, dates, and chart values depend on the current CSV.
  Recompute them instead of copying historical figures from this file.

## Change Rules

- Read `AGENTS.md` and the current `main.py` before modifying report behavior.
- When project logic or code changes, update this file in the same change so
  that `Current Report Logic`, caveats, inputs, outputs, and execution behavior
  remain accurate.
- Preserve the existing input and output filenames unless the user requests a
  change.
- Do not run `main.py` after editing unless the user explicitly asks. Running
  it overwrites `monthly_collection.jpg` and opens a native Qt window.
- Read-only inspection and validation are allowed. Use the existing virtual
  environment when practical; do not add or update dependencies unless the
  task requires it and the user authorizes it.
- Validate changes against the actual CSV structure and report any excluded,
  invalid, or ambiguous rows plainly.
- Do not commit changes unless the user explicitly asks.

## Project State

- Python version: 3.14 (`.python-version`).
- Dependencies are managed in `pyproject.toml` and `uv.lock`.
- Runtime libraries: pandas, Matplotlib, and PyQt6. Seaborn is listed but is
  not currently imported by `main.py`.
- `README.md` contains the Windows first-time setup, daily operating workflow,
  input requirements, generated-chart explanation, configurable settings, and
  common troubleshooting steps.
