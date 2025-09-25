# Portfolio Trade Recommendation System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](requirements.txt)
[![pandas](https://img.shields.io/badge/pandas-2.1.3-150458.svg)](requirements.txt)
[![numpy](https://img.shields.io/badge/numpy-1.24.3-013243.svg)](requirements.txt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An automated Python system that generates actionable buy/sell trade recommendations for customer portfolios based on configurable account filters and market conditions.

## Why it’s useful

- Automates portfolio rebalancing from raw CSV/JSON inputs
- Flexible account filtering with multiple criteria and operators
- Intelligent fallback to sector sentiment when security-level data is missing
- Single-command execution producing structured JSON output for downstream systems
- Scales to thousands of accounts and hundreds of securities

## Project structure

```
fidelity-robo/
├── data/
│   ├── api_data/
│   │   └── rebalance_requests.json      # Filter configurations
│   └── market_data/
│       ├── customer_accounts.csv        # Account profiles
│       ├── customer_accounts_holdings.csv   # Portfolio positions
│       ├── market_conditions.csv        # Market sentiment by ticker/sector
│       └── Safari55.csv                 # Security → sector mappings
├── scripts/
│   ├── recommend_trades.py              # Main entry point
│   ├── trade_recommender.py             # Core recommendation engine
│   ├── account_processor.py             # Account filtering logic
│   └── data_loader.py                   # Data I/O utilities
├── output/
│   └── trade_recommendations.json       # Generated trade signals
└── requirements.txt
```

Quick links:

- Main script: [scripts/recommend_trades.py](scripts/recommend_trades.py)
- Engine: [scripts/trade_recommender.py](scripts/trade_recommender.py)
- Account filtering: [scripts/account_processor.py](scripts/account_processor.py)
- Data I/O: [scripts/data_loader.py](scripts/data_loader.py)
- Config: [data/api_data/rebalance_requests.json](data/api_data/rebalance_requests.json)
- Sample inputs: [data/market_data](data/market_data)
- Output: [output/trade_recommendations.json](output/trade_recommendations.json)
- License: [LICENSE](LICENSE)
- Requirements: [requirements.txt](requirements.txt)

## Getting started

### Prerequisites

- Python 3.8+
- pip
- Windows, macOS, or Linux

### Install

On Windows (PowerShell):

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configure

1. Set account filter criteria in [data/api_data/rebalance_requests.json](data/api_data/rebalance_requests.json). Example:

```json
{
  "requestIdentifier": "unique-id",
  "accountRebalanceCriterias": [
    { "attribute": "state", "operator": "=", "value": "NY" },
    { "attribute": "riskTolerance", "operator": "!=", "value": "Conservative" }
  ]
}
```

Supported operators:

- "=" (equals)
- "!=" (not equals)
- ">", "<", ">=", "<=" (numeric comparisons)

2. (Optional) If your pipeline uses distinct request IDs, update `REQUEST_ID` in [scripts/recommend_trades.py](scripts/recommend_trades.py).

```python
REQUEST_ID = "your-request-id-here"
```

### Run

```powershell
python scripts/recommend_trades.py
```

- Input files are read from [data/market_data](data/market_data) and [data/api_data](data/api_data).
- Output is written to [output/trade_recommendations.json](output/trade_recommendations.json).

### Example output

```json
{
  "requestIdentifier": "c48cd16f-ed5c-426e-a53e-c214e9136055",
  "accounts": [
    {
      "Account_ID": "f3feaff86948",
      "trades": [
        { "Ticker": "AAPL", "Qty": 100, "Recommended_Trade": "SELL" },
        { "Ticker": "GOOGL", "Qty": 50, "Recommended_Trade": "BUY" }
      ]
    }
  ]
}
```

## How it works

1. Filter Accounts: load [data/api_data/rebalance_requests.json](data/api_data/rebalance_requests.json) and apply multi-criteria filters to [data/market_data/customer_accounts.csv](data/market_data/customer_accounts.csv).
2. Analyze Holdings: read positions from [data/market_data/customer_accounts_holdings.csv](data/market_data/customer_accounts_holdings.csv).
3. Check Market Conditions: join with [data/market_data/market_conditions.csv](data/market_data/market_conditions.csv), falling back to sector sentiment using [data/market_data/Safari55.csv](data/market_data/Safari55.csv) when needed.
4. Generate Trades:
   - BUY: Positive condition (e.g., increase position)
   - SELL: Negative condition (e.g., reduce/liquidate)
   - Fallback: Sector-level condition if ticker sentiment is unavailable
5. Export JSON: write to [output/trade_recommendations.json](output/trade_recommendations.json).

## Performance

- Processes 10,000+ accounts in seconds
- Analyzes 500+ securities with sector fallback
- Single-pass generation of trade recommendations

### Performance and quality tips

- Use OpenAI models for accuracy vs speed:
  - Quality: python scripts\openai_sentiment.py -f data\articles\article1.txt --quality quality
  - Speed: python scripts\openai_sentiment.py -f data\articles\article1.txt --quality speed
  - Or set a specific model: --model gpt-4o
- Set a timeout to avoid stalls: --timeout 20
- Skip the second retry for speed when acceptable: --no-retry
- Enable on-disk cache (default) to avoid re-calling the LLM for the same article; disable via --no-cache

### Secrets (OpenAI API key)

Prefer a local .env file (ignored by git):

Create c:\Users\aarus\robo-advisor\.env with:

```
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
# Optional:
OPENAI_MODEL=gpt-4o
# or choose a preset via quality flag:
# OPENAI_QUALITY=quality  # speed | balanced | quality
# OPENAI_TIMEOUT=20
```

Precedence:

1. --key
2. OS env OPENAI_API_KEY (including values loaded from .env or --env-file)
3. --key-file or OPENAI_API_KEY_FILE

Examples (PowerShell):

```powershell
# Using .env
'OPENAI_API_KEY=YOUR_OPENAI_API_KEY' | Out-File -FilePath .env -Encoding utf8 -NoNewline
python scripts\openai_sentiment.py -f data\articles\article1.txt --quality quality

# Using a custom env file
python scripts\openai_sentiment.py -f data\articles\article1.txt --env-file .config\dev.env

# Using an explicit key file (no defaults)
python scripts\openai_sentiment.py -f data\articles\article1.txt --key-file C:\path\to\openai_api_key.txt
```

### Test LLM sentiment extraction

Use the built-in CLI to extract sentiments from an article (uses .env for OPENAI_API_KEY):

```powershell
python scripts\openai_sentiment.py -f data\articles\article1.txt
```

Expected output shape:

```json
{
  "entities": [
    { "name": "AAPL", "type": "Company", "sentiment": "Positive" },
    { "name": "Energy Sector", "type": "Sector", "sentiment": "Neutral" }
  ]
}
```

Notes:

- Company names must be tickers (uppercase); Sectors may include “Sector”.
- In trade generation, Neutral is treated as HOLD.
  ]
  }

````

Notes:

- Company names must be tickers (uppercase); Sectors may include “Sector”.

```powershell
python scripts\gemini_sentiment.py -f data\articles\article1.txt
````

Expected output shape (Neutral supported):

```json
{
  "entities": [
    { "name": "AAPL", "type": "Company", "sentiment": "Positive" },
    { "name": "Energy Sector", "type": "Sector", "sentiment": "Neutral" }
  ]
}
```

Notes:

- Company names must be tickers (uppercase); Sectors may include “Sector”.
- In trade generation, Neutral is treated as HOLD.
