"""Generate trade recommendations based on account criteria and market conditions."""

import pandas as pd
import json

# Load data
accounts_df = pd.read_csv("data/market_data/customer_accounts.csv")
holdings_df = pd.read_csv("data/market_data/customer_accounts_holdings.csv")
market_df = pd.read_csv("data/market_data/market_conditions.csv")
safari_df = pd.read_csv("data/market_data/Safari55.csv")

with open("data/api_data/rebalance_requests.json", "r") as f:
    requests = json.load(f)

# Find and apply filters for a specific request
request_id = "c48cd16f-ed5c-426e-a53e-c214e9136055"
request = next((r for r in requests if r["requestIdentifier"] == request_id), None)

# Apply filters
filtered = accounts_df.copy()
for criteria in request["accountRebalanceCriterias"]:
    col = (
        criteria["attribute"]
        .replace("timeHorizon", "Time_Horizon")
        .replace("riskTolerance", "Risk_Tolerance")
        .replace("state", "State")
    )
    if criteria["operator"] == "=":
        filtered = filtered[filtered[col] == criteria["value"]]
    elif criteria["operator"] == "!=":
        filtered = filtered[filtered[col] != criteria["value"]]

# Create lookup for market conditions
security_conditions = {}
sector_conditions = {}
for _, row in market_df.iterrows():
    if row["Type"] == "Security":
        security_conditions[row["Name"]] = row["Condition"]
    elif row["Type"] == "Sector":
        sector_conditions[row["Name"]] = row["Condition"]

# Create ticker to sector mapping
ticker_to_sector = {}
for _, row in safari_df.iterrows():
    ticker_to_sector[row["Symbol"]] = row["GICS_Sector"]

#  Generate trade recommendations
recommendations = {}

for account_id in filtered["Account_ID"]:
    account_holdings = holdings_df[holdings_df["AccountID"] == account_id]
    account_trades = []

    for _, row in account_holdings.iterrows():
        ticker = row["Ticker"]
        current_qty = row["Qty"]
        # Check secuirty condition first
        condition = sector_conditions.get(ticker)
        if not condition and ticker in ticker_to_sector:
            sector = ticker_to_sector[ticker]
            condition = sector_conditions.get(sector)

        # Determine trade
        if condition == "Positive":
            trade_action = "BUY"
            trade_qty = current_qty
            account_trades.append(
                {
                    "Ticker": ticker,
                    "Qty": int(trade_qty),
                    "Recommended_Trade": trade_action,
                }
            )
        elif condition == "Negative":
            trade_action = "SELL"
            trade_qty = current_qty
            account_trades.append(
                {
                    "Ticker": ticker,
                    "Qty": int(trade_qty),
                    "Recommended_Trade": trade_action,
                }
            )

    recommendations[account_id] = account_trades

with open("output/recommendations.json", "w") as f:
    json.dump(recommendations, f, indent=2)

print(f"Trade recommendations saved to output/trade_recommendations.json")
print(f"\nSample output for first account:")
first_account = list(recommendations.keys())[0] if recommendations else None
if first_account:
    print(json.dumps({first_account: recommendations[first_account]}, indent=2))
