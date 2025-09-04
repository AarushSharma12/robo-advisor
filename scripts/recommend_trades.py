"""Generate trade recommendations and export to JSON."""

import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent.parent))

from scripts.trade_recommender import TradeRecommender
from scripts.data_loader import DataLoader


def main():
    """Generate trade recommendations for a specific request."""

    # Example Request ID to process
    REQUEST_ID = "c48cd16f-ed5c-426e-a53e-c214e9136055"

    # Initialize the recommender
    print("Initializing trade recommender...")
    recommender = TradeRecommender()
    recommender.initialize()

    # Generate recommendations
    print(f"Generating recommendations for request: {REQUEST_ID[:8]}...")
    recommendations = recommender.generate_recommendations(REQUEST_ID)

    if recommendations is None:
        print(
            "Error: Could not generate recommendations (request not found or no matches)"
        )
        return

    # Save to JSON
    loader = DataLoader()
    output_file = loader.save_json(recommendations, "trade_recommendations.json")


if __name__ == "__main__":
    main()
