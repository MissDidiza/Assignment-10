"""
factory_method.py — Factory Method Pattern
==========================================
USE CASE: CampusFind supports two types of Reports — LostReport and FoundReport.
Both share the same base Report class but have different default behaviours:
- LostReport triggers matching immediately on submission
- FoundReport notifies admin immediately on submission

The Factory Method pattern delegates the creation of the correct Report
subclass to a subclass of ReportCreator, keeping the base creation logic
in the parent class.

PATTERN: Abstract base class defines a factory_method() that subclasses override
to return the correct concrete product.
"""
from abc import ABC, abstractmethod
from datetime import date
from src.report import Report
from src.enums import ReportType, ItemCategory


# ── Concrete Report Subclasses ────────────────────────────────────

class LostReport(Report):
    """A Report submitted by a student who has lost an item."""

    def __init__(self, user_id, item_name, category, description, location, date_lost):
        super().__init__(
            user_id=user_id,
            report_type=ReportType.LOST,
            item_name=item_name,
            category=category,
            description=description,
            location=location,
            date_lost_or_found=date_lost,
        )

    def submit(self) -> "LostReport":
        """Validate and trigger AI matching on submission."""
        self.validate()
        self.trigger_matching()
        return self

    def __repr__(self):
        return f"LostReport(id={self.report_id[:8]}, item='{self.item_name}')"


class FoundReport(Report):
    """A Report submitted by a finder who has found an item."""

    def __init__(self, user_id, item_name, category, description, location, date_found):
        super().__init__(
            user_id=user_id,
            report_type=ReportType.FOUND,
            item_name=item_name,
            category=category,
            description=description,
            location=location,
            date_lost_or_found=date_found,
        )
        self._admin_notified: bool = False

    def submit(self) -> "FoundReport":
        """Validate and mark admin as needing notification."""
        self.validate()
        self._admin_notified = True
        self.trigger_matching()
        return self

    @property
    def admin_notified(self) -> bool:
        return self._admin_notified

    def __repr__(self):
        return f"FoundReport(id={self.report_id[:8]}, item='{self.item_name}')"


# ── Abstract Creator ──────────────────────────────────────────────

class ReportCreator(ABC):
    """
    Abstract creator — defines the factory_method interface.
    Subclasses override factory_method() to produce the correct Report type.
    """

    @abstractmethod
    def factory_method(
        self,
        user_id: str,
        item_name: str,
        category: ItemCategory,
        description: str,
        location: str,
        event_date: date,
    ) -> Report:
        """Override in subclass to return LostReport or FoundReport."""
        pass

    def create_and_submit(
        self,
        user_id: str,
        item_name: str,
        category: ItemCategory,
        description: str,
        location: str,
        event_date: date,
    ) -> Report:
        """Template method — create via factory_method then submit."""
        report = self.factory_method(
            user_id, item_name, category, description, location, event_date
        )
        report.submit()
        return report


# ── Concrete Creators ─────────────────────────────────────────────

class LostReportCreator(ReportCreator):
    """Creates LostReport instances."""

    def factory_method(self, user_id, item_name, category, description, location, event_date):
        return LostReport(user_id, item_name, category, description, location, event_date)


class FoundReportCreator(ReportCreator):
    """Creates FoundReport instances."""

    def factory_method(self, user_id, item_name, category, description, location, event_date):
        return FoundReport(user_id, item_name, category, description, location, event_date)