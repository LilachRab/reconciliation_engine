import random
from abc import ABC, abstractmethod

from constants import RECONCILIATION_STATUSES


class PaymentStatusStrategy(ABC):
    weight: float

    @abstractmethod
    def calculate_amount(self, benefit_amount: float) -> float:
        pass


class BalancedStrategy(PaymentStatusStrategy):
    weight = 0.55

    def calculate_amount(self, benefit_amount: float) -> float:
        return benefit_amount


class UnderpaidStrategy(PaymentStatusStrategy):
    weight = 0.225

    def calculate_amount(self, benefit_amount: float) -> float:
        return round(benefit_amount * random.uniform(0.6, 0.95), 2)


class OverpaidStrategy(PaymentStatusStrategy):
    weight = 0.225

    def calculate_amount(self, benefit_amount: float) -> float:
        return round(benefit_amount * random.uniform(1.05, 1.4), 2)


STRATEGIES = {
    RECONCILIATION_STATUSES["BALANCED"]: BalancedStrategy(),
    RECONCILIATION_STATUSES["UNDERPAID"]: UnderpaidStrategy(),
    RECONCILIATION_STATUSES["OVERPAID"]: OverpaidStrategy(),
}


def choose_strategy() -> PaymentStatusStrategy:
    weights = [s.weight for s in STRATEGIES.values()]
    return random.choices(list(STRATEGIES.values()), weights=weights)[0]
