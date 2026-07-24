import pandas as pd

from db_connection import get_engine

engine = get_engine()

DATA_PATH = "../cleaned_data/"

tables = {
    "Branches": "branches",
    "Customers": "customers",
    "Employees": "employees",
    "Accounts": "accounts",
    "ATMs": "atms",
    "Loans": "loans",
    "CreditCards": "creditcards",
    "Beneficiaries": "beneficiaries",
    "MobileBanking": "mobilebanking",
    "Transactions": "transactions",
}

for file_name, table_name in tables.items():
    print(f"Loading {file_name}.csv ...")

    df = pd.read_csv(f"{DATA_PATH}{file_name}.csv")

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False
    )

    print(f"✅ {table_name} loaded successfully ({len(df)} rows)")

print("\n🎉 All tables loaded successfully!")