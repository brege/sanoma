#!/usr/bin/env python3
"""
Temporal plotting tool for sanoma analysis results
"""

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def create_year_over_year_histogram(
    emails, output_file, title="Email Volume", display_method="save"
):
    """Create year-over-year stacked histogram by month"""
    # Parse dates and create month-year data
    parsed_emails = emails.dropna(subset=["date_parsed"])
    if parsed_emails.empty:
        print("No valid dates found in dataset")
        return

    counts = (
        parsed_emails.assign(
            year=parsed_emails["date_parsed"].dt.year,
            month_name=parsed_emails["date_parsed"].dt.strftime("%b"),
        )
        .groupby(["year", "month_name"])
        .size()
        .reset_index(name="count")
    )

    # Create pivot table for stacked histogram
    pivot_df = counts.pivot_table(
        index="month_name", columns="year", values="count", fill_value=0
    )

    # Reorder months correctly
    month_order = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    pivot_df = pivot_df.reindex(month_order)

    # Create the stacked bar chart
    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot stacked bars
    pivot_df.plot(kind="bar", stacked=True, ax=ax, colormap="tab20", width=0.8)

    ax.set_title(f"{title} - Year over Year by Month", fontsize=16, pad=20)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Email Count", fontsize=12)
    ax.legend(title="Year", bbox_to_anchor=(1.05, 1), loc="upper left")

    # Rotate x-axis labels
    plt.xticks(rotation=0)

    # Add grid for better readability
    ax.grid(True, alpha=0.3, axis="y")

    # Tight layout to prevent legend cutoff
    plt.tight_layout()

    # Handle display method
    if display_method in ["save", "both"]:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Year-over-year histogram saved to {output_file}")

    if display_method in ["show", "both"]:
        plt.show()
    else:
        # Close figure if not displaying
        plt.close()

    # Show summary stats
    total_by_year = pivot_df.sum(axis=0).sort_index()
    print("\nEmail volume by year:")
    for year, count in total_by_year.items():
        print(f"  {year}: {count:,} emails")


def create_simple_timeline(
    emails, output_file, title="Email Timeline", display_method="save"
):
    """Create a simple timeline plot of email volume over time"""
    parsed_emails = emails.dropna(subset=["date_parsed"])
    if parsed_emails.empty:
        print("No valid dates found in dataset")
        return

    month_counts = (
        parsed_emails.groupby(parsed_emails["date_parsed"].dt.to_period("M"))
        .size()
        .sort_index()
    )
    dates = [period.to_timestamp() for period in month_counts.index]
    counts = month_counts.values

    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(dates, counts, linewidth=2, color="steelblue")
    ax.fill_between(dates, counts, alpha=0.3, color="steelblue")

    ax.set_title(f"{title} - Timeline", fontsize=16, pad=20)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Emails per Month", fontsize=12)

    # Format x-axis
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())

    # Rotate labels if needed
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    # Add grid
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Handle display method
    if display_method in ["save", "both"]:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Timeline plot saved to {output_file}")

    if display_method in ["show", "both"]:
        plt.show()
    else:
        # Close figure if not displaying
        plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Generate temporal plots from email datasets"
    )
    parser.add_argument("input_file", help="Input dataset file (JSON)")
    parser.add_argument(
        "--plot-type",
        choices=["histogram", "timeline", "both"],
        default="histogram",
        help="Type of plot to generate",
    )
    parser.add_argument(
        "--output-dir", default="data/plots", help="Output directory for plots"
    )
    parser.add_argument("--title", default="Email Volume", help="Title for the plots")
    parser.add_argument(
        "--filter-domain", help="Filter emails by recipient domain (e.g., wsu.edu)"
    )
    parser.add_argument(
        "--display",
        choices=["show", "save", "both"],
        default="save",
        help="How to handle the plot (default: save)",
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Load emails
    emails = pd.read_json(args.input_file)
    required_columns = {"date", "to"}
    missing_columns = required_columns.difference(emails.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns in JSON: {', '.join(sorted(missing_columns))}"
        )
    date_series = pd.to_datetime(
        emails["date"].astype(str).str.slice(0, 19),
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce",
    )
    emails = emails.assign(date_parsed=date_series)

    # Filter by domain if specified
    if args.filter_domain:
        to_lower = emails["to"].astype(str).str.lower()
        emails = emails[to_lower.str.contains(args.filter_domain.lower(), na=False)]
        print(
            f"Filtered to {len(emails.index)} emails with recipient domain "
            f"'{args.filter_domain}'"
        )

    if emails.empty:
        print("No emails to plot after filtering")
        return

    # Generate plots
    if args.plot_type in ["histogram", "both"]:
        histogram_file = output_dir / "histogram.png"
        create_year_over_year_histogram(
            emails, histogram_file, args.title, args.display
        )

    if args.plot_type in ["timeline", "both"]:
        timeline_file = output_dir / "timeline.png"
        create_simple_timeline(emails, timeline_file, args.title, args.display)


if __name__ == "__main__":
    main()
