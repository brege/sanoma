import json
import re


def query_emails(input_file, pattern=None, case_sensitive=False):
    """Query emails matching pattern, return matching emails"""
    with open(input_file, "r") as f:
        emails = json.load(f)

    if not pattern:
        return emails

    flags = 0 if case_sensitive else re.IGNORECASE
    # Pattern search across subject and body.
    regex = re.compile(pattern, flags)

    matches = []
    for email in emails:
        if regex.search(email.get("subject", "")) or (
            email.get("has_body") and regex.search(email.get("body", ""))
        ):
            matches.append(email)

    return matches
