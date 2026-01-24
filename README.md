# sanoma

Fast Thunderbird email dataset extraction and analysis using Gloda database.

## Setup

### Installation
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install -e .
```
This installs the `sanoma` command globally without creating a local venv.

### Thunderbird Profile
1. Ensure your Thunderbird profile is indexed.
   ![Thunderbird Index Settings](docs/img/screenshot.png)

2. Copy your Thunderbird profile to `data/profiles/`:
   ```bash
   cp -r ~/.thunderbird/*.default-release data/profiles/
   ```
   If running on the in-situ profile, close Thunderbird first.

3. Update `config.yaml` with your profile folder name if it differs from `btajokz2.default-release`.

## Usage

### Command Line Interface

Extract complete dataset from Thunderbird:
```bash
sanoma extract [--output data/extract/all.json]
```

Filter emails by criteria:
```bash
sanoma filter input.json output.json --domain "*.edu" --year 2023
```

Query emails by content pattern:
```bash
sanoma query input.json output.json --pattern "unsubscribe"
```

Show dataset statistics:
```bash
sanoma stats input.json
```

### Domain Analysis

Analyze domains producing emails with specific patterns:
```bash
uv run sanoma/analysis/domains.py data/extract/all.json "*.edu" --pattern "unsubscribe" --threshold 0.95
```

## Output Formats

All commands support `--format json|csv|yaml`. Default format configured in `config.yaml`.

## Performance

Since the tool uses direct "Gloda" (**Glo**bal **Da**tabase) access, the JSON extraction takes roughly 2 seconds to extract 35K emails on a 2015 netbook.

## Workflows [ `workflows/` ]

**sanoma** uses YAML workflows to define multi-step analysis pipelines. The workflow runner automatically discovers and executes tools from the `sanoma/analysis/`, `sanoma/plot/`, and `sanoma/tools/` directories, making it easy to chain data extraction, filtering, analysis, and visualization into reproducible pipelines.

Run any workflow:
```bash
sanoma workflow workflows/spam.yaml
```

I'm not intentionally a data hoarder, I'm just not an aggressive email deleter and filter user. 
This has changed some in recent years, as the techniques for spam emails have evolved to covertly trojan "survey" subterfuge into your mailbox. Surveys are marketing emails, and a quick analysis on my email history (minimal deletions) has shown that my hunch on survey spam is mostly correct. Around 2023, I began marking all surveys as spam.

Much of this can be done in a Jupyter notebook--far easier to refresh plots this way--although `:MarkdownPreview` in **Neovim** is quite good. I'm not against notebooks. They are far more friendly than this model. 

I developed this method in my Markdown-to-PDF project--**[oshea](https://github.com/brege/oshea)**--where I realized comprehensive end-to-end tests were just manifest workflows. It's an intuitive way to string command line sequences together. The *pipeline* term in machine learning/data science is congruent to this system.

```bash
docs/img/ # <- data/plots/ <- workflows/
├── spam
│   ├── heatmap.png
│   ├── keywords.png
│   └── timeline.png
└── wsu
    ├── timeline.png
    └── histogram.png
```

#### Grad-school Emails

The monthly timeline reveals the academic year rhythm: high volume during active semesters with dramatic drops during summer breaks and winter holidays. The 2016-2017 dip corresponds to dissertation defense period, where militant email sanitation was a reprieve from LaTeX and simulation monitoring--hence the dip.

My personal dataset has about 35K emails between my grad-school emails and [my current website's](https://brege.org) personal email. Not included are my Gmail and undergrad email(s). I plan on synchronizing those at a later date.

- **[`workflows/wsu.yaml`](workflows/wsu.yaml)**
- **[`plot/timeline.py`](plot/timeline.py)**
- **[`analysis/timeline.py`](analysis/timeline.py)**

![Grad-school Emails (monthly)](docs/img/wsu/timeline.png)

WSU's Okta system requires(d) changing passwords every 6 months, and sometime a couple years after my defense my account died. I am thankful that I had a thunderbird profile tucked away on a drive that allowed me to recover all of my university emails..

![Grad-school Emails (yearly)](docs/img/wsu/histogram.png)

The year-over-year histogram demonstrates consistent academic seasonality, with September-April peaks and May -- mid-August valleys across all years of graduate study.  Even with teaching summer labs, the beuracratic pressure in the summertime dies. I loved teaching in the summer.

#### Spam Emails

- **[`workflows/spam.yaml`](workflows/spam.yaml)**
- **[`plot/spam.py`](plot/spam.py)**
- **[`analysis/spam.py`](analysis/spam.py)**

The spam timeline shows minimal marketing emails pre-2010, followed by a sharp increase around university enrollment. By 2015, spam reached 60-80% of all emails and has remained consistently high. The GDPR implementation around 2018 created a spike in `unsubscribe` language as companies scrambled to comply with new regulations.

![Spam Timeline](docs/img/spam/timeline.png)

The tail in the beginning of this timeline is presented for context.
It only includes a "purified" hotmail account mailbox from my teenage years that extended a bit into my undergrad years. Those years overlap with gmail usage (not integrated into this data) and my GVSU university email.

![Spam Keywords](docs/img/spam/keywords.png)


Another useful filter for spam emails is checking for keywords like **`unsubscribe`** in the message body.

`unsubscribe_bait` dominates with over 12,500 matches, followed by `satisfaction` surveys (~8k) and direct "survey" requests (~4k). This reveals how modern marketing shifted from direct sales to engagement-focused tactics requesting feedback and reviews.

![Spam Heatmap](docs/img/spam/heatmap.png)

The heatmap (filtered to post-2010) shows "satisfaction" spam as the most persistent threat, maintaining 20-25% frequency from 2012 onwards. Survey-based spam shows steady growth, intensifying after 2020, when both GDPR constraints pressured companies to invent new angles of attack, becoming increasingly desperate for customer "feedback" (attention) during the pandemic. **Satisfaction feedback surveys are advertisements.**

## License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)
