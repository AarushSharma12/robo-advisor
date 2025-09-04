# Portfolio Rebalancing System

An automated Python-based portfolio management system that filters customer accounts, analyzes holdings, and generates actionable trade recommendations based on market conditions and configurable investment criteria.

## 🎯 Overview

This system streamlines portfolio rebalancing by:

- Processing thousands of customer accounts against complex filtering criteria
- Analyzing portfolio holdings and market conditions
- Generating data-driven buy/sell/hold recommendations
- Outputting structured JSON for downstream trading systems

## 📁 Project Structure

```
fidelity-robo/
├── data/
│   ├── api_data/
│   │   ├── rebalance_requests.json    # Filter criteria configurations
│   │   └── robo_advisor.json          # Robo-advisor settings
│   └── market_data/
│       ├── customer_accounts.csv       # Customer profile data
│       ├── customer_accounts_holdings.csv  # Portfolio holdings
│       ├── market_conditions.csv       # Market sentiment indicators
│       └── Safari55.csv                # S&P 500 security metadata & sectors
├── scripts/
│   ├── __init__.py                    # Package initialization
│   ├── data_loader.py                 # Data I/O utilities
│   ├── account_processor.py           # Account filtering engine
│   ├── filter_accounts.py             # Main orchestration module
│   └── recommend_trades.py            # Trade recommendation generator
├── output/
│   └── trade_recommendations.json     # Generated trade signals
├── LICENSE                             # MIT License
├── README.md                           # Documentation
└── requirements.txt                    # Python dependencies
```

## 🚀 Installation

```bash
# Clone repository
git clone [repository-url]
cd fidelity-robo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 💡 Core Features

### 1. **Dynamic Account Filtering**

Apply complex, multi-criteria filters to identify target accounts:

```python
python scripts/filter_accounts.py
```

- Supports multiple operators (=, !=, >, <, >=, <=)
- AND logic for multiple conditions
- Filters on 15+ attributes (risk tolerance, time horizon, state, income, etc.)

### 2. **Portfolio Holdings Analysis**

View detailed holdings for filtered accounts:

```python
python scripts/view_holdings.py
```

- Displays positions, quantities, prices, and total values
- Links accounts to their complete portfolio data

### 3. **Intelligent Trade Recommendations**

Generate actionable trade signals based on market conditions:

```python
python scripts/recommend_trades.py
```

- **BUY**: Double position when market condition is positive
- **SELL**: Liquidate entire position when negative
- Fallback to sector conditions when security-specific data unavailable

## 📊 Data Schema

### Input Files

| File                             | Description           | Key Columns                                                    |
| -------------------------------- | --------------------- | -------------------------------------------------------------- |
| `customer_accounts.csv`          | Customer profiles     | Account_ID, Risk_Tolerance, Time_Horizon, State, Annual_Income |
| `customer_accounts_holdings.csv` | Portfolio positions   | AccountID, Ticker, Qty, Price, PositionTotal                   |
| `market_conditions.csv`          | Market sentiment      | Type (Sector/Security), Name, Condition (Positive/Negative)    |
| `Safari55.csv`                   | Security metadata     | Symbol, GICS_Sector, Last_Close_Price                          |
| `rebalance_requests.json`        | Filter configurations | requestIdentifier, accountRebalanceCriterias                   |

### Output Format

```json
{
  "requestIdentifier": "c48cd16f-ed5c-426e-a53e-c214e9136055",
  "accounts": [
    {
      "Account_ID": "f3feaff86948",
      "trades": [
        {
          "Ticker": "AAPL",
          "Qty": 100,
          "Recommended_Trade": "BUY"
        }
      ]
    }
  ]
}
```

## 🔧 Usage Examples

### Basic Workflow

```python
from scripts.filter_accounts import RebalanceFilter

# Initialize system
filter_system = RebalanceFilter()
filter_system.initialize()

# Process specific rebalance request
request_id = "c48cd16f-ed5c-426e-a53e-c214e9136055"
result = filter_system.process_single_request(request_id)

# Generate trade recommendations
# Run: python scripts/recommend_trades.py
# Output saved to: output/trade_recommendations.json
```

### Custom Filtering

```python
from scripts.account_processor import AccountProcessor
from scripts.data_loader import DataLoader

# Load data
loader = DataLoader()
accounts_df = loader.load_customer_accounts()
processor = AccountProcessor(accounts_df)

# Define custom criteria
custom_criteria = [
    {"attribute": "state", "operator": "=", "value": "NY"},
    {"attribute": "annualIncome", "operator": ">", "value": "100000"},
    {"attribute": "riskTolerance", "operator": "!=", "value": "Conservative"}
]

# Apply filters
filtered_df = processor.filter_by_criteria(custom_criteria)
```

## 🏗️ Architecture

The system follows a modular design pattern:

1. **Data Layer** (`data_loader.py`): Handles all file I/O operations
2. **Business Logic** (`account_processor.py`): Core filtering and processing engine
3. **Orchestration** (`filter_accounts.py`): Coordinates components and workflow
4. **Analytics** (`recommend_trades.py`): Generates trading signals based on market data

## 📈 Performance

- Processes 10,000+ accounts in seconds
- Handles complex multi-criteria filtering efficiently
- Generates recommendations for entire portfolios in batch

## 🔐 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
