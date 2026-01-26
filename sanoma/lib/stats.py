import pandas as pd


def stats(input_file):
    """Show dataset statistics"""
    emails = pd.read_json(input_file)
    required_columns = {"from_domain", "date", "folder", "has_body"}
    missing_columns = required_columns.difference(emails.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns in JSON: {', '.join(sorted(missing_columns))}"
        )

    domains = emails["from_domain"].astype(str).value_counts()
    years = emails["date"].astype(str).str.slice(0, 4).replace("", "unknown")
    years = years.value_counts()
    with_bodies = int(emails["has_body"].astype(bool).sum())

    print("Dataset Statistics:")
    print(f"  Total emails: {len(emails.index)}")
    print(f"  Emails with bodies: {with_bodies}")
    print(f"  Unique domains: {len(domains.index)}")
    print(f"  Date range: {years.index.min()} to {years.index.max()}")
    print("\nTop 10 domains:")
    for domain, count in domains.head(10).items():
        print(f"    {domain}: {int(count)}")
