#!/usr/bin/env python3
"""
Temporal analysis tool using the sanoma CLI API and lib output adapters
"""

import argparse
from typing import cast

import pandas as pd

from sanoma.lib.output import write_data  # noqa: E402


AnalysisRow = dict[str, int | float | str]
SummaryAnalysis = dict[str, object]


def build_group_stats(grouped):
    """Build totals and with_body counts from grouped rows"""
    totals = grouped.size()
    with_body = grouped["has_body_bool"].sum()
    return totals, with_body


def analyze_by_year(emails):
    """Analyze email patterns by year"""
    grouped = emails.groupby(emails["date_parsed"].dt.year)
    totals, with_body = build_group_stats(grouped)
    return {
        int(year): {"total": int(totals[year]), "with_body": int(with_body[year])}
        for year in totals.index
    }


def analyze_by_month(emails, year=None):
    """Analyze email patterns by month (optionally for specific year)"""
    filtered = emails
    if year is not None:
        filtered = filtered[filtered["date_parsed"].dt.year == year]
    month_key = filtered["date_parsed"].dt.strftime("%Y-%m")
    grouped = filtered.groupby(month_key)
    totals, with_body = build_group_stats(grouped)
    return {
        str(month): {"total": int(totals[month]), "with_body": int(with_body[month])}
        for month in totals.index
    }


def analyze_by_weekday(emails):
    """Analyze email patterns by day of week"""
    weekday_series = emails["date_parsed"].dt.day_name()
    grouped = emails.groupby(weekday_series)
    totals, with_body = build_group_stats(grouped)
    return {
        str(day): {"total": int(totals[day]), "with_body": int(with_body[day])}
        for day in totals.index
    }


def analyze_by_hour(emails):
    """Analyze email patterns by hour of day"""
    grouped = emails.groupby(emails["date_parsed"].dt.hour)
    totals, with_body = build_group_stats(grouped)
    return {
        int(hour): {"total": int(totals[hour]), "with_body": int(with_body[hour])}
        for hour in totals.index
    }


def get_date_range(emails):
    """Get the date range of the dataset"""
    if emails.empty:
        return None, None
    return emails["date_parsed"].min(), emails["date_parsed"].max()


def main():
    parser = argparse.ArgumentParser(description="Temporal analysis for email datasets")
    parser.add_argument("input_file", help="Input dataset file")
    parser.add_argument(
        "--analysis",
        choices=["year", "month", "weekday", "hour", "summary"],
        default="summary",
        help="Type of temporal analysis (default: summary)",
    )
    parser.add_argument("--year", type=int, help="Specific year for monthly analysis")
    parser.add_argument("--output", help="Output file for analysis results")

    args = parser.parse_args()

    emails_frame = pd.read_json(args.input_file)
    required_columns = {"date", "has_body"}
    missing_columns = required_columns.difference(emails_frame.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns in JSON: {', '.join(sorted(missing_columns))}"
        )
    date_series = pd.to_datetime(
        emails_frame["date"].astype(str).str.slice(0, 19),
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce",
    )
    emails = emails_frame.assign(
        date_parsed=date_series,
        has_body_bool=emails_frame["has_body"].astype(bool),
    ).dropna(subset=["date_parsed"])

    # Perform analysis based on type
    analysis_data: list[AnalysisRow] | SummaryAnalysis
    if args.analysis == "year":
        results = analyze_by_year(emails)
        analysis_data = [
            {
                "year": year,
                "total_emails": data["total"],
                "emails_with_body": data["with_body"],
                "body_percentage": (
                    (data["with_body"] / data["total"] * 100)
                    if data["total"] > 0
                    else 0
                ),
            }
            for year, data in sorted(results.items())
        ]
    elif args.analysis == "month":
        results = analyze_by_month(emails, args.year)
        analysis_data = [
            {
                "month": month,
                "total_emails": data["total"],
                "emails_with_body": data["with_body"],
                "body_percentage": (
                    (data["with_body"] / data["total"] * 100)
                    if data["total"] > 0
                    else 0
                ),
            }
            for month, data in sorted(results.items())
        ]
    elif args.analysis == "weekday":
        results = analyze_by_weekday(emails)
        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        analysis_data = [
            {
                "weekday": day,
                "total_emails": results[day]["total"],
                "emails_with_body": results[day]["with_body"],
                "body_percentage": (
                    (results[day]["with_body"] / results[day]["total"] * 100)
                    if results[day]["total"] > 0
                    else 0
                ),
            }
            for day in weekday_order
            if day in results
        ]
    elif args.analysis == "hour":
        results = analyze_by_hour(emails)
        analysis_data = [
            {
                "hour": hour,
                "total_emails": data["total"],
                "emails_with_body": data["with_body"],
                "body_percentage": (
                    (data["with_body"] / data["total"] * 100)
                    if data["total"] > 0
                    else 0
                ),
            }
            for hour, data in sorted(results.items())
        ]
    else:  # summary
        start_date, end_date = get_date_range(emails)
        yearly = analyze_by_year(emails)
        weekday = analyze_by_weekday(emails)

        analysis_data = {
            "dataset_info": {
                "total_emails": len(emails),
                "emails_with_body": int(emails["has_body_bool"].sum()),
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None,
                },
            },
            "by_year": yearly,
            "by_weekday": weekday,
        }

    # Output results
    if args.output:
        format_used = write_data(analysis_data, args.output, "json")
        print(f"Temporal analysis saved to {args.output} ({format_used})")
    else:
        # Console output
        if args.analysis == "summary":
            summary_data = cast(SummaryAnalysis, analysis_data)
            info = cast(dict[str, object], summary_data["dataset_info"])
            date_range = cast(dict[str, str | None], info["date_range"])
            start = date_range["start"]
            end = date_range["end"]
            print("Temporal Analysis Summary:")
            print(f"  Total emails: {info['total_emails']}")
            print(f"  With bodies: {info['emails_with_body']}")
            if start is not None and end is not None:
                print(f"  Date range: {start[:10]} to {end[:10]}")

            print("\nTop 5 years by volume:")
            by_year = cast(dict[int, dict[str, int]], summary_data["by_year"])
            yearly_sorted = sorted(
                by_year.items(),
                key=lambda x: x[1]["total"],
                reverse=True,
            )
            for year, data in yearly_sorted[:5]:
                print(f"  {year}: {data['total']} emails")
        else:
            rows = cast(list[AnalysisRow], analysis_data)
            print(f"Temporal Analysis ({args.analysis}):")
            for item in rows:
                if "year" in item:
                    period = item["year"]
                elif "month" in item:
                    period = item["month"]
                elif "weekday" in item:
                    period = item["weekday"]
                else:
                    period = item["hour"]
                print(
                    f"  {period}: {item['total_emails']} emails "
                    f"({item['body_percentage']:.1f}% with bodies)"
                )


if __name__ == "__main__":
    main()
