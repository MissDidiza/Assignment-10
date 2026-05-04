"""
builder.py — Builder Pattern
=============================
USE CASE: A Report in CampusFind has many optional and required fields.
Constructing a Report object directly with all fields in one constructor
call is error-prone and hard to read, especially when some fields
(e.g., photos, date) might be added at different times.

The Builder pattern constructs a Report step-by-step, making the
construction process readable and preventing partially initialised objects.

PATTERN: Director optionally orchestrates the building steps.
Builder exposes chainable set_*() methods and a final build() method.
"""
from datetime import date
from typing import List, Optional
from src.report import Report
from src.photo import Photo
from src.enums import ReportType, ItemCategory


class ReportBuilder:
    """
    Builder — constructs a Report object step by step.
    All required fields must be set before build() is called.
    """

    def __init__(self):
        self._user_id: Optional[str] = None
        self._report_type: Optional[ReportType] = None
        self._item_name: Optional[str] = None
        self._category: Optional[ItemCategory] = None
        self._description: Optional[str] = None
        self._location: Optional[str] = None
        self._date_lost_or_found: Optional[date] = None
        self._photos: List[Photo] = []

    def set_user(self, user_id: str) -> "ReportBuilder":
        self._user_id = user_id
        return self

    def set_type(self, report_type: ReportType) -> "ReportBuilder":
        self._report_type = report_type
        return self

    def set_item_name(self, item_name: str) -> "ReportBuilder":
        self._item_name = item_name
        return self

    def set_category(self, category: ItemCategory) -> "ReportBuilder":
        self._category = category
        return self

    def set_description(self, description: str) -> "ReportBuilder":
        self._description = description
        return self

    def set_location(self, location: str) -> "ReportBuilder":
        self._location = location
        return self

    def set_date(self, event_date: date) -> "ReportBuilder":
        self._date_lost_or_found = event_date
        return self

    def add_photo(self, photo: Photo) -> "ReportBuilder":
        if len(self._photos) >= 3:
            raise ValueError("A report can have a maximum of 3 photos.")
        self._photos.append(photo)
        return self

    def build(self) -> Report:
        """Validate all required fields then construct and return the Report."""
        missing = []
        if not self._user_id:
            missing.append("user_id")
        if not self._report_type:
            missing.append("report_type")
        if not self._item_name:
            missing.append("item_name")
        if not self._category:
            missing.append("category")
        if not self._description:
            missing.append("description")
        if not self._location:
            missing.append("location")
        if not self._date_lost_or_found:
            missing.append("date_lost_or_found")

        if missing:
            raise ValueError(f"Cannot build Report — missing required fields: {missing}")

        report = Report(
            user_id=self._user_id,
            report_type=self._report_type,
            item_name=self._item_name,
            category=self._category,
            description=self._description,
            location=self._location,
            date_lost_or_found=self._date_lost_or_found,
        )

        for photo in self._photos:
            report.add_photo(photo)

        return report

    def reset(self) -> "ReportBuilder":
        """Reset the builder so it can be reused for a new report."""
        self.__init__()
        return self


# ── Director ──────────────────────────────────────────────────────

class ReportDirector:
    """
    Director — knows how to build specific types of reports using the builder.
    Encapsulates common construction sequences.
    """

    def __init__(self, builder: ReportBuilder):
        self._builder = builder

    def build_minimal_lost_report(
        self, user_id: str, item_name: str, description: str, location: str
    ) -> Report:
        """Construct the simplest valid lost report (no photos, today's date)."""
        return (
            self._builder
            .reset()
            .set_user(user_id)
            .set_type(ReportType.LOST)
            .set_item_name(item_name)
            .set_category(ItemCategory.OTHER)
            .set_description(description)
            .set_location(location)
            .set_date(date.today())
            .build()
        )

    def build_full_found_report(
        self,
        user_id: str,
        item_name: str,
        category: ItemCategory,
        description: str,
        location: str,
        event_date: date,
        photos: List[Photo],
    ) -> Report:
        """Construct a fully populated found report with photos."""
        self._builder.reset().set_user(user_id).set_type(ReportType.FOUND)
        self._builder.set_item_name(item_name).set_category(category)
        self._builder.set_description(description).set_location(location)
        self._builder.set_date(event_date)
        for photo in photos:
            self._builder.add_photo(photo)
        return self._builder.build()