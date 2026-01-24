# Personal Analysis Cheatsheet

Private workflow reference for Thunder Muscle analysis tasks.

## Data Extraction
```bash
# Extract complete dataset to CSV (default from config)
python3 tm.py extract

# Force JSON output for complex processing
python3 tm.py extract --format json
```

## Domain Analysis Workflows

### Unsubscribe Analysis
```bash
# WSU unsubscribe analysis
python3 analyze_domains.py data/complete_dataset.json wsu.edu --pattern unsubscribe

# All .edu domains with 95% coverage
python3 analyze_domains.py data/complete_dataset.json "*.edu" --pattern unsubscribe --threshold 0.95

# Export top unsubscribe domains to CSV
python3 analyze_domains.py data/complete_dataset.json "*.edu" --pattern unsubscribe --output unsubscribe_domains.csv --format csv
```

### Password/Security Analysis
```bash
# Password reset patterns
python3 analyze_domains.py data/complete_dataset.json "*.com" --pattern "password|reset" --threshold 0.90

# Two-factor authentication emails
python3 analyze_domains.py data/complete_dataset.json "*.com" --pattern "2fa|two.factor|verification" --threshold 0.85
```

### Bulk Filtering
```bash
# Get all 2023 emails with bodies
python3 tm.py filter data/complete_dataset.json data/2023_emails.json --year 2023 --has-body

# Get WSU emails only
python3 tm.py filter data/complete_dataset.json data/wsu_emails.json --domain "wsu.edu" --has-body

# Marketing emails (common patterns)
python3 tm.py query data/complete_dataset.json data/marketing.json --pattern "unsubscribe|newsletter|promotion"
```

## Configuration Notes
- Default CSV output for spreadsheet analysis
- Profile: `btajokz2.default-release` 
- Data dir: `data/`
- Regex domain matching supported (`*.edu`, `.*\.gov$`, etc.)

## Performance Expectations
- Complete extraction: ~2 seconds (35k emails)
- Filtering: instant (JSON processing)
- Domain analysis: 1-2 seconds for full dataset
