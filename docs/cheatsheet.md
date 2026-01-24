# Personal Analysis Cheatsheet

Private workflow reference for Sanoma analysis tasks.

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
python3 -m sanoma.analysis.domains data/extract/all.json wsu.edu --pattern unsubscribe

# All .edu domains with 95% coverage
python3 -m sanoma.analysis.domains data/extract/all.json "*.edu" --pattern unsubscribe --threshold 0.95

# Export top unsubscribe domains to CSV
python3 -m sanoma.analysis.domains data/extract/all.json "*.edu" --pattern unsubscribe --output data/analysis/unsubscribe.csv --format csv
```

### Password/Security Analysis
```bash
# Password reset patterns
python3 -m sanoma.analysis.domains data/extract/all.json "*.com" --pattern "password|reset" --threshold 0.90

# Two-factor authentication emails
python3 -m sanoma.analysis.domains data/extract/all.json "*.com" --pattern "2fa|two.factor|verification" --threshold 0.85
```

### Bulk Filtering
```bash
# Get all 2023 emails with bodies
python3 tm.py filter data/extract/all.json data/extract/2023_emails.json --year 2023 --has-body

# Get WSU emails only
python3 tm.py filter data/extract/all.json data/extract/wsu.json --domain "wsu.edu" --has-body

# Marketing emails (common patterns)
python3 tm.py query data/extract/all.json data/extract/marketing.json --pattern "unsubscribe|newsletter|promotion"
```

## Configuration Notes
- Default output format configured in `config.yaml`
- Profile: `btajokz2.default-release`
- Extract dir: `data/extract/` (datasets)
- Data dirs: `data/analysis/`, `data/plots/`, `data/profiles/`
- Regex domain matching supported (`*.edu`, `.*\.gov$`, etc.)

## Performance Expectations
- Complete extraction: ~2 seconds (35k emails)
- Filtering: instant (JSON processing)
- Domain analysis: 1-2 seconds for full dataset
