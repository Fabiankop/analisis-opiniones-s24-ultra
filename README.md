# Análisis de opiniones — Samsung Galaxy S24 Ultra

Scripts en Python que acompañan al trabajo académico de la asignatura
**Recolección y extracción de datos masivos**.

## Estructura de archivos

```
.
# Opinion Analysis — Samsung Galaxy S24 Ultra

Python scripts that accompany the academic work for the course
**Large-scale data collection and extraction**.

## Project structure

```
.
├── main.py
├── pyproject.toml
├── src/
│   └── contextualization/
│       ├── __init__.py
│       ├── cli.py
│       ├── extraction_scraping.py
│       ├── statistical_analysis.py
│       ├── sentiment_analysis.py
│       └── word_frequency.py
└── README.md
```

## Installation

1. Ensure you have Python 3.9+ installed.
2. Create a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate     # Linux / macOS
   env\Scripts\activate        # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Execution order

Run the steps in order because each stage uses the output from the
previous one. Use `main.py` to run each step:

### 1. Comment extraction (`extraction`)

Before running this step:

1. Create a developer account at https://developer.x.com
2. Generate a Bearer Token
3. Set it as an environment variable:
   ```bash
   export X_BEARER_TOKEN="your_token_here"     # Linux / macOS
   set X_BEARER_TOKEN=your_token_here          # Windows CMD
   ```
4. Run:
   ```bash
   python main.py extraction
   ```

**Output**: `s24_comments.db` (SQLite) with the extracted tweets.

### 2. Statistical analysis (`statistics`)

Processes survey data and generates summary statistics:

```bash
python main.py statistics
```

**Outputs**:
- `survey_statistics.csv` — statistics table
- `likert_distribution.png` — distribution chart
- `averages.png` — mean/median chart

### 3. Sentiment analysis (`sentiment`)

Classifies each comment as positive, neutral, or negative:

```bash
python main.py sentiment
```

**Note**: the first run downloads the BERT model (~700 MB).

**Outputs**:
- `classified_comments.csv` — comments with sentiment
- `sentiment_by_aspect.csv` — analysis by product aspect
- `sentiment_distribution.png` — sentiment charts

### 4. Word frequency analysis (`frequency`)

Identifies the most mentioned words in the comments:

```bash
python main.py frequency
```

**Outputs**:
- `word_frequency.csv` — frequency table
- `word_frequency.png` — bar chart

### Run the full pipeline

```bash
python main.py all
```

## Privacy notes

All scripts comply with **Law 1581 of 2012** (General Data Protection
Regime in Colombia) via:

- **Anonymization** of user IDs (SHA-256 hash).
- **Data minimization**: only the necessary fields are collected.
- **Encryption in transit** via HTTPS.
- **Access tokens** managed through environment variables (never in code).

## Troubleshooting

| Issue | Solution |
|---|---|
| `ImportError: No module named 'tweepy'` | Run `pip install -r requirements.txt` |
| `ValueError: Token not found` | Set the `X_BEARER_TOKEN` environment variable |
| `Out of memory` in step 3 | BERT requires >=4 GB RAM. Close other apps. |
| `LookupError` with NLTK | The script downloads stopwords automatically on first run. |

## Author

[Student name]
[Academic program]
[Institution]
2026
