import pandas as pd
from typing import Dict, List, Any


class AccountProcessor:
    ATTRIBUTE_MAPPING = {
        "timeHorizon": "Time_Horizon",
        "riskTolerance": "Risk_Tolerance",
        "state": "State",
        "age": "Age",
        "maritalStatus": "Marital_Status",
        "dependents": "Dependents",
        "clientIndustry": "Client_Industry",
        "residencyZip": "Residency_Zip",
        "accountStatus": "Account_Status",
        "annualIncome": "Annual_Income",
        "liquidityNeeds": "Liquidity_Needs",
        "investmentExperience": "Investment_Experience",
        "investmentGoals": "Investment_Goals",
        "exclusions": "Exclusions",
        "sriPreferences": "SRI_Preferences",
        "taxStatus": "Tax_Status",
        "accountId": "Account_ID",
    }

    def __init__(self, accounts_df: pd.DataFrame):
        self.accounts_df = accounts_df
        self.original_df = accounts_df.copy()

    def map_attribute(self, attribute: str) -> str:
        return self.ATTRIBUTE_MAPPING.get(attribute, attribute)

    def apply_single_criteria(
        self, df: pd.DataFrame, criteria: Dict[str, Any]
    ) -> pd.DataFrame:
        column = self.map_attribute(criteria["attribute"])
        operator = criteria["operator"]
        value = criteria["value"]

        if column not in df.columns:
            print(f"Warning: Column '{column}' not found in DataFrame.")
            return df

        if operator == "=":
            return df[df[column] == value]
        elif operator == "!=":
            return df[df[column] != value]
        elif operator == ">":
            return df[df[column] > float(value)]
        elif operator == "<":
            return df[df[column] < float(value)]
        elif operator == ">=":
            return df[df[column] >= float(value)]
        elif operator == "<=":
            return df[df[column] <= float(value)]
        elif operator == "in":
            if isinstance(value, list):
                return df[df[column].isin(value)]
            else:
                return df[df[column] == value]
        elif operator == "not in":
            if isinstance(value, list):
                return df[~df[column].isin(value)]
            else:
                return df[df[column] != value]
        else:
            print(f"Warning: Unsupported operator '{operator}'.")
            return df

    def filter_by_criteria(self, criterias: List[Dict[str, Any]]) -> pd.DataFrame:
        filtered_df = self.accounts_df.copy()

        for criteria in criterias:
            filtered_df = self.apply_single_criteria(filtered_df, criteria)
            if filtered_df.empty:
                break

        return filtered_df

    def get_account_summary(self, df: pd.DataFrame) -> Dict:
        if df.empty:
            return {"count": 0, "accounts": []}

        summary = {
            "count": len(df),
            "accounts": df["Account_ID"].tolist(),
            "statistics": {
                "avg_age": df["Age"].mean() if "Age" in df.columns else None,
                "avg_annual_income": (
                    df["Annual_Income"].mean()
                    if "Annual_Income" in df.columns
                    else None
                ),
                "risk_distribution": (
                    df["Risk_Tolerance"].value_counts().to_dict()
                    if "Risk_Tolerance" in df.columns
                    else {}
                ),
                "state_distribution": (
                    df["State"].value_counts().to_dict()
                    if "State" in df.columns
                    else {}
                ),
                "time_horizon_distribution": (
                    df["Time_Horizon"].value_counts().to_dict()
                    if "Time_Horizon" in df.columns
                    else {}
                ),
            },
        }
        return summary

    def merge_with_holdings(
        self, accounts_df: pd.DataFrame, holdings_df: pd.DataFrame
    ) -> pd.DataFrame:
        return pd.merge(accounts_df, holdings_df, on="Account_ID", how="left")

    def reset_filters(self):
        self.accounts_df = self.original_df.copy()
