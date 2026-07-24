import logging

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


logger = logging.getLogger(__name__)


def run_quality_checks(tables: dict) -> bool:
    """
    Run data quality checks on transformed tables.
    Returns True if all checks pass.
    """

    logger.info("Starting data quality checks...")

    all_passed = True

    for table_name, df in tables.items():

        logger.info(f"Checking {table_name}")

        # -----------------------------
        # Missing Values
        # -----------------------------
        missing = df.isnull().sum().sum()

        if missing > 0:
            logger.error(f"[{table_name}] Missing values: {missing}")
            all_passed = False
        else:
            logger.info(f"[{table_name}] Missing values: PASS")

        # -----------------------------
        # Duplicate Rows
        # -----------------------------
        duplicates = df.duplicated().sum()

        if duplicates > 0:
            logger.error(f"[{table_name}] Duplicate rows: {duplicates}")
            all_passed = False
        else:
            logger.info(f"[{table_name}] Duplicate rows: PASS")

        # -----------------------------
        # Primary Key
        # -----------------------------
        pk = PRIMARY_KEYS.get(table_name)

        if pk and pk in df.columns:

            duplicated_pk = df[pk].duplicated().sum()

            if duplicated_pk > 0:
                logger.error(
                    f"[{table_name}] Duplicate Primary Keys: {duplicated_pk}"
                )
                all_passed = False
            else:
                logger.info(f"[{table_name}] Primary Key: PASS")

    if all_passed:
        logger.info("All quality checks passed.")
    else:
        logger.error("Quality checks failed.")

    return all_passed


if __name__ == "__main__":

    import config
    import extract
    import transform

    config.setup_logging()

    raw_tables = extract.extract_all_csv_files()

    transformed_tables = transform.transform_all_tables(raw_tables)

    result = run_quality_checks(transformed_tables)

    print("\n" + "=" * 50)
    print("QUALITY CHECK RESULT")
    print("=" * 50)

    if result:
        print("PASS")
    else:
        print("FAIL")