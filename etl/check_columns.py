import pandas as pd

DATA_PATH = "../cleaned_data/"

files = [
    "Customers",
    "Branches",
    "Accounts",
    "Employees",
    "Loans",
    "Transactions"
]

for file in files:
    df = pd.read_csv(f"{DATA_PATH}{file}.csv")
    print(f"\n===== {file} =====")
    print(df.columns.tolist())