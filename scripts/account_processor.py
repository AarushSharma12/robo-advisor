"""Account filtering engine for processing rebalance criteria."""

import pandas as pd
from typing import Dict, List, Any


class AccountProcessor:
    """Handles filtering of customer accounts based on criteria."""

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

    def map_attribute(self, attribute: str) -> str:
        """Map JSON attribute name to CSV column name."""
        return self.ATTRIBUTE_MAPPING.get(attribute, attribute)

    def apply_single_criteria(
        self, df: pd.DataFrame, criteria: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply a single filter criteria to DataFrame."""
        column = self.map_attribute(criteria["attribute"])
        operator = criteria["operator"]
        value = criteria["value"]

        if column not in df.columns:
            return df

        if operator == "=":
            return df[df[column] == value]
        elif operator == "!=":
            return df[df[column] != value]
        elif operator == ">":
            return df[pd.to_numeric(df[column], errors="coerce") > float(value)]
        elif operator == "<":
            return df[pd.to_numeric(df[column], errors="coerce") < float(value)]
        elif operator == ">=":
            return df[pd.to_numeric(df[column], errors="coerce") >= float(value)]
        elif operator == "<=":
            return df[pd.to_numeric(df[column], errors="coerce") <= float(value)]
        else:
            return df

    def filter_by_criteria(self, criterias: List[Dict[str, Any]]) -> pd.DataFrame:
        """Apply multiple filter criteria."""
        filtered_df = self.accounts_df.copy()

        for criteria in criterias:
            filtered_df = self.apply_single_criteria(filtered_df, criteria)
            if filtered_df.empty:
                break

        return filtered_df
