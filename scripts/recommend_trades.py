"""Script to recommend buy/sell based on market conditions."""

import pandas as pd
import json

# Load data
accounts_df = pd.read_csv("data/market_data/customer_accounts.csv")
holdings_df = pd.read_csv("data/market_data/customer_accounts_holdings.csv")
market_df = pd.read_csv("data/market_data/market_conditions.csv")
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
market_conditions = {}
for _, row in market_df.iterrows():
    if row["Type"] == "Security":
        market_conditions[row["Name"]] = row["Condition"]

# Show holdings with buy/sell recommendations
for account_id in filtered["Account_ID"]:
    account_holdings = holdings_df[holdings_df["AccountID"] == account_id]
    print(f"\nAccount: {account_id}")
    if not account_holdings.empty:
        for _, row in account_holdings.iterrows():
            ticker = row["Ticker"]
            condition = market_conditions.get(ticker, "Unknown")
            action = (
                "SELL"
                if condition == "Negative"
                else "HOLD" if condition == "Positive" else "NO DATA"
            )
            print(
                f"  {ticker} - {row['Qty']} shares @ ${row['Price']} = ${row['PositionTotal']} -> {action}"
            )
    else:
        print("  No holdings")
