import re

import pandas as pd


def query_emails(input_file, pattern=None, case_sensitive=False):
    """Query emails matching pattern, return matching emails"""
    emails = pd.read_json(input_file)
    required_columns = {"subject", "body", "has_body"}
    missing_columns = required_columns.difference(emails.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns in JSON: {', '.join(sorted(missing_columns))}"
        )

    if not pattern:
        return emails.to_dict(orient="records")

    flags = 0 if case_sensitive else re.IGNORECASE
    # Pattern search across subject and body.
    regex = re.compile(pattern, flags)

    subject_mask = (
        emails["subject"].fillna("").astype(str).str.contains(regex, na=False)
    )
    body_mask = emails["body"].fillna("").astype(str).str.contains(regex, na=False)
    mask = subject_mask | (body_mask & emails["has_body"].astype(bool))
    return emails[mask].to_dict(orient="records")
