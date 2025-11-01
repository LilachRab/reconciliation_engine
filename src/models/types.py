from typing import TypedDict
from datetime import date


class PatientDict(TypedDict):
    patient_id: int
    name: str


class ClaimDict(TypedDict):
    claim_id: str
    patient_id: int
    date_of_service: date
    charges_amount: float
    benefit_amount: float


class InvoiceDict(TypedDict):
    invoice_id: str
    claim_id: str
    type_of_bill: str
    transaction_value: float
    date_of_transaction: date
