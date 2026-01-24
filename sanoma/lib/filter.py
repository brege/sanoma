import json
import re

from sanoma.lib.output import write_data


def filter_emails(input_file, output_file, output_format="json", **filters):
    """Filter emails by various criteria"""
    with open(input_file, "r") as f:
        emails = json.load(f)

    results = emails

    for key, value in filters.items():
        if key == "domain" and value:
            if value.startswith("*."):
                # Match wildcard suffix like "*.edu".
                domain_suffix = value[2:].lower()
                results = [
                    e
                    for e in results
                    if e.get("from_domain", "").lower().endswith(domain_suffix)
                ]
            else:
                # Treat as regex, fall back to exact match if invalid.
                try:
                    domain_regex = re.compile(value, re.IGNORECASE)
                    results = [
                        e
                        for e in results
                        if domain_regex.search(e.get("from_domain", ""))
                    ]
                except re.error:
                    results = [
                        e
                        for e in results
                        if e.get("from_domain", "").lower() == value.lower()
                    ]
        elif key == "year" and value:
            results = [e for e in results if value in str(e.get("date", ""))]
        elif key == "subject_contains" and value:
            results = [
                e for e in results if value.lower() in e.get("subject", "").lower()
            ]
        elif key == "has_body" and value:
            results = [e for e in results if e.get("has_body") is True]
        elif key == "limit" and value:
            results = results[: int(value)]

    format_used = write_data(results, output_file, output_format)

    print(f"Filtered to {len(results)} emails, saved to {output_file} ({format_used})")
