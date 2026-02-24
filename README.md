# sanoma

Visualizing and analyzing email trends with YAML workflows and fast Python scripts.  Export Thunderbird's Gloda database to an mbox JSON for convenient slicing and filtering.

## Setup

### Installation
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install -e .
```
This installs the `sanoma` command globally without creating a local venv.

### Thunderbird Profile
1. Ensure your Thunderbird profile is indexed.

   <details>
   <summary>Thunderbird Index Settings</summary>

   <img src="docs/img/screenshot.png" alt="Thunderbird Index Settings" />
   
   </details>

2. Copy your Thunderbird profile to `data/profiles/`:
   ```bash
   cp -r ~/.thunderbird/*.default-release data/profiles/
   ```
   You will need to close Thunderbird because it locks the database while it's running. This profile looks like `xyzabc12.default-release`.

3. Create `config.yaml` from `config.example.yaml` and add the `xyzabc12.default-release` profile path.

### Performance
Since the tool uses direct "Gloda" (**Glo**bal **Da**tabase) access, the JSON extraction takes me roughly 2 seconds to extract 35K emails using a 2015 netbook.

## Workflows

**sanoma** uses YAML workflows in `workflows/` to define multi-step analysis pipelines. 

The workflow runner automatically discovers and executes tools from `sanoma/analysis/` and `sanoma/plot/`, making it easy to chain data extraction, filtering, analysis, and visualization into reproducible pipelines.

Run any workflow:
```bash
sanoma workflow workflows/spam.yaml
```

Generated plots are written to `data/plots/*`.

## Examples

### 1) University Email Reference

| **Tool**               | **Script**                                                   |
|:---------------------- |:------------------------------------------------------------ |
| **Workflow Snippet**   | [`workflows/wsu.yaml`](workflows/wsu.yaml)                   |
| **Plot script**        | [`sanoma/plot/timeline.py`](sanoma/plot/timeline.py)         |
| **Analysis script**    | [`sanoma/analysis/timeline.py`](sanoma/analysis/timeline.py) |

```bash
sanoma workflow workflows/wsu.yaml
```

### 1.1) University Email Seasonality

Academic-year seasonality appears as repeated term-time peaks and summer drops.

![Grad-school Emails (monthly)](docs/img/wsu/timeline.png)

#### Workflow

```yaml
steps:
  - name: plot wsu timeline
    action: plot_temporal
    params:
      input: data/extract/all.json
      filter_domain: wsu.edu
      plot_type: timeline
      output_dir: data/plots/wsu
      title: WSU Email Volume Analysis
      display: save
```

<details>
<summary>Manual Command</summary>

```bash
uv run sanoma/plot/timeline.py \
  data/extract/all.json \
  --plot-type timeline \
  --output-dir data/plots/wsu \
  --title "WSU Email Volume Analysis" \
  --filter-domain wsu.edu \
  --display save
```

</details>

### 1.2) University Email Volume

#### Year-Month Histogram

Year-over-year bars show the same seasonal cadence when grouped by month.

![Grad-school Emails (yearly)](docs/img/wsu/histogram.png)

#### Workflow

```yaml
steps:
  - name: plot wsu histogram
    action: plot_temporal
    params:
      input: data/extract/all.json
      filter_domain: wsu.edu
      plot_type: histogram
      output_dir: data/plots/wsu
      title: WSU Email Volume Analysis
      display: save
```

<details>
<summary>Manual Command</summary>

```bash
uv run sanoma/plot/timeline.py \
  data/extract/all.json \
  --plot-type histogram \
  --output-dir data/plots/wsu \
  --title "WSU Email Volume Analysis" \
  --filter-domain wsu.edu \
  --display save
```

</details>

### 2) Spam Email Reference

| **Tool**               | **Script**                                           |
|:---------------------- |:---------------------------------------------------- |
| **Workflow Snippet**   | [`workflows/spam.yaml`](workflows/spam.yaml)         |
| **Plot script**        | [`sanoma/plot/spam.py`](sanoma/plot/spam.py)         |
| **Analysis script**    | [`sanoma/analysis/spam.py`](sanoma/analysis/spam.py) |

```bash
sanoma workflow workflows/spam.yaml
```

### 2.1) Spam Timeline

Spam frequency rises sharply after enrollment years and remains persistently high.

#### Marketing Spam Trends

Email spam accumulation and its increasing share of all emails over time.

![Spam Timeline](docs/img/spam/timeline.png)

#### Workflow

```yaml
steps:
  - name: plot spam timeline
    action: plot_spam_trends
    params:
      input: data/analysis/spam/keywords.json
      plot_type: timeline
      output_dir: data/plots/spam
      title: Marketing Spam Trends Analysis
      display: save
```

<details>
<summary>Manual Command</summary>

```bash
uv run sanoma/plot/spam.py \
  data/analysis/spam/keywords.json \
  --plot-type timeline \
  --output-dir data/plots/spam \
  --title "Marketing Spam Trends Analysis" \
  --display save
```

</details>

### 2.2) Spam Type Distribution

Keyword totals show which marketing-language patterns dominate over time.

![Spam Keywords](docs/img/spam/keywords.png)

#### Workflow

```yaml
steps:
  - name: plot spam keywords
    action: plot_spam_trends
    params:
      input: data/analysis/spam/keywords.json
      plot_type: keywords
      output_dir: data/plots/spam
      title: Marketing Spam Trends Analysis
      display: save
```

<details>
<summary>Manual Command</summary>

```bash
uv run sanoma/plot/spam.py \
  data/analysis/spam/keywords.json \
  --plot-type keywords \
  --output-dir data/plots/spam \
  --title "Marketing Spam Trends Analysis" \
  --display save
```

</details>

### 2.3) Spam Heatmap: the curse of Satisfaction Surveys

The heatmap highlights long-running persistence of recurring keyword families by year.

![Spam Heatmap](docs/img/spam/heatmap.png)

#### Workflow

```yaml
steps:
  - name: plot spam heatmap
    action: plot_spam_trends
    params:
      input: data/analysis/spam/keywords.json
      plot_type: heatmap
      output_dir: data/plots/spam
      title: Marketing Spam Trends Analysis
      display: save
```

<details>
<summary>Manual Command</summary>

```bash
uv run sanoma/plot/spam.py \
  data/analysis/spam/keywords.json \
  --plot-type heatmap \
  --output-dir data/plots/spam \
  --title "Marketing Spam Trends Analysis" \
  --display save
```

</details>

## Usage

### Command Line Interface

**Extract** complete dataset from Thunderbird:
```bash
sanoma extract [--output data/extract/all.json]
```

**Filter** emails by criteria:
```bash
sanoma filter input.json output.json --domain "*.edu" --year 2023
```

**Query** emails by content pattern:
```bash
sanoma query input.json output.json --pattern "unsubscribe"
```

Show dataset **statistics**:
```bash
sanoma stats input.json
```

### Domain Analysis

Analyze domains producing emails with specific patterns:
```bash
uv run sanoma/analysis/domains.py \
  data/extract/all.json "*.edu" \
  --pattern "unsubscribe" \
  --threshold 0.95
```


## License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)
