import re
import sqlite3
from pathlib import Path

from sanoma.lib.output import write_data
from sanoma.lib.config import get_extraction_filters, should_filter_email


def extract_domain(email_addr):
    """Extract domain from email address"""
    if not email_addr:
        return "unknown"
    email_str = str(email_addr)
    # Match either "<user@domain>" or "user@domain".
    match = re.search(r"<([^>]+)>|([^\s<>]+@[^\s<>]+)", email_str)
    if match:
        email_clean = match.group(1) or match.group(2)
        # Extract domain part.
        domain_match = re.search(r"@([a-zA-Z0-9.-]+)", email_clean)
        return domain_match.group(1).lower() if domain_match else "malformed"
    return "malformed"


def extract_complete_dataset(
    profile_path, output_file, output_format="json", config=None
):
    """Extract complete email dataset from Gloda"""
    db_path = Path(profile_path) / "global-messages-db.sqlite"
    if not db_path.exists():
        raise FileNotFoundError(f"Gloda database not found at {db_path}")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    sql = """
        SELECT
            m.headerMessageID,
            datetime(m.date/1000000, 'unixepoch') as date_formatted,
            t.c3author as from_field,
            t.c4recipients as to_field,
            t.c1subject as subject,
            t.c0body as body_text,
            fl.name as folder_path
        FROM messages m
        LEFT JOIN messagesText_content t ON m.id = t.docid
        LEFT JOIN folderLocations fl ON m.folderID = fl.id
        ORDER BY m.date DESC
    """

    print("Extracting complete dataset from Thunderbird Gloda...")
    cursor.execute(sql)
    rows = cursor.fetchall()

    filters = get_extraction_filters(config or {})

    emails = []
    filtered_count = 0
    for row in rows:
        (msg_id, date, from_field, to_field, subject, body_text, folder_path) = row
        email = {
            "message_id": (
                f"<{msg_id}>" if msg_id and not msg_id.startswith("<") else msg_id or ""
            ),
            "date": date or "",
            "from": from_field or "",
            "from_domain": extract_domain(from_field or ""),
            "to": to_field or "",
            "subject": subject or "",
            "folder": folder_path or "",
            "body": body_text or "",
            "has_body": bool(body_text),
        }

        if should_filter_email(email, filters):
            filtered_count += 1
            continue

        emails.append(email)

    conn.close()

    format_used = write_data(emails, output_file, output_format)

    with_bodies = sum(1 for e in emails if e["has_body"])
    filter_msg = f" (filtered out {filtered_count})" if filtered_count > 0 else ""
    print(
        f"Extracted {len(emails)} emails ({with_bodies} with bodies) "
        f"to {output_file} ({format_used}){filter_msg}"
    )
