import os

import polars as pl

from data import (
    PatientGenerator,
    ClaimGenerator,
    InvoiceGenerator,
)
from models import CLAIMS_SCHEMA, INVOICES_SCHEMA
from utils import get_project_root, ensure_directory_exists


def generate_input_data(
    num_of_patients: int, claims_file_path: str, invoices_file_path: str
):
    # Convert relative paths to absolute paths
    project_root = get_project_root()
    absolute_claims_path = os.path.join(project_root, claims_file_path)
    absolute_invoices_path = os.path.join(project_root, invoices_file_path)

    # Ensure directories exist
    ensure_directory_exists(absolute_claims_path)
    ensure_directory_exists(absolute_invoices_path)

    print(f"📊 Generating patients...")
    patients = PatientGenerator(num_of_patients).generate()
    claims = ClaimGenerator(patients).generate()
    invoices = InvoiceGenerator(claims).generate()

    claims_df = pl.DataFrame(claims, schema=CLAIMS_SCHEMA)
    invoices_df = pl.DataFrame(invoices, schema=INVOICES_SCHEMA)

    claims_df.write_csv(absolute_claims_path)
    invoices_df.write_csv(absolute_invoices_path)

    print(f"✅ Generated claims -> {absolute_claims_path}")
    print(f"✅ Generated invoices -> {absolute_invoices_path}")
