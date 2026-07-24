"""
transform.py

Transformation layer for the Smart Banking ETL pipeline.
Cleans, standardizes, and validates each source DataFrame produced by
extract.py, using the schema definitions centralized in config.py.
No invented business rules or default values are applied beyond what
creat_db.sql itself defines (NOT NULL, PRIMARY KEY, FOREIGN KEY).
"""

import logging
from pathlib import Path

import pandas as pd

import config

logger = logging.getLogger(__name__)

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "cleaned_data"


# ---------------------------------------------------------------------------
# Column / value normalization
# ---------------------------------------------------------------------------
def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and lowercase all column names for consistency."""
    df = df.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]
    return df


def trim_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from all object (string) columns."""
    df = df.copy()
    string_cols = df.select_dtypes(include="object").columns
    for col in string_cols:
        df[col] = df[col].str.strip()
    return df


def normalize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Convert empty strings / whitespace-only strings to real NaN values."""
    df = df.copy()
    string_cols = df.select_dtypes(include="object").columns
    for col in string_cols:
        df[col] = df[col].replace(r"^\s*$", pd.NA, regex=True)
    return df


# ---------------------------------------------------------------------------
# Duplicate handling
# ---------------------------------------------------------------------------
def remove_duplicate_rows(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Drop exact full-row duplicates, keeping the first occurrence."""
    before = len(df)
    df = df.drop_duplicates(keep="first").copy()
    dropped = before - len(df)
    if dropped:
        logger.warning("[%s] Dropped %d fully duplicate row(s)", table_name, dropped)
    return df


def remove_duplicate_primary_keys(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Drop rows with a duplicate primary key, keeping the first occurrence."""
    pk_col = config.PRIMARY_KEYS.get(table_name)
    if pk_col is None or pk_col not in df.columns:
        return df

    before = len(df)
    df = df.drop_duplicates(subset=[pk_col], keep="first").copy()
    dropped = before - len(df)
    if dropped:
        logger.warning(
            "[%s] Dropped %d row(s) with duplicate primary key '%s'",
            table_name, dropped, pk_col,
        )
    return df


# ---------------------------------------------------------------------------
# Type conversion
# ---------------------------------------------------------------------------
def convert_date_columns(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Parse date and timestamp columns using config.DATE_COLUMNS."""
    df = df.copy()
    date_cols = config.DATE_COLUMNS.get(table_name, [])

    for col in date_cols:
        if col not in df.columns:
            continue
        parsed = pd.to_datetime(df[col], errors="coerce")
        invalid = parsed.isna() & df[col].notna()
        if invalid.any():
            logger.warning(
                "[%s] %d value(s) in '%s' could not be parsed as a date and were set to NULL",
                table_name, invalid.sum(), col,
            )
        df[col] = parsed
    return df


def convert_id_columns(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Cast primary/foreign key columns to pandas nullable Int64.

    Nullable Int64 (not plain int64) is required because rows with a
    missing key must survive as NaN through validation, then get
    dropped explicitly by validate_primary_key / validate_foreign_keys
    rather than crashing the cast itself.
    """
    df = df.copy()
    id_columns = set()

    if table_name in config.PRIMARY_KEYS:
        id_columns.add(config.PRIMARY_KEYS[table_name])
    if table_name in config.FOREIGN_KEYS:
        id_columns.update(config.FOREIGN_KEYS[table_name].keys())

    for col in id_columns:
        if col not in df.columns:
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df


# ---------------------------------------------------------------------------
# Key validation
# ---------------------------------------------------------------------------
def validate_primary_key(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Drop rows where the primary key is missing (NULL PKs are unloadable)."""
    pk_col = config.PRIMARY_KEYS.get(table_name)
    if pk_col is None or pk_col not in df.columns:
        return df

    before = len(df)
    df = df[df[pk_col].notna()].copy()
    dropped = before - len(df)
    if dropped:
        logger.warning(
            "[%s] Dropped %d row(s) with missing primary key '%s'",
            table_name, dropped, pk_col,
        )
    return df


def validate_foreign_keys(
    df: pd.DataFrame,
    table_name: str,
    valid_keys_registry: dict[str, set],
) -> pd.DataFrame:
    """
    Validate every foreign key column against already-cleaned parent
    primary keys in valid_keys_registry. Rows referencing a non-existent
    parent are dropped (they would violate the FK constraint on load).
    Nullable FK columns (config.NULLABLE_FOREIGN_KEYS) allow NULL values
    without being flagged as orphans.
    """
    fk_map = config.FOREIGN_KEYS.get(table_name, {})
    nullable_fks = config.NULLABLE_FOREIGN_KEYS.get(table_name, set())

    for fk_col, parent_table in fk_map.items():
        if fk_col not in df.columns:
            continue

        valid_parent_keys = valid_keys_registry.get(parent_table, set())

        is_null = df[fk_col].isna()
        is_orphan = ~df[fk_col].isin(valid_parent_keys) & ~is_null

        if fk_col in nullable_fks:
            rows_to_drop = is_orphan  # NULLs are allowed, only true orphans dropped
        else:
            rows_to_drop = is_orphan | is_null  # NOT NULL FK: missing is also invalid

        dropped = int(rows_to_drop.sum())
        if dropped:
            logger.warning(
                "[%s] Dropped %d row(s) with invalid foreign key '%s' -> %s",
                table_name, dropped, fk_col, parent_table,
            )
            df = df[~rows_to_drop].copy()

    return df


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def transform_table(
    table_name: str,
    df: pd.DataFrame,
    valid_keys_registry: dict[str, set],
) -> pd.DataFrame:
    """
    Apply the full cleaning and validation pipeline to a single table.

    Args:
        table_name: Logical table name (must exist in config.PRIMARY_KEYS).
        df: Raw DataFrame for this table, as returned by extract.py.
        valid_keys_registry: Accumulated set of valid primary keys per
            table, used to validate foreign keys of tables processed later.

    Returns:
        pd.DataFrame: Cleaned, validated DataFrame ready for quality_checks.py.
    """
    logger.info("[%s] Starting transformation (%d raw rows)", table_name, len(df))

    df = normalize_column_names(df)
    df = trim_string_columns(df)
    df = normalize_missing_values(df)
    df = remove_duplicate_rows(df, table_name)
    df = remove_duplicate_primary_keys(df, table_name)
    df = convert_date_columns(df, table_name)
    df = convert_id_columns(df, table_name)
    df = validate_primary_key(df, table_name)
    df = validate_foreign_keys(df, table_name, valid_keys_registry)

    pk_col = config.PRIMARY_KEYS.get(table_name)
    if pk_col and pk_col in df.columns:
        valid_keys_registry[table_name] = set(df[pk_col].dropna().tolist())

    logger.info("[%s] Transformation complete (%d rows remain)", table_name, len(df))
    return df


def transform_all_tables(raw_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Transform every table extracted by extract.py, in dependency-safe
    order (config.SOURCE_TABLE_LOAD_ORDER), so foreign key validation
    always has access to already-cleaned parent keys.

    Args:
        raw_data: Mapping of table name -> raw DataFrame from extract.py.

    Returns:
        dict[str, pd.DataFrame]: Mapping of table name -> cleaned DataFrame.

    Raises:
        RuntimeError: If transformation fails for any table.
    """
    logger.info("Starting transformation for %d tables", len(raw_data))

    valid_keys_registry: dict[str, set] = {}
    transformed: dict[str, pd.DataFrame] = {}

    for table_name in config.SOURCE_TABLE_LOAD_ORDER:
        if table_name not in raw_data:
            logger.warning("Table '%s' not found in extracted data; skipping", table_name)
            continue
        try:
            transformed[table_name] = transform_table(
                table_name, raw_data[table_name], valid_keys_registry
            )
        except Exception as exc:
            logger.exception("Transformation failed for table '%s'", table_name)
            raise RuntimeError(
                f"Transformation pipeline aborted at table '{table_name}'"
            ) from exc

    logger.info("Transformation complete: %d/%d tables processed",
                len(transformed), len(raw_data))
    return transformed

def save_cleaned_data(cleaned_tables: dict[str, pd.DataFrame]) -> None:
    """
    Save all transformed tables as CSV files
    inside the cleaned_data folder.
    """

    OUTPUT_PATH.mkdir(exist_ok=True)

    for table_name, df in cleaned_tables.items():

        file_map = {
            "branches": "Branches.csv",
            "customers": "Customers.csv",
            "employees": "Employees.csv",
            "accounts": "Accounts.csv",
            "atms": "ATMs.csv",
            "loans": "Loans.csv",
            "creditcards": "CreditCards.csv",
            "beneficiaries": "Beneficiaries.csv",
            "mobilebanking": "MobileBanking.csv",
            "transactions": "Transactions.csv",
        }

        filename = file_map.get(table_name, f"{table_name}.csv")

        df.to_csv(
            OUTPUT_PATH / filename,
            index=False
        )

    logger.info("All cleaned CSV files saved successfully.")

if __name__ == "__main__":
    import extract

    config.setup_logging()

    raw = extract.extract_all_csv_files()

    cleaned = transform_all_tables(raw)

    save_cleaned_data(cleaned)

    print("\nSaved cleaned CSV files successfully.\n")

    for name, frame in cleaned.items():
        print(f"{name}: {frame.shape[0]} rows, {frame.shape[1]} columns")