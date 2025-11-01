from generate_input_data import generate_input_data
from reconciliation_engine import run_reconciliation_engine


if __name__ == "__main__":
    NUM_OF_PATIENTS = 200
    CLAIMS_FILE_PATH = "input/claims.csv"
    INVOICES_FILE_PATH = "input/invoices.csv"
    OUTPUT_FILE_PATH = "output/report.html"

    # Generate input data
    generate_input_data(NUM_OF_PATIENTS, CLAIMS_FILE_PATH, INVOICES_FILE_PATH)

    # Run the reconciliation engine
    run_reconciliation_engine(CLAIMS_FILE_PATH, INVOICES_FILE_PATH, OUTPUT_FILE_PATH)
