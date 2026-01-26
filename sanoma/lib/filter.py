import re

import pandas as pd

from sanoma.lib.output import write_data


def filter_emails(input_file, output_file, **filters):
    """Filter emails by various criteria"""
    emails = pd.read_json(input_file)
    required_columns = {"from_domain", "date", "subject", "has_body"}
    missing_columns = required_columns.difference(emails.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns in JSON: {', '.join(sorted(missing_columns))}"
        )

    results = emails

    for key, value in filters.items():
        if key == "domain" and value:
            if value.startswith("*."):
                # Match wildcard suffix like "*.edu".
                domain_suffix = value[2:].lower()
                domain_series = results["from_domain"].astype(str).str.lower()
                results = results[domain_series.str.endswith(domain_suffix, na=False)]
            else:
                # Treat as regex, fall back to exact match if invalid.
                try:
                    domain_regex = re.compile(value, re.IGNORECASE)
                    domain_series = results["from_domain"].astype(str)
                    results = results[
                        domain_series.str.contains(domain_regex, na=False)
                    ]
                except re.error:
                    domain_series = results["from_domain"].astype(str).str.lower()
                    results = results[domain_series == value.lower()]
        elif key == "year" and value:
            date_series = results["date"].astype(str)
            results = results[date_series.str.contains(str(value), na=False)]
        elif key == "subject_contains" and value:
            subject_series = results["subject"].astype(str).str.lower()
            results = results[subject_series.str.contains(value.lower(), na=False)]
        elif key == "has_body" and value:
            results = results[results["has_body"].astype(bool)]
        elif key == "limit" and value:
            results = results.head(int(value))

    format_used = write_data(results.to_dict(orient="records"), output_file, "json")

    print(
        f"Filtered to {len(results.index)} emails, saved to "
        f"{output_file} ({format_used})"
    )
