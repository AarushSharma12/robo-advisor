import pandas as pd
import json
from pathlib import Path


class DataLoader:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data"
        self.api_data_path = self.data_path / "api_data"
        self.market_data_path = self.data_path / "market_data"

    def load_customer_accounts(self):
        file_path = self.market_data_path / "customer_accounts.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")
        return pd.read_csv(file_path)

    def load_customer_holdings(self):
        file_path = self.market_data_path / "customer_accounts_holdings.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")
        return pd.read_csv(file_path)

    def load_rebalance_requests(self):
        file_path = self.api_data_path / "rebalance_requests.json"
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")
        with open(file_path, "r") as file:
            return json.load(file)

    def load_robo_advisor_config(self):
        file_path = self.api_data_path / "robo_advisor.json"
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")
        with open(file_path, "r") as file:
            return json.load(file)

    def load_market_conditions(self):
        file_path = self.market_data_path / "market_conditions.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")
        return pd.read_csv(file_path)

    def load_safari55(self):
        file_path = self.market_data_path / "Safari55.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")
        return pd.read_csv(file_path)

    def save_results(self, df, filename, subfolder=None):
        output_path = self.base_path / "output"
        if subfolder:
            output_path = output_path / subfolder
        output_path.mkdir(parents=True, exist_ok=True)

        file_path = output_path / filename
        df.to_csv(file_path, index=False)
        return file_path
