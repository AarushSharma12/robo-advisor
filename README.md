# Portfolio Rebalancing System

A Python-based system for filtering customer accounts and generating trade recommendations based on configurable criteria and market conditions.

## Overview

This system processes customer account data, applies filtering criteria from JSON configuration files, and provides buy/sell recommendations based on current market conditions.

## Project Structure

```
project/
├── data/
│   ├── api/
│   │   ├── rebalance_requests.json    # Filter criteria configurations
│   │   └── robo_advisor.json          # Robo-advisor settings
│   └── market/
│       ├── customer_accounts.csv       # Customer profile data
│       ├── customer_accounts_holdings.csv  # Portfolio holdings
│       ├── market_conditions.csv       # Market sentiment data
│       └── Safari55.csv                # Safari55 fund data
├── scripts/
│   ├── filter_accounts.py             # Main filtering system
│   ├── data_loader.py                 # Data loading utilities
│   ├── account_processor.py           # Account filtering logic
│   ├── view_holdings.py               # Display filtered holdings
│   └── recommend_trades.py            # Trade recommendations
├── output/                             # Generated results (auto-created)
├── requirements.txt
└── README.md
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt
```

## Core Capabilities

### 1. Account Filtering

Filter customer accounts based on multiple criteria defined in JSON configuration files.

**Supported filter criteria:**

- Time Horizon (Short-term, Long-term)
- Risk Tolerance (Conservative, Moderate, Aggressive)
- State/Location
- Annual Income
- Age
- Investment Experience
- And more...

**Supported operators:**

- `=` (equals)
- `!=` (not equals)
- `>`, `<`, `>=`, `<=` (numerical comparisons)

### 2. Holdings Visualization

View portfolio holdings for filtered accounts, including:

- Ticker symbols
- Quantity of shares
- Current price
- Total position value

### 3. Trade Recommendations

Generate buy/sell recommendations based on market conditions:

- **SELL**: When security has negative market condition
- **HOLD**: When security has positive market condition
- **NO DATA**: When no market condition data available

## Usage Examples

### Filter Accounts

```python
# Run the main filtering script
python scripts/filter_accounts.py
```

This will:

- Load customer data and filter criteria
- Apply filters based on request ID
- Display matching accounts
- Save results to `output/` directory

### View Holdings for Filtered Accounts

```python
python scripts/view_holdings.py
```

Output example:

```
Account: f3feaff86948
  ROST - 81 shares @ $39.29 = $3182.49
  EXR - 39 shares @ $124.52 = $4856.28
  IVZ - 68 shares @ $134.54 = $9148.72
```

### Generate Trade Recommendations

```python
python scripts/recommend_trades.py
```

Output example:

```
Account: f3feaff86948
  ROST - 81 shares @ $39.29 = $3182.49 -> NO DATA
  EXR - 39 shares @ $124.52 = $4856.28 -> HOLD
  IVZ - 68 shares @ $134.54 = $9148.72 -> SELL
```

### Programmatic Usage

```python
from scripts.filter_accounts import RebalanceFilter

# Initialize the system
filter_system = RebalanceFilter()
filter_system.initialize()

# Process a specific request
request_id = "c48cd16f-ed5c-426e-a53e-c214e9136055"
result = filter_system.process_single_request(request_id)

# Process all requests
all_results = filter_system.process_all_requests()
```

## Data Files Description

### Input Files

**customer_accounts.csv**

- Customer profile information
- Columns: Account_ID, Age, State, Risk_Tolerance, Time_Horizon, Annual_Income, etc.

**customer_accounts_holdings.csv**

- Portfolio holdings for each account
- Columns: AccountID, Ticker, Qty, Price, PositionTotal

**market_conditions.csv**

- Market sentiment for sectors and securities
- Columns: Type, Name, Condition
- Type: "Sector" or "Security"
- Condition: "Positive" or "Negative"

**rebalance_requests.json**

- Filter criteria configurations
- Each request has a unique identifier and list of criteria
- Example:

```json
{
  "requestIdentifier": "c48cd16f-ed5c-426e-a53e-c214e9136055",
  "accountRebalanceCriterias": [
    {
      "attribute": "state",
      "operator": "=",
      "value": "NY"
    }
  ]
}
```

### Output Files

Generated files are saved to the `output/` directory:

- `filtered_accounts_[request_id].csv` - Filtered account lists
- `holdings_[request_id].csv` - Holdings for filtered accounts

## Key Features

✅ **Flexible Filtering** - Apply multiple AND conditions to filter accounts  
✅ **Batch Processing** - Process multiple rebalance requests at once  
✅ **Holdings Integration** - View portfolio details for filtered accounts  
✅ **Market-Based Recommendations** - Generate trade signals from market conditions  
✅ **CSV Export** - Save all results for further analysis  
✅ **Modular Design** - Easy to extend and maintain

## Requirements

- Python 3.8+
- pandas 2.1.3+
- numpy 1.24.3+

## Contact

aarush.angrish@gmail.com
