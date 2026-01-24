# Cheatsheet

Private workflow reference for Sanoma analysis tasks.

## Data Extraction

Extract complete dataset to CSV (default from config):
```bash
sanoma extract
```

Force JSON output for complex processing:
```bash
sanoma extract --format json
```

## Domain Analysis

### Unsubscribe

Analyze emails containing unsubscribe patterns for WSU emails:
```bash
uv run sanoma/analysis/domains.py \
  data/extract/all.json \
  wsu.edu \
  --pattern unsubscribe
```

All .edu domains with 95% coverage:
```bash
uv run sanoma/analysis/domains.py \
  data/extract/all.json \
  "*.edu" \
  --pattern unsubscribe \
  --threshold 0.95
```

Export top unsubscribe domains to CSV:
```bash
uv run sanoma/analysis/domains.py \
  data/extract/all.json \
  "*.edu" \
  --pattern unsubscribe \
  --output data/analysis/unsubscribe.csv \
  --format csv
```

### Password/Security

Password reset patterns:
```bash
uv run sanoma/analysis/domains.py \
  data/extract/all.json \
  "*.com" \
  --pattern "password|reset" \
  --threshold 0.90
```

Two-factor authentication emails:
```bash
uv run sanoma/analysis/domains.py \
  data/extract/all.json \
  "*.com" \
  --pattern "2fa|two.factor|verification" \
  --threshold 0.85
```

## Bulk Filtering

Get all 2023 emails with bodies:
```bash
sanoma filter \
  data/extract/all.json \
  data/extract/2023_emails.json \
  --year 2023 \
  --has-body
```

Get WSU emails only:
```bash
sanoma filter \
  data/extract/all.json \
  data/extract/wsu.json \
  --domain "wsu.edu" \
  --has-body
```

Marketing emails (common patterns):
```bash
sanoma query \
  data/extract/all.json \
  data/extract/marketing.json \
  --pattern "unsubscribe|newsletter|promotion"
```

## Configuration Notes
Output format configured in `config.yaml` (extract.format).

```
data/
├── analysis        results
├── extract         extracted datasets
├── plots           visualizations output
└── profiles        thunderbird profiles like btajokz2.default-release
```

Regex domain matching is also supported (`*.edu`, `.*\.gov$`)
