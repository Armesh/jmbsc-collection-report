from pathlib import Path

import pandas as pd
import matplotlib

matplotlib.use('QtAgg')

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

INPUT_CSV = 'collection.csv'
OUTPUT_IMAGE = 'monthly_collection.jpg'

# Change this to 'Post Date' if needed
DATE_COL = 'Doc Date'

PATTERN = (
    r'(?i)MAINTENANCE FEE|'
    r'SINKING FUND|'
    r'FIRE INSURANCE|'
    r'LATE PAYMENT INTEREST|'
    r'\bLPI\b'
)

BAR_COLOR = (203 / 255, 33 / 255, 150 / 255)

CREDD= ''.join(chr(code) for code in (
    83, 111, 102, 116, 119, 97, 114, 101,
    32, 98, 121, 32,
    65, 114, 109, 101, 115, 104,
    32, 83, 105, 110, 103, 104
))

PROJECT_ROOT = Path(__file__).resolve().parent


def resolve_input_csv(project_root=PROJECT_ROOT):
    preferred_csv = project_root / INPUT_CSV
    if preferred_csv.is_file():
        return preferred_csv

    csv_files = sorted(
        (
            path
            for path in project_root.iterdir()
            if path.is_file() and path.suffix.lower() == '.csv'
        ),
        key=lambda path: path.name.casefold()
    )

    if len(csv_files) == 1:
        print(f'{INPUT_CSV} not found. Using: {csv_files[0].name}', flush=True)
        return csv_files[0]

    if not csv_files:
        raise SystemExit(
            f'No CSV file found in the project root: {project_root}'
        )

    csv_names = '\n'.join(f'- {path.name}' for path in csv_files)
    raise SystemExit(
        f'{INPUT_CSV} was not found and more than one CSV file exists in the '
        f'project root:\n{csv_names}\n\n'
        'Delete the extra CSV files so that only one CSV file remains, then '
        'run the software again.'
    )


def get_required_headers():
    return (DATE_COL, 'Doc Amount', 'Description 2')


def validate_csv_headers(df, input_csv):
    required_headers = get_required_headers()
    missing_headers = [
        header for header in required_headers if header not in df.columns
    ]

    if not missing_headers:
        return

    missing_list = '\n'.join(f'- {header}' for header in missing_headers)
    required_list = '\n'.join(f'- {header}' for header in required_headers)
    found_list = (
        '\n'.join(f'- {header}' for header in df.columns)
        if len(df.columns)
        else '- No headers found'
    )

    raise SystemExit(
        f'ERROR: CSV header validation failed for "{input_csv.name}".\n\n'
        f'Header(s) found:\n{found_list}\n\n'
        f'Missing required header(s):\n{missing_list}\n\n'
        'Re-export the CSV from SQL Accounting ERP with the following '
        f'required column headings:\n{required_list}\n\n'
        'Then run the software again.'
    )


def load_csv(input_csv):
    try:
        df = pd.read_csv(input_csv, dtype=str)
    except pd.errors.EmptyDataError:
        required_list = '\n'.join(
            f'- {header}' for header in get_required_headers()
        )
        raise SystemExit(
            f'ERROR: CSV header validation failed for "{input_csv.name}".\n\n'
            'The file is empty or does not contain a header row.\n\n'
            'Re-export the CSV from SQL Accounting ERP with the following '
            f'required column headings:\n{required_list}\n\n'
            'Then run the software again.'
        ) from None

    validate_csv_headers(df, input_csv)
    return df


def rm_axis_formatter(value, _):
    return f'RM {value:,.0f}'


def rm_label(value):
    return f'RM {value:,.2f}'


def main():
    # Load CSV
    input_csv = resolve_input_csv()
    print(f'Input CSV: {input_csv.name}', flush=True)
    df = load_csv(input_csv)

    # Same filtering logic as Splunk
    match_mask = (
        df['Description 2']
        .fillna('')
        .str.contains(PATTERN, regex=True, na=False)
    )

    # Print records that do NOT match PATTERN
    unmatched = df.loc[~match_mask]

    if not unmatched.empty:
        print('\nDescriptions NOT matching PATTERN:')
        for _, row in unmatched.iterrows():
            print(f"{row.iloc[1]} | {row['Description 2']}")

    # Keep only matching records for the chart
    df = df.loc[match_mask].copy()

    # Parse dates
    df[DATE_COL] = pd.to_datetime(
        df[DATE_COL],
        dayfirst=True,
        errors='coerce'
    )

    # Date filter:
    # from first day of the month 12 months ago
    # to last day of previous month
    today = pd.Timestamp.today().normalize()
    first_day_current_month = today.replace(day=1)

    start_date = first_day_current_month - pd.DateOffset(months=12)
    end_date = first_day_current_month - pd.Timedelta(days=1)

    df = df[
        (df[DATE_COL] >= start_date) &
        (df[DATE_COL] <= end_date)
    ].copy()

    print(f'Date filter: {start_date.date()} to {end_date.date()}')

    # Parse amount
    df['Doc Amount'] = pd.to_numeric(
        df['Doc Amount']
        .fillna('0')
        .str.replace(',', '', regex=False)
        .str.strip(),
        errors='coerce'
    ).fillna(0)

    # Drop invalid dates
    df = df.dropna(subset=[DATE_COL])

    # Group by month
    df['_time'] = df[DATE_COL].dt.to_period('M').dt.to_timestamp()

    monthly = (
        df.groupby('_time', as_index=False)['Doc Amount']
        .sum()
        .rename(columns={'Doc Amount': 'Total'})
        .sort_values('_time')
    )

    monthly['Month'] = monthly['_time'].dt.strftime('%b %Y')
    average_monthly = monthly['Total'].mean() if not monthly.empty else 0

    print(monthly[['Month', 'Total']].to_string(index=False))

    # Create figure
    fig, (ax, average_ax) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        gridspec_kw={
            'height_ratios': (7, 1.4),
            'hspace': 0.25
        }
    )

    # Black background
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    average_ax.set_facecolor('black')

    # Bar chart
    bars = ax.bar(
        monthly['Month'],
        monthly['Total'],
        color=BAR_COLOR,
        width=0.65
    )

    # Title and labels
    ax.set_title(
        'Monthly Collection',
        color='white',
        fontsize=18,
        fontweight='bold',
        pad=16
    )

    ax.set_xlabel('')
    ax.set_ylabel('Collection (RM)', color='white', fontsize=11)

    # Axis colors
    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')

    # Spines
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Y-axis format
    ax.yaxis.set_major_formatter(FuncFormatter(rm_axis_formatter))

    # Grid
    ax.grid(axis='y', color='white', alpha=0.15, linestyle='--')
    ax.grid(axis='x', visible=False)

    # Value labels on bars
    ax.bar_label(
        bars,
        labels=[rm_label(v) for v in monthly['Total']],
        padding=4,
        color='white',
        fontsize=9,
        fontweight='bold'
    )

    # Average monthly collection panel
    average_ax.set_xticks([])
    average_ax.set_yticks([])

    for spine in average_ax.spines.values():
        spine.set_color(BAR_COLOR)
        spine.set_linewidth(1.5)

    average_ax.text(
        0.5,
        0.68,
        'Average Monthly Collection',
        transform=average_ax.transAxes,
        ha='center',
        va='center',
        color='white',
        fontsize=10,
        fontweight='bold'
    )

    average_ax.text(
        0.5,
        0.28,
        rm_label(average_monthly),
        transform=average_ax.transAxes,
        ha='center',
        va='center',
        color=BAR_COLOR,
        fontsize=20,
        fontweight='bold'
    )

    fig.subplots_adjust(
        left=0.09,
        right=0.98,
        top=0.93,
        bottom=0.035
    )

    fig.text(
        0.995,
        0.005,
        CREDD,
        ha='right',
        va='bottom',
        color='#8a8a8a',
        fontsize=7
    )

    # Save as JPG
    plt.savefig(
        OUTPUT_IMAGE,
        format='jpg',
        dpi=200,
        bbox_inches='tight',
        facecolor=fig.get_facecolor()
    )

    print(f'\nChart saved as: {OUTPUT_IMAGE}')
    print(f'Matplotlib backend: {matplotlib.get_backend()}')

    # Show native GUI window
    plt.show()


if __name__ == '__main__':
    main()
