"""Data loading utilities for portfolio rebalancing system."""

import pandas as pd
import json
from pathlib import Path


class DataLoader:
    """Handles loading of CSV and JSON files."""

    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.api_path = self.base_path / "data" / "api_data"
        self.market_path = self.base_path / "data" / "market_data"

    def load_customer_accounts(self):
        """Load customer accounts CSV."""
        return pd.read_csv(self.market_path / "customer_accounts.csv")

    def load_customer_holdings(self):
        """Load customer holdings CSV."""
        return pd.read_csv(self.market_path / "customer_accounts_holdings.csv")

    def load_rebalance_requests(self):
        """Load rebalance requests JSON."""
        with open(self.api_path / "rebalance_requests.json", "r") as f:
            return json.load(f)

    def load_market_conditions(self):
        """Load market conditions CSV."""
        return pd.read_csv(self.market_path / "market_conditions.csv")

    def load_safari55(self):
        """Load Safari55 security metadata CSV."""
        return pd.read_csv(self.market_path / "Safari55.csv")

    def save_json(self, data, filename):
        """Save data to JSON in output directory."""
        output_path = self.base_path / "output"
        output_path.mkdir(exist_ok=True)

        with open(output_path / filename, "w") as f:
            json.dump(data, f, indent=2)

        return output_path / filename
