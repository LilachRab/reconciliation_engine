import os
from reporting import generate_report
from data.loader import ClaimsLoader, InvoicesLoader
from processing import (
    reconcile_claims,
    analyze_reconciliation_results,
)
from utils import get_project_root


def run_reconciliation_engine(
    claims_file_path: str, invoices_file_path: str, output_file_path: str
) -> str:
    print("🚀 Starting full reconciliation workflow...")

    # Step 1: Load data using ClaimsLoader and InvoicesLoader
    project_root = get_project_root()
    claims_path = os.path.join(project_root, claims_file_path)
    invoices_path = os.path.join(project_root, invoices_file_path)

    claims_loader = ClaimsLoader(claims_path)
    invoices_loader = InvoicesLoader(invoices_path)

    claims_df = claims_loader.load()
    invoices_df = invoices_loader.load()
    print(f"✅ Loaded {claims_df.height} claims and {invoices_df.height} invoices")

    # Step 2: Send the load results to reconcile_claims()
    reconciled_df = reconcile_claims(claims_df, invoices_df)
    print(f"✅ Reconciled {reconciled_df.height} claims")

    # Step 3: Send reconcile_claims() results to analyze_reconciliation_results()
    analyzed_data = analyze_reconciliation_results(reconciled_df)
    print(f"✅ Analyzed reconciliation results")

    # Step 4: Generate the report
    report_path = generate_report(reconciled_df, analyzed_data, output_file_path)

    print(f"✅ Full reconciliation completed successfully!")
    print(f"📄 Report available at: {report_path}")

    return report_path
