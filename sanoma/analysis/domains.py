#!/usr/bin/env python3
"""
Domain analysis tool using sanoma lib helpers and output adapters
"""

import re
import argparse
from collections import Counter

import pandas as pd

from sanoma.lib.output import write_data  # noqa: E402


def filter_emails_by_domain(emails, domain_pattern):
    """Filter emails by sender domain pattern"""
    from_domains = emails["from_domain"].astype(str)
    if domain_pattern.startswith("*."):
        suffix = domain_pattern[2:].lower()
        mask = from_domains.str.lower().str.endswith(suffix, na=False)
        return emails[mask]

    # Allow regex-based domain matching.
    domain_regex = re.compile(domain_pattern, re.IGNORECASE)
    mask = from_domains.str.contains(domain_regex, na=False)
    return emails[mask]


def get_pattern_emails(emails, pattern):
    """Get emails containing pattern"""
    combined = (
        emails["subject"].fillna("").astype(str)
        + " "
        + emails["body"].fillna("").astype(str)
    )
    mask = combined.str.contains(pattern, case=False, regex=True, na=False)
    return emails[mask]


def analyze_top_domains(emails, threshold=0.95):
    """Find domains producing threshold% of pattern-matching emails"""
    domain_counts = Counter(emails["from_domain"].astype(str))
    total = len(emails.index)

    sorted_domains = domain_counts.most_common()
    cumulative = 0
    top_domains = []

    for domain, count in sorted_domains:
        cumulative += count
        percentage = count / total * 100
        cumulative_percentage = cumulative / total

        top_domains.append(
            {
                "domain": domain,
                "count": count,
                "percentage": percentage,
                "cumulative_percentage": cumulative_percentage,
            }
        )

        if cumulative_percentage >= threshold:
            break

    return top_domains, cumulative / total


def main():
    parser = argparse.ArgumentParser(description="Domain analysis for email patterns")
    parser.add_argument("input_file", help="Input dataset file")
    parser.add_argument(
        "compare_pattern", help="Domain pattern to compare (e.g., wsu.edu)"
    )
    parser.add_argument(
        "--pattern",
        default="unsubscribe",
        help="Email content pattern to analyze (default: unsubscribe)",
    )
    parser.add_argument("--output", help="Output file for analysis results")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.95,
        help="Coverage threshold (default: 0.95)",
    )

    args = parser.parse_args()

    emails_frame = pd.read_json(args.input_file)
    required_columns = {"from_domain", "subject", "body"}
    missing_columns = required_columns.difference(emails_frame.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns in JSON: {', '.join(sorted(missing_columns))}"
        )

    pattern_emails = get_pattern_emails(emails_frame, args.pattern)
    top_domains, coverage = analyze_top_domains(pattern_emails, args.threshold)

    compare_emails = filter_emails_by_domain(emails_frame, args.compare_pattern)

    # Prepare analysis results
    analysis_results = {
        "pattern_analysis": {
            "pattern": args.pattern,
            "total_emails": int(pattern_emails.shape[0]),
            "coverage_threshold": args.threshold,
            "actual_coverage": coverage,
            "top_domains": top_domains,
        },
        "comparison": {
            "pattern": args.compare_pattern,
            "total_emails": int(compare_emails.shape[0]),
            "domains": list(set(compare_emails["from_domain"].astype(str))),
        },
    }

    # Find overlap
    compare_domains = set(compare_emails["from_domain"].astype(str))
    top_domain_names = set(d["domain"] for d in top_domains)
    overlap = list(compare_domains.intersection(top_domain_names))
    analysis_results["overlap"] = overlap

    if args.output:
        format_used = write_data(analysis_results, args.output, "json")
        print(f"Analysis saved to {args.output} ({format_used})")
    else:
        # Console output
        print(f"Pattern Analysis ('{args.pattern}'):")
        print(f"  Total pattern emails: {len(pattern_emails)}")
        print(f"  Top domains cover {coverage*100:.1f}% of pattern volume:")
        for i, domain_info in enumerate(top_domains, 1):
            print(
                f"    {i:2d}. {domain_info['domain']:<30} "
                f"{domain_info['count']:>5} "
                f"({domain_info['percentage']:>5.1f}%)"
            )
        print(f"\nComparison with {args.compare_pattern}:")
        print(f"  Total {args.compare_pattern} emails: {len(compare_emails)}")
        if overlap:
            print(f"  Overlap domains: {', '.join(overlap)}")
        else:
            print(
                f"  No overlap between top pattern domains and "
                f"{args.compare_pattern}"
            )


if __name__ == "__main__":
    main()
