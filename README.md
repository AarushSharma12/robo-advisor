# Portfolio Trade Recommendation System

An automated Python system that generates actionable buy/sell trade recommendations for customer portfolios based on configurable filtering criteria and real-time market conditions.

## 🎯 Overview

This system automates portfolio rebalancing by:

- Filtering customer accounts based on investment criteria
- Analyzing current holdings against market conditions
- Generating buy/sell recommendations with intelligent sector fallback
- Exporting structured JSON for execution by trading systems

## 📁 Project Structure

```
fidelity-robo/
├── data/
│   ├── api_data/
│   │   └── rebalance_requests.json      # Filter configurations
│   └── market_data/
│       ├── customer_accounts.csv        # Account profiles
│       ├── customer_accounts_holdings.csv   # Portfolio positions
│       ├── market_conditions.csv        # Market sentiment
│       └── Safari55.csv                 # Security-sector mappings
├── scripts/
│   ├── recommend_trades.py             # Main execution script
│   ├── trade_recommender.py            # Core recommendation engine
│   ├── account_processor.py            # Account filtering logic
│   └── data_loader.py                  # Data I/O utilities
├── output/
│   └── trade_recommendations.json      # Generated trade signals
└── requirements.txt
```

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate trade recommendations
python scripts/recommend_trades.py

# Output saved to: output/trade_recommendations.json
```

## 💡 How It Works

1. **Filter Accounts**: Apply multi-criteria filters from JSON configuration
2. **Analyze Holdings**: Load current portfolio positions for filtered accounts
3. **Check Market Conditions**: Evaluate each holding against market sentiment
4. **Generate Trades**:
   - **BUY**: When condition is Positive (double position)
   - **SELL**: When condition is Negative (liquidate position)
   - **Fallback**: Use sector condition if security-specific data unavailable
5. **Export JSON**: Structured output ready for trading system integration

## 📊 Data Flow

```
rebalance_requests.json → Filter Accounts
                              ↓
customer_accounts.csv → Filtered Account IDs
                              ↓
customer_holdings.csv → Current Positions
                              ↓
market_conditions.csv + Safari55.csv → Trade Decisions
                              ↓
                    trade_recommendations.json
```

## 🔧 Configuration

### Filter Criteria (rebalance_requests.json)

```json
{
  "requestIdentifier": "unique-id",
  "accountRebalanceCriterias": [
    { "attribute": "state", "operator": "=", "value": "NY" },
    { "attribute": "riskTolerance", "operator": "!=", "value": "Conservative" }
  ]
}
```

### Supported Operators

- `=` (equals)
- `!=` (not equals)
- `>`, `<`, `>=`, `<=` (numeric comparisons)

### Output Format

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

## 📈 Performance

- Processes 10,000+ accounts in seconds
- Analyzes 500+ securities with sector fallback
- Generates complete portfolio rebalancing in one execution

## 🛠️ Customization

To process a different request, modify the `REQUEST_ID` in `recommend_trades.py`:

```python
REQUEST_ID = "your-request-id-here"
```

## 📋 Requirements

- Python 3.8+
- pandas 2.1.3
- numpy 1.24.3

## 🔐 License

MIT License - see [LICENSE](LICENSE) file
