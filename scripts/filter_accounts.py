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

    def process_single_request(self, request_id: str, save_output: bool = True) -> Dict:
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

        summary = self.processor.get_account_summary(filtered_df)

        if save_output and not filtered_df.empty:
            filename = f"filtered_accounts_{request_id[:8]}.csv"
            output_path = self.loader.save_results(filtered_df, filename)
            summary["output_file"] = str(output_path)

        return summary

    def process_all_requests(self, save_outputs: bool = True) -> Dict:
        results = {}

        for request in self.requests:
            request_id = request["requestIdentifier"]
            print(f"Processing request ID: {request_id}")

            result = self.process_single_request(request_id, save_outputs)
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
            print(f"\n Risk Tolerance Distribution:")
            for risk, count in result["statistics"]["risk_distribution"].items():
                print(f"  {risk}: {count}")

            print(f"\n First 5 Account IDs:")
            for account_id in result["accounts"][:5]:
                print(f"  {account_id}")

            if "output_file" in result:
                print(f"\nFiltered accounts saved to: {result['output_file']}")

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
