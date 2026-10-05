# JMBSC Monthly Collection Report

This program turns the latest collection CSV export into a monthly bar chart.
It includes collection receipts for maintenance fees, sinking funds, fire
insurance, and late-payment interest.

## Daily Use Steps

1. Export the latest customer payment data as a CSV file from SQL Accounting ERP. Preferably name the exported file `collection.csv`.
2. Copy `collection.csv` file into this project folder. 
3. Open PowerShell (shift+right click) in this `jmbsc-collection-report` project folder.
4. Run:

   ```powershell
   uv run python main.py
   ```
5. The chart is saved as `monthly_collection.jpg` in the project folder.
6. Close the chart window when finished.

Note:
- If `collection.csv` is not present, the software automatically uses the only other CSV file in the folder. 
- Do not keep multiple CSV files in the project folder.


## First-Time Setup

These steps are only needed once on a Windows computer.

### 1. Install uv

Open PowerShell and install `uv` with Windows Package Manager:

```powershell
winget install --id=astral-sh.uv -e
```

Close and reopen PowerShell, then confirm that it is available:

```powershell
uv --version
```

Other official installation methods are available in the
[uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### 2. Create the project environment

Open PowerShell in this `jmbsc-collection-report` project folder.

Run this command from the project folder in PowerShell:

```powershell
uv sync --locked
```

This installs the Python version and package versions required by the project. After it finishes, follow the **Daily
Use** instructions above.












### What the daily report includes

- The 12 complete calendar months immediately before the current month.
- Receipts whose `Description 2` contains `MAINTENANCE FEE`, `SINKING FUND`,
  `FIRE INSURANCE`, `LATE PAYMENT INTEREST`, or the whole word `LPI`.
- The full `Doc Amount` of every matching receipt.
- Dates from `Doc Date` by default.

The current month is deliberately excluded because it is incomplete. A month
with no matching receipts is omitted from the chart instead of appearing as a
zero-value bar.

## Input CSV Requirements

Keep the column names from the original collection export. The program needs:

- `Doc Date`
- `Post Date` if that date option is selected
- `Doc Amount`
- `Description 2`

Immediately after opening the CSV, the software validates these headers. If
one or more are missing, it stops before processing any rows and prints the
CSV filename, headers actually found, missing headers, and instructions to
re-export the CSV with the complete list of required headings. An empty CSV
also produces a clear header-validation error with that required list.

Dates should use day/month/year format. Amounts may contain commas, such as
`1,500.00`. The export's final `Count = ...` summary row is ignored by the
current description filter.

Blank descriptions and descriptions that do not match the collection terms
are excluded. Review the terminal totals against the source report whenever a
new export format is introduced.

The software looks for `collection.csv` first. If it is missing and exactly one
other CSV file exists in the project root, that file is used automatically. If
several CSV files exist without `collection.csv`, the software stops, lists the
files, and asks you to delete the extras so that only one remains.

## Understanding the Generated Chart

The generated image contains two panels:

- The upper panel shows the collection total for each displayed month.
- The lower panel shows the **Average Monthly Collection**.

The average is calculated by adding the displayed monthly totals and dividing
the result by the number of displayed months. For example, monthly totals of
RM 5.00, RM 8.00, and RM 10.00 produce an average of **RM 7.67**.

Months without matching collection records are omitted and are not counted as
zero when calculating the average. If no months are displayed, the average
panel shows **RM 0.00**.

The small `Software by Armesh Singh` credit appears at the bottom-right of the
generated image.

## Changing the Report Settings

The user-editable settings are near the beginning of `main.py`:

- `INPUT_CSV` controls the input filename.
- `OUTPUT_IMAGE` controls the generated image filename.
- `DATE_COL` can be changed from `Doc Date` to `Post Date`.
- `PATTERN` controls which descriptions are included.
- `BAR_COLOR` controls the chart's bar colour.

Keep quoted text and punctuation intact when editing these settings.

## Common Problems

### `uv` is not recognized

Close and reopen PowerShell after installing `uv`. If it is still unavailable,
repeat the first-time installation or follow the official installation guide.

### `collection.csv` cannot be found

The software can use a differently named CSV when it is the only CSV file in
the project folder. If no CSV exists, copy the export into the folder. If the
software reports multiple CSV files, delete the old or unrelated files and
keep only the one that should be processed.

### A required column is missing

Read the header-validation error in PowerShell. It lists the headers found in
the selected CSV first, followed by the missing headers. It then asks you to
re-export the file from SQL Accounting ERP with the displayed required column
headings. If the source system changed those headings, the program must be
updated before using the new format.

### The current month is missing

This is expected. The report only includes completed months.

### The chart window does not open

Run the program from a normal Windows desktop session. The chart uses a native
Qt window and cannot be displayed in a headless session.
