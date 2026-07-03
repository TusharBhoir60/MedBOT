"""Abstract CarePlanProvider interface for future extensibility."""
from abc import ABC, abstractmethod
from typing import Any, Dict

from schemas.patient_response import CarePlan


class CarePlanProvider(ABC):
    """
    Abstract interface for care plan sources.
    Concrete implementations can be static templates, LLM-generated plans,
    or external clinical decision support systems.
    """

    @abstractmethod
    def get_plan(self, condition: str) -> CarePlan:
        """
        Returns a base CarePlan for the given condition name.
        Returns a generic/unknown plan if condition is not found.
        """
        ...

    @abstractmethod
    def supports(self, condition: str) -> bool:
        """Returns True if this provider has a plan for the given condition."""
        ...
