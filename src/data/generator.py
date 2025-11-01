import random
from abc import ABC, abstractmethod
from typing import List

from faker import Faker

from constants import VALID_TYPE_OF_BILL
from models import (
    PatientDict,
    ClaimDict,
    InvoiceDict,
)
from strategies import choose_strategy

fake = Faker()


class DataGenerator(ABC):
    @abstractmethod
    def generate(self) -> List[dict]:
        pass


class PatientGenerator(DataGenerator):
    def __init__(self, num_of_patients: int):
        self.num_of_patients = num_of_patients

    def generate(self) -> List[PatientDict]:
        patients: List[PatientDict] = []

        for i in range(self.num_of_patients):
            patients.append(
                PatientDict(
                    patient_id=i + 1,
                    name=fake.name(),
                )
            )

        return patients


class ClaimGenerator(DataGenerator):
    def __init__(self, patients: List[PatientDict]):
        self.patients = patients

    def generate(self) -> List[ClaimDict]:
        claims: List[ClaimDict] = []
        claim_id = 1

        for patient in self.patients:
            random_claim_number = random.randint(2, 20)

            for _ in range(random_claim_number):
                charges_amount = round(random.uniform(0.000001, 10000), 2)
                benefit_amount = round(random.uniform(0, charges_amount), 2)
                date_of_service = fake.date_between(start_date="-2y", end_date="today")

                claims.append(
                    ClaimDict(
                        claim_id=f"C{claim_id}",
                        patient_id=patient["patient_id"],
                        date_of_service=date_of_service,
                        charges_amount=charges_amount,
                        benefit_amount=benefit_amount,
                    )
                )
                claim_id += 1

        return claims


class InvoiceGenerator(DataGenerator):
    def __init__(self, claims: List[ClaimDict]):
        self.claims = claims

    def _distribute_amount(self, total: float, num_of_invoices: int) -> List[float]:
        amount_parts = []
        remaining = total

        while len(amount_parts) < num_of_invoices - 1:
            portion = random.uniform(0.2, 0.6)
            value = round(remaining * portion, 2)
            amount_parts.append(value)
            remaining -= value
        amount_parts.append(round(remaining, 2))

        return amount_parts

    def generate(self) -> List[InvoiceDict]:
        invoices: List[InvoiceDict] = []
        invoice_id = 1

        for claim in self.claims:
            random_invoice_number = random.randint(1, 5)
            total_amount = claim["benefit_amount"]
            payment_status = choose_strategy()
            transaction_value = payment_status.calculate_amount(total_amount)
            invoice_amount_parts = self._distribute_amount(
                transaction_value, random_invoice_number
            )
            transaction_date = fake.date_between(start_date="-2y", end_date="today")

            for amount_part in invoice_amount_parts:
                invoices.append(
                    InvoiceDict(
                        invoice_id=f"I{invoice_id}",
                        claim_id=claim["claim_id"],
                        type_of_bill=random.choice(list(VALID_TYPE_OF_BILL)),
                        transaction_value=amount_part,
                        date_of_transaction=transaction_date,
                    )
                )
                invoice_id += 1

        return invoices
