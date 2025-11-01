"""
Business domain constants and valid values.
"""

# Valid values for constrained fields
VALID_TYPE_OF_BILL = {"fee", "procedure payment"}

# Reconciliation status constants
RECONCILIATION_STATUSES = {
    "BALANCED": "BALANCED",
    "OVERPAID": "OVERPAID",
    "UNDERPAID": "UNDERPAID",
}
