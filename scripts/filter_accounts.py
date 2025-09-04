import sys
import pandas as pd
from pathlib import Path
from typing import Dict, Optional

sys.path.append(str(Path(__file__).resolve().parent.parent))

from scripts.data_loader import DataLoader
from scripts.account_processor import AccountProcessor


class RebalanceFilter:
    def __init__(self, base_path="."):
        self.loader = DataLoader(base_path)
        self.processor = None
        self.requests = None
        self.accounts_df = None
        self.holdings_df = None

    def initialize(self):
        print("Loading data...")
        self.accounts_df = self.loader.load_customer_accounts()
        self.holdings_df = self.loader.load_customer_holdings()
        self.requests = self.loader.load_rebalance_requests()
        self.processor = AccountProcessor(self.accounts_df)
        print(f"Loaded {len(self.accounts_df)} customer accounts.")
        print(f"Loaded {len(self.requests)} rebalance requests.")

    def process_single_request(self, request_id: str) -> Dict:
        target_request = None
        for request in self.requests:
            if request["requestIdentifier"] == request_id:
                target_request = request
                break

        if not target_request:
            print(f"Request ID '{request_id}' not found.")
            return {"error": "Request ID not found"}

        filtered_df = self.processor.filter_by_criteria(
            target_request["accountRebalanceCriterias"]
        )

        if not filtered_df.empty:
            print(
                f"Filtered accounts for request ID '{request_id}': {len(filtered_df)} matched."
            )

        return {
            "count": len(filtered_df),
            "accounts": filtered_df["Account_ID"].tolist(),
        }

    def process_all_requests(self) -> Dict:
        results = {}

        for request in self.requests:
            request_id = request["requestIdentifier"]
            print(f"Processing request ID: {request_id}")

            result = self.process_single_request(request_id)
            results[request_id] = result

            if "error" not in result:
                print(f"Request ID '{request_id}': {result['count']} accounts matched.")

        return results

    def get_accounts_with_holdings(self, request_id: str) -> Optional[pd.DataFrame]:
        target_request = None

        for request in self.requests:
            if request["requestIdentifier"] == request_id:
                target_request = request
                break

        if not target_request:
            print(f"Request ID '{request_id}' not found.")
            return None

        filtered_accounts = self.processor.filter_by_criteria(
            target_request["accountRebalanceCriterias"]
        )

        return self.processor.merge_with_holdings(filtered_accounts, self.holdings_df)

    def get_holdings_for_accounts(self, request_id: str) -> Dict:
        target_request = None
        for request in self.requests:
            if request["requestIdentifier"] == request_id:
                target_request = request
                break

        if not target_request:
            return {"error": "Request ID not found"}

        filtered_accounts = self.processor.filter_by_criteria(
            target_request["accountRebalanceCriterias"]
        )

        if filtered_accounts.empty:
            return {"error": "No accounts matched the criteria"}

        account_ids = filtered_accounts["Account_ID"].tolist()
        account_holdings = {}

        for account_id in account_ids:
            holdings = self.holdings_df[self.holdings_df["AccountID"] == account_id]
            if not holdings.empty:
                account_holdings[account_id] = {
                    "positions": holdings[
                        ["Ticker", "Qty", "Price", "PositionTotal"]
                    ].to_dict("records"),
                    "total_value": holdings["PositionTotal"].sum(),
                    "position_count": len(holdings),
                }

        result = {
            "request_id": request_id,
            "matched_accounts": len(account_ids),
            "account_holdings": account_holdings,
        }

        return result


def main():
    filter_system = RebalanceFilter()
    filter_system.initialize()

    request_id = "c48cd16f-ed5c-426e-a53e-c214e9136055"
    print(f"\n{'='*50}")
    print(f"Processing Request ID: {request_id}")
    print(f"{'='*50}")

    result = filter_system.process_single_request(request_id)

    if "error" not in result:
        print(f"\nResults:")
        print(f"Total Accounts Matched: {result['count']}")

        if result["count"] > 0:
            print(f"\nFirst 5 Account IDs:")
            for account_id in result["accounts"][:5]:
                print(f"  {account_id}")

        print(f"\n{'='*50}")
        print("Processing all requests...")
        print(f"{'='*50}")

        all_results = filter_system.process_all_requests()

        print(f"\n{'='*50}")
        print("Summary of All Requests:")
        print(f"{'='*50}")

        total_accounts = 0
        for req_id, result in all_results.items():
            if "error" not in result:
                count = result["count"]
                total_accounts += count
                print(f"  {req_id[:8]}... : {count} accounts")

        print(f"\nTotal unique filtered accounts across all requests: {total_accounts}")


if __name__ == "__main__":
    main()
