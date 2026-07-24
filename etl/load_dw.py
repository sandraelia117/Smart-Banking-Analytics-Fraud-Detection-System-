import pandas as pd
from sqlalchemy import text

from db_connection import get_engine

# ==========================================
# PostgreSQL Connection
# ==========================================
engine = get_engine()
with engine.begin() as conn:
    conn.execute(text("""
        TRUNCATE TABLE
            dw.fact_transactions,
            dw.dimcustomer,
            dw.dimbranch,
            dw.dimaccount,
            dw.dimemployee,
            dw.dimloan,
            dw.dimdate
        RESTART IDENTITY CASCADE;
    """))
# ==========================================
# Read Source Tables
# ==========================================
customers = pd.read_sql("SELECT * FROM customers", engine)
branches = pd.read_sql("SELECT * FROM branches", engine)
accounts = pd.read_sql("SELECT * FROM accounts", engine)
employees = pd.read_sql("SELECT * FROM employees", engine)
loans = pd.read_sql("SELECT * FROM loans", engine)
transactions = pd.read_sql("SELECT transactiondate FROM transactions", engine)

# ==========================================
# DimCustomer
# ==========================================
dim_customer = customers[[
    "customerid",
    "firstname",
    "lastname",
    "dateofbirth",
    "gender",
    "email",
    "phone",
    "address",
    "city",
    "joindate"
]]

dim_customer.to_sql(
    "dimcustomer",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("✅ DimCustomer Loaded")

# ==========================================
# DimBranch
# ==========================================
dim_branch = branches[[
    "branchid",
    "branchname",
    "city",
    "region"
]].copy()

dim_branch["managername"] = None
dim_branch["openingdate"] = None

dim_branch = dim_branch[[
    "branchid",
    "branchname",
    "city",
    "region",
    "managername",
    "openingdate"
]]

dim_branch.to_sql(
    "dimbranch",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("✅ DimBranch Loaded")

# ==========================================
# DimAccount
# ==========================================
dim_account = accounts[[
    "accountid",
    "accountnumber",
    "accounttype",
    "opendate",
    "status"
]]

dim_account.to_sql(
    "dimaccount",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("✅ DimAccount Loaded")

# ==========================================
# DimEmployee
# ==========================================
dim_employee = employees[[
    "employeeid",
    "firstname",
    "lastname",
    "position",
    "hiredate"
]].copy()

dim_employee["status"] = "Active"

dim_employee = dim_employee[[
    "employeeid",
    "firstname",
    "lastname",
    "position",
    "hiredate",
    "status"
]]

dim_employee.to_sql(
    "dimemployee",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("✅ DimEmployee Loaded")

# ==========================================
# DimLoan
# ==========================================
dim_loan = loans[[
    "loanid",
    "loantype",
    "amount",
    "interestrate",
    "termmonths",
    "status"
]].copy()


def amount_range(x):
    if x < 50000:
        return "Low"
    elif x < 100000:
        return "Medium"
    else:
        return "High"


dim_loan["amountrange"] = dim_loan["amount"].apply(amount_range)

dim_loan = dim_loan[[
    "loanid",
    "loantype",
    "amountrange",
    "interestrate",
    "termmonths",
    "status"
]]

dim_loan.to_sql(
    "dimloan",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("✅ DimLoan Loaded")

# ==========================================
# DimDate
# ==========================================
dim_date = pd.DataFrame()

dim_date["fulldate"] = (
    pd.to_datetime(transactions["transactiondate"])
    .dt.normalize()
    .drop_duplicates()
    .sort_values()
    .reset_index(drop=True)
)

dim_date["datekey"] = dim_date["fulldate"].dt.strftime("%Y%m%d").astype(int)
dim_date["day"] = dim_date["fulldate"].dt.day
dim_date["dayname"] = dim_date["fulldate"].dt.day_name()
dim_date["week"] = dim_date["fulldate"].dt.isocalendar().week.astype(int)
dim_date["month"] = dim_date["fulldate"].dt.month
dim_date["monthname"] = dim_date["fulldate"].dt.month_name()
dim_date["quarter"] = dim_date["fulldate"].dt.quarter
dim_date["year"] = dim_date["fulldate"].dt.year
dim_date["isweekend"] = dim_date["fulldate"].dt.dayofweek >= 5
dim_date["isholiday"] = False

dim_date = dim_date[[
    "datekey",
    "fulldate",
    "day",
    "dayname",
    "week",
    "month",
    "monthname",
    "quarter",
    "year",
    "isweekend",
    "isholiday"
]]

dim_date.to_sql(
    "dimdate",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("✅ DimDate Loaded")

print("\n🎉 All Dimension Tables Loaded Successfully!")