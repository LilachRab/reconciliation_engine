import polars as pl

PATIENT_SCHEMA = {
    "patient_id": pl.Int64,
    "name": pl.Utf8,
}

CLAIMS_SCHEMA = {
    "claim_id": pl.Utf8,  # String IDs like "C1", "C2", etc.
    "patient_id": pl.Int64,
    "date_of_service": pl.Date,
    "charges_amount": pl.Float64,
    "benefit_amount": pl.Float64,
}

INVOICES_SCHEMA = {
    "invoice_id": pl.Utf8,  # String IDs like "I1", "I2", etc.
    "claim_id": pl.Utf8,  # References claim_id
    "type_of_bill": pl.Utf8,  # "fee" or "procedure payment"
    "transaction_value": pl.Float64,
    "date_of_transaction": pl.Date,
}

PATIENT_REQUIRED_COLUMNS = set(PATIENT_SCHEMA.keys())
CLAIMS_REQUIRED_COLUMNS = set(CLAIMS_SCHEMA.keys())
INVOICES_REQUIRED_COLUMNS = set(INVOICES_SCHEMA.keys())
