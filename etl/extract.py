import pandas as pd
from pathlib import Path

# Path to the data folder
DATA_PATH = Path(__file__).resolve().parent.parent / "data"


def extract_all_csv_files():
    """
    Read all CSV files from the data folder and return them
    as a dictionary of DataFrames.
    """

    tables = {
    "accounts": pd.read_csv(DATA_PATH / "Accounts.csv"),
    "atms": pd.read_csv(DATA_PATH / "ATMs.csv"),
    "beneficiaries": pd.read_csv(DATA_PATH / "Beneficiaries.csv"),
    "branches": pd.read_csv(DATA_PATH / "Branches.csv"),
    "creditcards": pd.read_csv(DATA_PATH / "CreditCards.csv"),
    "customers": pd.read_csv(DATA_PATH / "Customers.csv"),
    "employees": pd.read_csv(DATA_PATH / "Employees.csv"),
    "loans": pd.read_csv(DATA_PATH / "Loans.csv"),
    "mobilebanking": pd.read_csv(DATA_PATH / "MobileBanking.csv"),
    "transactions": pd.read_csv(DATA_PATH / "Transactions.csv"),
}

    return tables


if __name__ == "__main__":
    tables = extract_all_csv_files()

    for name, df in tables.items():
        print(f"{name}: {df.shape[0]} rows, {df.shape[1]} columns")