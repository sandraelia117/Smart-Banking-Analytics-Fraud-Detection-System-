import pandas as pd
from sqlalchemy import text

from db_connection import get_engine

# ==========================
# PostgreSQL Connection
# ==========================
engine = get_engine()

# ==========================
# Read Source Tables
# ==========================
transactions = pd.read_sql(
    "SELECT * FROM transactions",
    engine
)

accounts = pd.read_sql(
    "SELECT * FROM accounts",
    engine
)

# ==========================
# Read Dimension Tables
# ==========================
dim_customer = pd.read_sql(
    "SELECT customerkey, customerid FROM dw.dimcustomer",
    engine
)

dim_account = pd.read_sql(
    "SELECT accountkey, accountid FROM dw.dimaccount",
    engine
)

dim_branch = pd.read_sql(
    "SELECT branchkey, branchid FROM dw.dimbranch",
    engine
)

dim_employee = pd.read_sql(
    "SELECT employeekey, employeeid FROM dw.dimemployee",
    engine
)

dim_date = pd.read_sql(
    "SELECT datekey, fulldate FROM dw.dimdate",
    engine
)

# ==========================
# Prepare Date
# ==========================
transactions["transactiondate"] = pd.to_datetime(
    transactions["transactiondate"]
).dt.normalize()

dim_date["fulldate"] = pd.to_datetime(
    dim_date["fulldate"]
).dt.normalize()

# ==========================
# Build Fact Table
# ==========================
fact = transactions.merge(
    accounts[["accountid", "customerid", "branchid"]],
    on="accountid",
    how="left"
)

fact = fact.merge(
    dim_customer,
    on="customerid",
    how="left"
)

fact = fact.merge(
    dim_account,
    on="accountid",
    how="left"
)

fact = fact.merge(
    dim_branch,
    on="branchid",
    how="left"
)

fact = fact.merge(
    dim_employee,
    on="employeeid",
    how="left"
)

fact = fact.merge(
    dim_date,
    left_on="transactiondate",
    right_on="fulldate",
    how="left"
)

# ==========================
# Measures
# ==========================
fact["transactioncount"] = 1

fact["transactionamount"] = fact["amount"]

fact["depositamount"] = fact.apply(
    lambda x: x["amount"] if x["transactiontype"] == "Deposit" else 0,
    axis=1
)

fact["withdrawalamount"] = fact.apply(
    lambda x: x["amount"] if x["transactiontype"] == "Withdrawal" else 0,
    axis=1
)

fact["transferamount"] = fact.apply(
    lambda x: x["amount"] if x["transactiontype"] == "Transfer" else 0,
    axis=1
)

fact["fraudamount"] = fact.apply(
    lambda x: x["amount"] if x["isfraud"] else 0,
    axis=1
)

# لا يوجد ربط مع القروض
fact["loankey"] = None

# ==========================
# Select DW Columns
# ==========================
fact_dw = fact[[
    "datekey",
    "customerkey",
    "branchkey",
    "accountkey",
    "employeekey",
    "loankey",
    "transactioncount",
    "transactionamount",
    "depositamount",
    "withdrawalamount",
    "transferamount",
    "fraudamount"
]].copy()

# الأعمدة الموجودة في الـ Fact لكنها ليست موجودة في الـ Source
fact_dw["loandisbursementamount"] = 0
fact_dw["loanrepaymentamount"] = 0
fact_dw["interestamount"] = 0
fact_dw["feeamount"] = 0

fact_dw = fact_dw[[
    "datekey",
    "customerkey",
    "branchkey",
    "accountkey",
    "employeekey",
    "loankey",
    "transactioncount",
    "transactionamount",
    "depositamount",
    "withdrawalamount",
    "transferamount",
    "loandisbursementamount",
    "loanrepaymentamount",
    "interestamount",
    "feeamount",
    "fraudamount"
]]

# ==========================
# Check Missing Keys
# ==========================
print("\nMissing Values:")
print(fact_dw[["datekey","customerkey","branchkey","accountkey"]].isnull().sum())

# ==========================
# Remove Invalid Rows
# ==========================
fact_dw = fact_dw.dropna(
    subset=[
        "datekey",
        "customerkey",
        "branchkey",
        "accountkey"
    ]
)

# ==========================
# Load Fact Table
# ==========================
with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE dw.fact_transactions RESTART IDENTITY"))
    fact_dw.to_sql(
        "fact_transactions",
        conn,
        schema="dw",
        if_exists="append",
        index=False
    )

print("\n🎉 Fact_Transactions Loaded Successfully!")
print("Rows Loaded:", len(fact_dw))