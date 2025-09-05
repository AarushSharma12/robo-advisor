"""Generate trade recommendations and export to JSON."""

import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent.parent))

from scripts.trade_recommender import TradeRecommender
from scripts.data_loader import DataLoader


def main():
    """Generate trade recommendations for a specific request."""

    print("Initializing trade recommender...")
    recommender = TradeRecommender()
    recommender.initialize()

    print(f"\nFound {len(recommender.requests)} rebalance requests to process")
    print("=" * 50)

    total_accounts = 0
    all_recommendations = []

    for request in recommender.requests:
        request_id = request["requestIdentifier"]
        recommendations = recommender.generate_recommendations(request_id)

        if recommendations:
            all_recommendations.append(recommendations)
            account_count = len(recommendations["accounts"])
            total_accounts += account_count

            # Save individual file for each request

    if all_recommendations:
        combined_output = {
            "total_requests": len(recommender.requests),
            "total_accounts_with_trades": total_accounts,
            "recommendations": all_recommendations,
        }

        loader = DataLoader()
        output_file = loader.save_json(
            combined_output, "all_trade_recommendations.json"
        )

        print("\n" + "=" * 50)
        print(f"📁 Individual files saved for each request")
        print(f"📁 Combined file: all_trade_recommendations.json")
        print(
            f"📊 Total: {total_accounts} accounts across {len(all_recommendations)} requests"
        )


if __name__ == "__main__":
    main()
