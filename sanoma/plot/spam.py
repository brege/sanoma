#!/usr/bin/env python3
"""
Spam trends plotting tool for sanoma
Creates visualizations showing spam keyword frequency over time
"""

import argparse
from pathlib import Path

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def create_spam_timeline(
    monthly_data, output_file, title="Spam Trends", display_method="save"
):
    """Create timeline plot showing spam percentage over time"""
    if monthly_data.empty:
        print("No monthly data found")
        return

    # Prepare data for plotting
    monthly_data = monthly_data.copy()
    monthly_data["period_date"] = pd.to_datetime(
        monthly_data["month"], format="%Y-%m", errors="coerce"
    )
    monthly_data = monthly_data.dropna(subset=["period_date"])
    monthly_data = monthly_data[monthly_data["total_emails"] > 5]

    if monthly_data.empty:
        print("No valid date data found")
        return
    monthly_data = monthly_data.sort_values("period_date")

    dates = monthly_data["period_date"].tolist()
    percentages = monthly_data["spam_percentage"].tolist()
    total_counts = monthly_data["total_emails"].tolist()
    spam_counts = monthly_data["spam_emails"].tolist()
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Top plot: Spam percentage over time
    ax1.plot(dates, percentages, linewidth=2, color="red", alpha=0.8)
    ax1.fill_between(dates, percentages, alpha=0.3, color="red")
    ax1.set_title(f"{title} - Spam Percentage Over Time", fontsize=14, pad=15)
    ax1.set_ylabel("Spam Percentage (%)", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # Bottom plot: Total email volume
    ax2.bar(
        dates,
        total_counts,
        alpha=0.6,
        color="steelblue",
        width=20,
        label="Total Emails",
    )
    ax2.bar(dates, spam_counts, alpha=0.8, color="red", width=20, label="Spam Emails")
    ax2.set_title("Email Volume (Total vs Spam)", fontsize=14, pad=15)
    ax2.set_xlabel("Date", fontsize=12)
    ax2.set_ylabel("Email Count", fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis="y")
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # Format x-axis
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()

    # Handle display method
    if display_method in ["save", "both"]:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Spam timeline saved to {output_file}")

    if display_method in ["show", "both"]:
        plt.show()
    else:
        plt.close()


def create_keyword_breakdown(
    keyword_data, output_file, title="Spam Keywords", display_method="save"
):
    """Create bar chart showing most common spam keywords"""
    if keyword_data.empty:
        print("No keyword data found")
        return

    keyword_totals = (
        keyword_data.groupby("keyword")["count"].sum().sort_values(ascending=False)
    )
    keywords = keyword_totals.head(10).index.tolist()
    counts = keyword_totals.head(10).tolist()

    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.bar(keywords, counts, color="orange", alpha=0.7)
    ax.set_title(f"{title} - Most Common Spam Keywords", fontsize=14, pad=15)
    ax.set_xlabel("Keyword Pattern", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.grid(True, alpha=0.3, axis="y")

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{int(height)}",
            ha="center",
            va="bottom",
        )

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Handle display method
    if display_method in ["save", "both"]:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Keyword breakdown saved to {output_file}")

    if display_method in ["show", "both"]:
        plt.show()
    else:
        plt.close()


def create_yearly_heatmap(
    yearly_data, keyword_data, output_file, title="Spam Trends", display_method="save"
):
    """Create heatmap showing spam percentage by year and keyword"""
    if yearly_data.empty:
        print("No yearly data found")
        return

    filtered_years = yearly_data[yearly_data["year"] >= 2010]
    keyword_data = keyword_data[
        (keyword_data["year"] >= 2010) & (keyword_data["keyword"] != "unsubscribe_bait")
    ]

    if keyword_data.empty:
        print("No keyword data for heatmap")
        return

    # Create matrix
    keywords_list = sorted(keyword_data["keyword"].unique().tolist())
    years_list = sorted(filtered_years["year"].unique().tolist())

    matrix = []
    for keyword in keywords_list:
        row = []
        keyword_rows = keyword_data[keyword_data["keyword"] == keyword]
        for year in years_list:
            year_data = keyword_rows[keyword_rows["year"] == year]
            total_emails = int(
                filtered_years.loc[filtered_years["year"] == year, "total_emails"].iloc[
                    0
                ]
            )
            keyword_count = (
                int(year_data["count"].iloc[0]) if not year_data.empty else 0
            )
            percentage = (keyword_count / total_emails * 100) if total_emails > 0 else 0
            row.append(percentage)
        matrix.append(row)

    # Create heatmap
    fig, ax = plt.subplots(figsize=(12, 8))

    im = ax.imshow(matrix, cmap="Reds", aspect="auto")

    # Set ticks and labels
    ax.set_xticks(range(len(years_list)))
    ax.set_yticks(range(len(keywords_list)))
    ax.set_xticklabels(years_list)
    ax.set_yticklabels(keywords_list)

    # Rotate x-axis labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # Add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label("Spam Percentage (%)", rotation=270, labelpad=15)

    ax.set_title(f"{title} - Spam Keywords by Year (Heatmap)", fontsize=14, pad=15)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Keyword Pattern", fontsize=12)

    plt.tight_layout()

    # Handle display method
    if display_method in ["save", "both"]:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Spam heatmap saved to {output_file}")

    if display_method in ["show", "both"]:
        plt.show()
    else:
        plt.close()


def main():
    parser = argparse.ArgumentParser(description="Generate spam trend visualizations")
    parser.add_argument("input_file", help="Input spam analysis data (JSON)")
    parser.add_argument(
        "--plot-type",
        choices=["timeline", "keywords", "heatmap", "all"],
        default="all",
        help="Type of plot to generate",
    )
    parser.add_argument(
        "--output-dir", default="data/plots", help="Output directory for plots"
    )
    parser.add_argument("--title", default="Spam Analysis", help="Title for the plots")
    parser.add_argument(
        "--display",
        choices=["show", "save", "both"],
        default="save",
        help="How to handle plots",
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load spam analysis data
    with open(args.input_file, "r") as f:
        spam_data = json.load(f)

    if "by_month" not in spam_data or "by_year" not in spam_data:
        raise ValueError("Missing required sections in analysis JSON")

    monthly_data = (
        pd.DataFrame.from_dict(spam_data["by_month"], orient="index")
        .reset_index()
        .rename(columns={"index": "month"})
    )
    yearly_data = (
        pd.DataFrame.from_dict(spam_data["by_year"], orient="index")
        .reset_index()
        .rename(columns={"index": "year"})
    )
    yearly_data["year"] = pd.to_numeric(yearly_data["year"], errors="coerce")
    yearly_data = yearly_data.dropna(subset=["year"])
    yearly_data["year"] = yearly_data["year"].astype(int)

    keyword_data = (
        yearly_data[["year", "keyword_matches"]]
        .set_index("year")["keyword_matches"]
        .apply(pd.Series)
        .stack()
        .reset_index()
        .rename(columns={"level_0": "year", "level_1": "keyword", 0: "count"})
    )
    keyword_data["count"] = pd.to_numeric(
        keyword_data["count"], errors="coerce"
    ).fillna(0)

    print("Generating spam trend plots...")

    # Generate plots based on type
    if args.plot_type in ["timeline", "all"]:
        timeline_file = output_dir / "timeline.png"
        create_spam_timeline(monthly_data, timeline_file, args.title, args.display)

    if args.plot_type in ["keywords", "all"]:
        keywords_file = output_dir / "keywords.png"
        create_keyword_breakdown(keyword_data, keywords_file, args.title, args.display)

    if args.plot_type in ["heatmap", "all"]:
        heatmap_file = output_dir / "heatmap.png"
        create_yearly_heatmap(
            yearly_data, keyword_data, heatmap_file, args.title, args.display
        )


if __name__ == "__main__":
    main()
