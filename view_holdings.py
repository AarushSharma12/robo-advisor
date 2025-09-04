"""Simple script to view holdings for filtered accounts."""

import pandas as pd
import json

# Load data
accounts_df = pd.read_csv("data/market_data/customer_accounts.csv")
holdings_df = pd.read_csv("data/market_data/customer_accounts_holdings.csv")
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

# Show holdings for each filtered account
for account_id in filtered["Account_ID"]:
    account_holdings = holdings_df[holdings_df["AccountID"] == account_id]
    print(f"\nAccount: {account_id}")
    if not account_holdings.empty:
        for _, row in account_holdings.iterrows():
            print(
                f"  {row['Ticker']} - {row['Qty']} shares @ ${row['Price']} = ${row['PositionTotal']}"
            )
    else:
        print("  No holdings")
