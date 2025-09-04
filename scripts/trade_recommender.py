"""Trade recommendation generator for portfolio rebalancing."""

from .data_loader import DataLoader
from .account_processor import AccountProcessor


class TradeRecommender:
    """Generates trade recommendations based on market conditions."""

    def __init__(self):
        self.loader = DataLoader()
        self.accounts_df = None
        self.holdings_df = None
        self.market_df = None
        self.safari_df = None
        self.requests = None

    def initialize(self):
        """Load all necessary data."""
        self.accounts_df = self.loader.load_customer_accounts()
        self.holdings_df = self.loader.load_customer_holdings()
        self.market_df = self.loader.load_market_conditions()
        self.safari_df = self.loader.load_safari55()
        self.requests = self.loader.load_rebalance_requests()

    def get_filtered_accounts(self, request_id):
        """Get accounts that match the request criteria."""
        # Find the request
        request = next(
            (r for r in self.requests if r["requestIdentifier"] == request_id), None
        )
        if not request:
            return None

        # Apply filters
        processor = AccountProcessor(self.accounts_df)
        return processor.filter_by_criteria(request["accountRebalanceCriterias"])

    def build_market_lookups(self):
        """Create lookups for market conditions and sectors."""
        security_conditions = {}
        sector_conditions = {}

        for _, row in self.market_df.iterrows():
            if row["Type"] == "Security":
                security_conditions[row["Name"]] = row["Condition"]
            elif row["Type"] == "Sector":
                sector_conditions[row["Name"]] = row["Condition"]

        ticker_to_sector = {}
        for _, row in self.safari_df.iterrows():
            ticker_to_sector[row["Symbol"]] = row["GICS_Sector"]

        return security_conditions, sector_conditions, ticker_to_sector

    def get_trade_action(
        self, ticker, security_conditions, sector_conditions, ticker_to_sector
    ):
        """Determine trade action for a ticker based on market conditions."""
        condition = security_conditions.get(ticker)

        # Fallback to sector condition
        if not condition and ticker in ticker_to_sector:
            sector = ticker_to_sector[ticker]
            condition = sector_conditions.get(sector)

        if condition == "Positive":
            return "BUY"
        elif condition == "Negative":
            return "SELL"
        else:
            return "HOLD"

    def generate_recommendations(self, request_id):
        """Generate trade recommendations for a request."""
        # Get filtered accounts
        filtered_accounts = self.get_filtered_accounts(request_id)
        if filtered_accounts is None or filtered_accounts.empty:
            return None

        # Build market lookups
        security_conditions, sector_conditions, ticker_to_sector = (
            self.build_market_lookups()
        )

        # Generate recommendations for each account
        accounts_list = []

        for account_id in filtered_accounts["Account_ID"]:
            account_holdings = self.holdings_df[
                self.holdings_df["AccountID"] == account_id
            ]
            account_trades = []

            for _, row in account_holdings.iterrows():
                ticker = row["Ticker"]
                current_qty = row["Qty"]

                trade_action = self.get_trade_action(
                    ticker, security_conditions, sector_conditions, ticker_to_sector
                )

                if trade_action != "HOLD":
                    account_trades.append(
                        {
                            "Ticker": ticker,
                            "Qty": int(current_qty),
                            "Recommended_Trade": trade_action,
                        }
                    )

            if account_trades:
                accounts_list.append(
                    {"Account_ID": account_id, "trades": account_trades}
                )

        return {"requestIdentifier": request_id, "accounts": accounts_list}
