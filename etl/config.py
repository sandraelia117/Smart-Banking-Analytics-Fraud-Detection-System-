from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# CSV files
CSV_FILES = {
    "branches": "branches.csv",
    "customers": "customers.csv",
    "employees": "employees.csv",
    "accounts": "accounts.csv",
    "atms": "atms.csv",
    "loans": "loans.csv",
    "creditcards": "creditcards.csv",
    "beneficiaries": "beneficiaries.csv",
    "mobilebanking": "mobilebanking.csv",
    "transactions": "transactions.csv",
}

# Primary Keys
PRIMARY_KEYS = {
    "branches": "branchid",
    "customers": "customerid",
    "employees": "employeeid",
    "accounts": "accountid",
    "atms": "atmid",
    "loans": "loanid",
    "creditcards": "cardid",
    "beneficiaries": "beneficiaryid",
    "mobilebanking": "mobileid",
    "transactions": "transactionid",
}

# Foreign Keys
FOREIGN_KEYS = {
    "employees": {"branchid": "branches"},
    "accounts": {
        "customerid": "customers",
        "branchid": "branches"
    },
    "atms": {"branchid": "branches"},
    "loans": {
        "customerid": "customers",
        "employeeid": "employees"
    },
    "creditcards": {"customerid": "customers"},
    "beneficiaries": {"customerid": "customers"},
    "mobilebanking": {"customerid": "customers"},
    "transactions": {
        "accountid": "accounts",
        "atmid": "atms",
        "employeeid": "employees",
    },
}

NULLABLE_FOREIGN_KEYS = {
    "transactions": {"atmid", "employeeid"},
    "loans": {"employeeid"},
}

SOURCE_TABLE_LOAD_ORDER = [
    "branches",
    "customers",
    "employees",
    "accounts",
    "atms",
    "loans",
    "creditcards",
    "beneficiaries",
    "mobilebanking",
    "transactions",
]

DATE_COLUMNS = {
    "customers": ["dateofbirth", "joindate"],
    "employees": ["hiredate"],
    "accounts": ["opendate"],
    "loans": ["enddate"],
    "creditcards": ["issuedate", "expirydate"],
    "mobilebanking": ["registereddate"],
    "transactions": ["transactiondate"],
}
import logging

def setup_logging(log_filename="etl_pipeline.log"):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )