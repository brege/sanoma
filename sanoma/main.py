"""
Sanoma - Email analysis and workflow orchestration for Thunderbird
"""

import argparse

from sanoma.lib.output import write_data
from sanoma.lib.config import (
    load_config,
    get_profile_path,
    get_default_complete_dataset_path,
)
from sanoma.lib.extract import extract_complete_dataset
from sanoma.lib.filter import filter_emails
from sanoma.lib.query import query_emails
from sanoma.lib.stats import stats


def main():
    """Entry point for sanoma CLI"""
    parser = argparse.ArgumentParser(description="Sanoma - Thunderbird email analysis")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Extract command
    extract_parser = subparsers.add_parser(
        "extract", help="Extract complete dataset from Thunderbird"
    )
    extract_parser.add_argument("--profile", help="Path to Thunderbird profile")
    extract_parser.add_argument("--output", help="Output file")

    # Filter command
    filter_parser = subparsers.add_parser("filter", help="Filter emails")
    filter_parser.add_argument("input_file", help="Input JSON file")
    filter_parser.add_argument("output_file", help="Output file")
    filter_parser.add_argument("--domain", help="Filter by domain")
    filter_parser.add_argument("--year", help="Filter by year")
    filter_parser.add_argument("--subject-contains", help="Filter by subject content")
    filter_parser.add_argument(
        "--has-body", action="store_true", help="Only emails with bodies"
    )
    filter_parser.add_argument("--limit", type=int, help="Limit results")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query emails matching pattern")
    query_parser.add_argument("input_file", help="Input JSON file")
    query_parser.add_argument("output_file", help="Output file")
    query_parser.add_argument("--pattern", help="Pattern to search for")
    query_parser.add_argument(
        "--case-sensitive", action="store_true", help="Case sensitive search"
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show dataset statistics")
    stats_parser.add_argument("input_file", help="Input JSON file")

    # Workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Run YAML workflow")
    workflow_parser.add_argument("workflow_file", help="Path to workflow YAML file")

    args = parser.parse_args()

    try:
        config = load_config()

        if args.command == "extract":
            profile = get_profile_path(config, args.profile)
            output = args.output or get_default_complete_dataset_path(config)
            extract_complete_dataset(profile, output, config)
        elif args.command == "filter":
            filter_emails(
                args.input_file,
                args.output_file,
                domain=args.domain,
                year=args.year,
                subject_contains=args.subject_contains,
                has_body=args.has_body,
                limit=args.limit,
            )
        elif args.command == "query":
            results = query_emails(args.input_file, args.pattern, args.case_sensitive)
            format_used = write_data(results, args.output_file, "json")
            print(
                f"Found {len(results)} matching emails, saved to "
                f"{args.output_file} ({format_used})"
            )
        elif args.command == "stats":
            stats(args.input_file)
        elif args.command == "workflow":
            from sanoma.lib.workflow import run_workflow

            success = run_workflow(args.workflow_file)
            exit(0 if success else 1)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
