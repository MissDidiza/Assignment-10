"""
test_classes.py — Unit tests for core domain entity classes.
Tests attributes, methods, business rules, and edge cases.
"""
import pytest
from datetime import date, datetime
from src.user import User
from src.report import Report, LOCKED_STATUSES
from src.photo import Photo
from src.match_record import MatchRecord
from src.handover import Handover
from src.notification import Notification
from src.enums import (
    UserRole, ReportType, ReportStatus, ItemCategory,
    MatchStatus, HandoverStatus, NotificationType, NotificationChannel
)


# ── Fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def valid_user():
    pw_hash = User.hash_password("SecurePassword123")
    user = User("Iminathi Didiza", "iminathi@university.ac.za", pw_hash)
    user.verify_email()
    return user


@pytest.fixture
def valid_report(valid_user):
    return Report(
        user_id=valid_user.user_id,
        report_type=ReportType.LOST,
        item_name="Black Nike Backpack",
        category=ItemCategory.ACCESSORIES,
        description="Black Nike backpack with broken zip on left pocket and UCT keyring",
        location="Library — Second Floor",
        date_lost_or_found=date.today(),
    )


@pytest.fixture
def valid_photo(valid_report):
    return Photo(
        report_id=valid_report.report_id,
        cloudinary_url="https://res.cloudinary.com/campusfind/test.jpg",
        cloudinary_public_id="campusfind/test",
        file_size_kb=1024,
        mime_type="image/jpeg",
    )


# ── User Tests ────────────────────────────────────────────────────

class TestUser:

    def test_user_created_with_correct_defaults(self, valid_user):
        assert valid_user.full_name == "Iminathi Didiza"
        assert valid_user.role == UserRole.STUDENT
        assert valid_user.is_verified is True
        assert valid_user.email_notifications_enabled is True

    def test_user_id_is_uuid_string(self, valid_user):
        assert isinstance(valid_user.user_id, str)
        assert len(valid_user.user_id) == 36  # UUID format

    def test_valid_university_email_accepted(self):
        assert User.validate_email_domain("student@university.ac.za") is True

    def test_invalid_email_domain_rejected(self):
        assert User.validate_email_domain("student@gmail.com") is False

    def test_password_hashing_and_verification(self):
        pw_hash = User.hash_password("MyPassword!")
        assert User.check_password("MyPassword!", pw_hash) is True
        assert User.check_password("WrongPassword", pw_hash) is False

    def test_is_admin_returns_true_for_admin_role(self):
        u = User("Admin", "admin@university.ac.za", "hash", UserRole.ADMIN)
        assert u.is_admin() is True

    def test_is_admin_returns_false_for_student(self, valid_user):
        assert valid_user.is_admin() is False

    def test_is_super_admin(self):
        u = User("SA", "sa@university.ac.za", "hash", UserRole.SUPER_ADMIN)
        assert u.is_super_admin() is True
        assert u.is_admin() is True  # Super admin is also admin

    def test_deactivate_sets_not_verified(self, valid_user):
        valid_user.deactivate()
        assert valid_user.is_verified is False


# ── Report Tests ──────────────────────────────────────────────────

class TestReport:

    def test_report_created_with_open_status(self, valid_report):
        assert valid_report.status == ReportStatus.OPEN

    def test_validate_passes_with_valid_data(self, valid_report):
        assert valid_report.validate() is True

    def test_validate_fails_for_short_description(self, valid_user):
        report = Report(
            user_id=valid_user.user_id,
            report_type=ReportType.LOST,
            item_name="Bag",
            category=ItemCategory.ACCESSORIES,
            description="Short",  # < 20 chars
            location="Library",
            date_lost_or_found=date.today(),
        )
        with pytest.raises(ValueError, match="at least 20 characters"):
            report.validate()

    def test_add_photo_up_to_max(self, valid_report):
        for i in range(3):
            photo = Photo(valid_report.report_id, f"http://url{i}.jpg", f"id{i}", 500, "image/jpeg")
            valid_report.add_photo(photo)
        assert len(valid_report.photos) == 3

    def test_add_photo_beyond_max_raises(self, valid_report):
        for i in range(3):
            photo = Photo(valid_report.report_id, f"http://url{i}.jpg", f"id{i}", 500, "image/jpeg")
            valid_report.add_photo(photo)
        extra = Photo(valid_report.report_id, "http://extra.jpg", "extra", 500, "image/jpeg")
        with pytest.raises(ValueError, match="maximum of 3"):
            valid_report.add_photo(extra)

    def test_report_is_editable_when_open(self, valid_report):
        assert valid_report.is_editable() is True

    def test_report_not_editable_when_matched(self, valid_report):
        valid_report.update_status(ReportStatus.MATCHED)
        assert valid_report.is_editable() is False

    def test_trigger_matching_changes_status(self, valid_report):
        valid_report.trigger_matching()
        assert valid_report.status == ReportStatus.MATCHING

    def test_to_match_payload_returns_dict(self, valid_report):
        payload = valid_report.to_match_payload()
        assert payload["item_name"] == "Black Nike Backpack"
        assert payload["type"] == "LOST"
        assert isinstance(payload["photo_urls"], list)


# ── Photo Tests ───────────────────────────────────────────────────

class TestPhoto:

    def test_photo_validate_passes_valid_file(self):
        assert Photo.validate(1024, "image/jpeg") is True

    def test_photo_validate_rejects_oversized_file(self):
        with pytest.raises(ValueError, match="5 MB limit"):
            Photo.validate(6000, "image/jpeg")

    def test_photo_validate_rejects_invalid_mime_type(self):
        with pytest.raises(ValueError, match="Invalid file type"):
            Photo.validate(1000, "application/pdf")

    def test_photo_delete_marks_deleted(self, valid_photo):
        valid_photo.delete()
        assert valid_photo.is_deleted is True

    def test_fetch_deleted_photo_raises(self, valid_photo):
        valid_photo.delete()
        with pytest.raises(RuntimeError, match="deleted photo"):
            valid_photo.fetch_for_analysis()

    def test_fetch_active_photo_returns_url(self, valid_photo):
        url = valid_photo.fetch_for_analysis()
        assert url.startswith("https://")


# ── MatchRecord Tests ─────────────────────────────────────────────

class TestMatchRecord:

    def test_confidence_score_calculated_correctly(self):
        match = MatchRecord("lost-id", "found-id", 0.80, 0.90)
        expected = round(0.80 * 0.6 + 0.90 * 0.4, 4)
        assert match.confidence_score == expected

    def test_meets_threshold_above_70(self):
        match = MatchRecord("l", "f", 0.85, 0.75)
        assert match.meets_threshold() is True

    def test_does_not_meet_threshold_below_70(self):
        match = MatchRecord("l", "f", 0.50, 0.40)
        assert match.meets_threshold() is False

    def test_confirm_changes_status(self):
        match = MatchRecord("l", "f", 0.90, 0.85)
        match.notify()
        match.confirm("admin-123")
        assert match.status == MatchStatus.CONFIRMED

    def test_dismiss_requires_reason(self):
        match = MatchRecord("l", "f", 0.90, 0.85)
        match.notify()
        with pytest.raises(ValueError, match="reason is required"):
            match.dismiss("admin-123", "")

    def test_dismiss_with_reason_succeeds(self):
        match = MatchRecord("l", "f", 0.90, 0.85)
        match.notify()
        match.dismiss("admin-123", "Items are different colours")
        assert match.status == MatchStatus.DISMISSED

    def test_confirm_without_notify_raises(self):
        match = MatchRecord("l", "f", 0.90, 0.85)
        with pytest.raises(RuntimeError):
            match.confirm("admin-123")


# ── Handover Tests ────────────────────────────────────────────────

class TestHandover:

    @pytest.fixture
    def handover(self):
        return Handover("match-1", "lost-1", "found-1", "admin-1", "student-1")

    def test_handover_created_with_initiated_status(self, handover):
        assert handover.status == HandoverStatus.INITIATED

    def test_notify_student_sets_awaiting_collection(self, handover):
        handover.notify_student("Security Desk A", datetime.utcnow(), datetime.utcnow())
        assert handover.status == HandoverStatus.AWAITING_COLLECTION
        assert handover.pickup_location == "Security Desk A"

    def test_send_reminder_1(self, handover):
        handover.send_reminder(1)
        assert handover.status == HandoverStatus.REMINDER_1_SENT

    def test_send_reminder_2(self, handover):
        handover.send_reminder(2)
        assert handover.status == HandoverStatus.REMINDER_2_SENT

    def test_invalid_reminder_number_raises(self, handover):
        with pytest.raises(ValueError):
            handover.send_reminder(3)

    def test_record_collection_sets_collected(self, handover):
        handover.record_collection()
        assert handover.status == HandoverStatus.COLLECTED

    def test_manual_override_without_reason_raises(self, handover):
        with pytest.raises(ValueError, match="reason is required"):
            handover.record_manual_override("")

    def test_manual_override_with_reason_succeeds(self, handover):
        handover.record_manual_override("Student came in person without app access")
        assert handover.is_manual_override is True
        assert handover.status == HandoverStatus.COLLECTED


# ── Notification Tests ────────────────────────────────────────────

class TestNotification:

    @pytest.fixture
    def notification(self):
        return Notification(
            user_id="user-1",
            notification_type=NotificationType.MATCH_ALERT,
            channel=NotificationChannel.BOTH,
            subject="Match found!",
            body="Your item has been matched.",
            related_entity_id="match-1",
        )

    def test_notification_starts_queued(self, notification):
        assert notification.status.value == "QUEUED"
        assert notification.is_read is False

    def test_can_retry_within_limit(self, notification):
        assert notification.can_retry() is True

    def test_retry_increments_count(self, notification):
        notification.retry()
        assert notification.retry_count == 1

    def test_retry_exceeds_max_raises(self, notification):
        for _ in range(3):
            notification.retry()
        with pytest.raises(RuntimeError, match="Maximum retries"):
            notification.retry()

    def test_mark_read(self, notification):
        notification.mark_read()
        assert notification.is_read is True

    def test_mark_expired(self, notification):
        notification.mark_expired()
        assert notification.status.value == "EXPIRED"