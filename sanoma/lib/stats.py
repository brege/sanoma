import json


def stats(input_file):
    """Show dataset statistics"""
    with open(input_file, "r") as f:
        emails = json.load(f)

    domains = {}
    years = {}
    folders = {}
    with_bodies = 0

    for email in emails:
        domain = email.get("from_domain", "unknown")
        domains[domain] = domains.get(domain, 0) + 1

        date = email.get("date", "")
        year = date[:4] if len(date) >= 4 else "unknown"
        years[year] = years.get(year, 0) + 1

        folder = email.get("folder", "unknown")
        folders[folder] = folders.get(folder, 0) + 1

        if email.get("has_body"):
            with_bodies += 1

    print("Dataset Statistics:")
    print(f"  Total emails: {len(emails)}")
    print(f"  Emails with bodies: {with_bodies}")
    print(f"  Unique domains: {len(domains)}")
    print(f"  Date range: {min(years.keys())} to {max(years.keys())}")
    print("\nTop 10 domains:")
    for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"    {domain}: {count}")
