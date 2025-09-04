"""Example usage of the rebalance filtering system."""

from scripts.filter_accounts import RebalanceFilter
from scripts.data_loader import DataLoader
from scripts.account_processor import AccountProcessor


# Example 1: Process a single request
def example_single_request():
    """Process one specific rebalance request."""
    filter_system = RebalanceFilter()
    filter_system.initialize()

    request_id = "c48cd16f-ed5c-426e-a53e-c214e9136055"
    result = filter_system.process_single_request(request_id)

    print(f"Found {result['count']} accounts matching criteria")
    return result


# Example 2: Process all requests
def example_all_requests():
    """Process all rebalance requests at once."""
    filter_system = RebalanceFilter()
    filter_system.initialize()

    results = filter_system.process_all_requests(save_outputs=True)

    for req_id, result in results.items():
        print(f"{req_id}: {result['count']} matches")

    return results


# Example 3: Custom filtering without request JSON
def example_custom_filter():
    """Apply custom filter criteria directly."""
    loader = DataLoader()
    accounts_df = loader.load_customer_accounts()
    processor = AccountProcessor(accounts_df)

    # Define custom criteria
    custom_criteria = [
        {"attribute": "state", "operator": "=", "value": "NY"},
        {"attribute": "riskTolerance", "operator": "!=", "value": "Conservative"},
        {"attribute": "annualIncome", "operator": ">", "value": "100000"},
    ]

    filtered_df = processor.filter_by_criteria(custom_criteria)
    summary = processor.get_account_summary(filtered_df)

    print(f"Custom filter found {summary['count']} accounts")
    return filtered_df


if __name__ == "__main__":
    print("Running Example 1: Single Request")
    print("-" * 40)
    example_single_request()

    print("\n\nRunning Example 2: All Requests")
    print("-" * 40)
    example_all_requests()

    print("\n\nRunning Example 3: Custom Filter")
    print("-" * 40)
    example_custom_filter()
