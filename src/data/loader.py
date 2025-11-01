from abc import ABC, abstractmethod
from pathlib import Path

import polars as pl

from constants import VALID_TYPE_OF_BILL
from models import (
    CLAIMS_SCHEMA,
    INVOICES_SCHEMA,
    CLAIMS_REQUIRED_COLUMNS,
    INVOICES_REQUIRED_COLUMNS,
)


class DataValidationError(Exception):
    """Raised when data validation fails."""

    pass


class DataLoader(ABC):
    @abstractmethod
    def _validate_data(self, df: pl.DataFrame) -> None:
        """Validate the loaded data. Raise DataValidationError if invalid."""
        pass

    @abstractmethod
    def load(self) -> pl.DataFrame:
        """Load and validate data from CSV file."""
        pass


class ClaimsLoader(DataLoader):
    def __init__(self, file_path: str):
        self._file_path = Path(file_path)
        if not self._file_path.exists():
            raise FileNotFoundError(f"Claims file not found: {file_path}")

    def _validate_data(self, df: pl.DataFrame) -> None:
        for col in CLAIMS_REQUIRED_COLUMNS:
            null_count = df.filter(pl.col(col).is_null()).height
            if null_count > 0:
                raise DataValidationError(
                    f"Found {null_count} rows with null {col} in claims!"
                )

        invalid_patient_ids = df.filter(pl.col("patient_id") <= 0).height
        if invalid_patient_ids > 0:
            raise DataValidationError(
                f"Found {invalid_patient_ids} claims with non-positive patient_id"
            )

        negative_charges = df.filter(pl.col("charges_amount") < 0).height
        if negative_charges > 0:
            raise DataValidationError(
                f"Found {negative_charges} claims with negative charges_amount"
            )

        negative_benefits = df.filter(pl.col("benefit_amount") < 0).height
        if negative_benefits > 0:
            raise DataValidationError(
                f"Found {negative_benefits} claims with negative benefit_amount"
            )

        invalid_benefits = df.filter(
            pl.col("benefit_amount") > pl.col("charges_amount")
        ).height
        if invalid_benefits > 0:
            raise DataValidationError(
                f"Found {invalid_benefits} claims where benefit_amount > charges_amount"
            )

        duplicate_claims = (
            df.group_by("claim_id").agg(pl.count()).filter(pl.col("count") > 1).height
        )
        if duplicate_claims > 0:
            raise DataValidationError(f"Found {duplicate_claims} duplicate claim_ids")

    def load(self) -> pl.DataFrame:
        claims_df = pl.read_csv(self._file_path, schema_overrides=CLAIMS_SCHEMA)

        required_columns = CLAIMS_REQUIRED_COLUMNS
        if not required_columns.issubset(claims_df.columns):
            missing = required_columns - set(claims_df.columns)
            raise DataValidationError(
                f"Missing required columns in {self._file_path.name}: {missing}"
            )

        self._validate_data(claims_df)

        return claims_df


class InvoicesLoader(DataLoader):
    def __init__(self, file_path: str):
        self._file_path = Path(file_path)
        if not self._file_path.exists():
            raise FileNotFoundError(f"Invoices file not found: {file_path}")

    def _validate_data(self, df: pl.DataFrame) -> None:
        for col in INVOICES_REQUIRED_COLUMNS:
            null_count = df.filter(pl.col(col).is_null()).height
            if null_count > 0:
                raise DataValidationError(
                    f"Found {null_count} rows with null {col} in invoices - data quality issue!"
                )

        invalid_types = df.filter(
            ~pl.col("type_of_bill").is_in(VALID_TYPE_OF_BILL)
        ).height
        if invalid_types > 0:
            raise DataValidationError(
                f"Found {invalid_types} invoices with invalid type_of_bill (must be 'fee' or 'procedure payment')"
            )

        negative_transactions = df.filter(pl.col("transaction_value") < 0).height
        if negative_transactions > 0:
            raise DataValidationError(
                f"Found {negative_transactions} invoices with negative transaction_value"
            )

        duplicate_invoices = (
            df.group_by("invoice_id").agg(pl.count()).filter(pl.col("count") > 1).height
        )
        if duplicate_invoices > 0:
            raise DataValidationError(
                f"Found {duplicate_invoices} duplicate invoice_ids"
            )

    def load(self) -> pl.DataFrame:
        invoices_df = pl.read_csv(self._file_path, schema_overrides=INVOICES_SCHEMA)

        required_columns = INVOICES_REQUIRED_COLUMNS
        if not required_columns.issubset(invoices_df.columns):
            missing = required_columns - set(invoices_df.columns)

            raise DataValidationError(
                f"Missing required columns in {self._file_path.name}: {missing}"
            )

        self._validate_data(invoices_df)

        return invoices_df
