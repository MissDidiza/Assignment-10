"""
prototype.py — Prototype Pattern
==================================
USE CASE: CampusFind admins frequently create Reports with similar
configurations for testing, demos, and seeding the staging environment.
Instead of constructing each Report from scratch (expensive validation
and field assignment), the Prototype pattern stores pre-configured
"template" Reports and clones them on demand.

PATTERN: Objects implement a clone() method. A cache (ReportPrototypeCache)
stores named prototypes and returns deep copies when requested.
"""
import copy
from datetime import date
from src.report import Report
from src.enums import ReportType, ItemCategory


class CloneableReport(Report):
    """
    Extends Report with a clone() method.
    The clone is a deep copy — modifying the clone does not affect the original.
    """

    def clone(self) -> "CloneableReport":
        """Return a deep copy of this report with a fresh report_id and timestamps."""
        import uuid
        from datetime import datetime

        cloned = copy.deepcopy(self)
        # Assign a new identity to the clone
        cloned._report_id = str(uuid.uuid4())
        cloned._created_at = datetime.utcnow()
        cloned._updated_at = datetime.utcnow()
        return cloned

    def with_user(self, user_id: str) -> "CloneableReport":
        """Convenience method: clone and assign to a different user."""
        cloned = self.clone()
        cloned._user_id = user_id
        return cloned


class ReportPrototypeCache:
    """
    Cache of pre-configured CloneableReport prototypes.
    Clients call get(key) to receive a ready-to-use clone.
    """

    def __init__(self):
        self._cache: dict[str, CloneableReport] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Seed the cache with common report templates."""

        electronics_lost = CloneableReport(
            user_id="template-user",
            report_type=ReportType.LOST,
            item_name="Laptop",
            category=ItemCategory.ELECTRONICS,
            description="Silver laptop with university sticker on the lid, charger included",
            location="Library — Second Floor",
            date_lost_or_found=date.today(),
        )
        self._cache["lost_electronics"] = electronics_lost

        keys_found = CloneableReport(
            user_id="template-user",
            report_type=ReportType.FOUND,
            item_name="Keys",
            category=ItemCategory.KEYS,
            description="Set of keys with a blue lanyard and a small torch attached",
            location="Student Centre — Main Entrance",
            date_lost_or_found=date.today(),
        )
        self._cache["found_keys"] = keys_found

        docs_lost = CloneableReport(
            user_id="template-user",
            report_type=ReportType.LOST,
            item_name="Student ID Card",
            category=ItemCategory.DOCUMENTS,
            description="University student ID card with photo and student number printed",
            location="Cafeteria — Block B",
            date_lost_or_found=date.today(),
        )
        self._cache["lost_documents"] = docs_lost

    def register(self, key: str, prototype: CloneableReport) -> None:
        """Register a new prototype under the given key."""
        self._cache[key] = prototype

    def get(self, key: str) -> CloneableReport:
        """Return a deep clone of the named prototype."""
        prototype = self._cache.get(key)
        if not prototype:
            raise KeyError(f"No prototype found for key: '{key}'")
        return prototype.clone()

    def list_keys(self) -> list:
        return list(self._cache.keys())