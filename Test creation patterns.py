"""
test_creational_patterns.py — Unit tests for all 6 creational patterns.
Verifies correct object creation, attribute initialisation, and edge cases.
"""
import pytest
import threading
from datetime import date
from src.enums import ReportType, ItemCategory, NotificationType, NotificationChannel
from src.photo import Photo

from creational_patterns.simple_factory import NotificationFactory
from creational_patterns.factory_method import (
    LostReportCreator, FoundReportCreator, LostReport, FoundReport
)
from creational_patterns.abstract_factory import (
    ProductionServiceFactory, TestingServiceFactory, NotificationDispatcher
)
from creational_patterns.builder import ReportBuilder, ReportDirector
from creational_patterns.prototype import ReportPrototypeCache, CloneableReport
from creational_patterns.singleton import MatchingConfig, DatabaseConnectionPool


# ── Simple Factory Tests ──────────────────────────────────────────

class TestSimpleFactory:

    def test_creates_match_alert_notification(self):
        n = NotificationFactory.create("match_alert", "user-1", "match-1")
        assert n.notification_type == NotificationType.MATCH_ALERT
        assert n.channel == NotificationChannel.BOTH
        assert "match" in n.subject.lower()

    def test_creates_handover_notification_with_location(self):
        n = NotificationFactory.create(
            "handover_scheduled", "user-1", "handover-1",
            extra={"location": "Block A Security Desk"}
        )
        assert "Block A Security Desk" in n.body
        assert n.notification_type == NotificationType.HANDOVER_SCHEDULED

    def test_creates_reminder_with_day(self):
        n = NotificationFactory.create("reminder", "user-1", "handover-1", extra={"day": 7})
        assert "Day 7" in n.subject

    def test_creates_verification_email_only(self):
        n = NotificationFactory.create("verification", "user-1", "user-1")
        assert n.channel == NotificationChannel.EMAIL

    def test_creates_password_reset(self):
        n = NotificationFactory.create("password_reset", "user-1", "user-1")
        assert n.notification_type == NotificationType.PASSWORD_RESET

    def test_creates_daily_digest(self):
        n = NotificationFactory.create("daily_digest", "admin-1", "admin-1")
        assert n.notification_type == NotificationType.DAILY_DIGEST

    def test_unknown_type_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown notification type"):
            NotificationFactory.create("unknown_type", "user-1", "entity-1")


# ── Factory Method Tests ──────────────────────────────────────────

class TestFactoryMethod:

    def test_lost_creator_produces_lost_report(self):
        creator = LostReportCreator()
        report = creator.create_and_submit(
            "user-1", "Black Backpack", ItemCategory.ACCESSORIES,
            "Black Nike backpack with broken zip on the left side",
            "Library Block B", date.today()
        )
        assert isinstance(report, LostReport)
        assert report.report_type == ReportType.LOST

    def test_found_creator_produces_found_report(self):
        creator = FoundReportCreator()
        report = creator.create_and_submit(
            "user-2", "Set of Keys", ItemCategory.KEYS,
            "Set of keys with blue lanyard and small torch attached",
            "Cafeteria Entrance", date.today()
        )
        assert isinstance(report, FoundReport)
        assert report.report_type == ReportType.FOUND

    def test_found_report_notifies_admin_on_submit(self):
        creator = FoundReportCreator()
        report = creator.create_and_submit(
            "user-2", "Laptop", ItemCategory.ELECTRONICS,
            "Silver Dell laptop with university sticker on lid",
            "Computer Lab Room 204", date.today()
        )
        assert report.admin_notified is True

    def test_lost_creator_validates_on_submit(self):
        creator = LostReportCreator()
        with pytest.raises(ValueError):
            creator.create_and_submit(
                "user-1", "Bag", ItemCategory.ACCESSORIES,
                "Short",  # Too short — will fail validation
                "Library", date.today()
            )


# ── Abstract Factory Tests ────────────────────────────────────────

class TestAbstractFactory:

    def test_production_factory_creates_sendgrid_sender(self):
        factory = ProductionServiceFactory()
        sender = factory.create_email_sender()
        result = sender.send("student@university.ac.za", "Test", "Body")
        assert result["provider"] == "sendgrid"
        assert result["status"] == "delivered"

    def test_testing_factory_creates_mock_sender(self):
        factory = TestingServiceFactory()
        sender = factory.create_email_sender()
        result = sender.send("student@university.ac.za", "Test", "Body")
        assert result["provider"] == "mock"
        assert result["status"] == "captured"

    def test_mock_sender_records_sent_emails(self):
        factory = TestingServiceFactory()
        sender = factory.create_email_sender()
        sender.send("a@university.ac.za", "Subject 1", "Body 1")
        sender.send("b@university.ac.za", "Subject 2", "Body 2")
        assert len(sender.sent_emails) == 2

    def test_testing_storage_returns_localhost_url(self):
        factory = TestingServiceFactory()
        storage = factory.create_storage_client()
        url = storage.upload("/tmp/test.jpg", "test.jpg")
        assert "localhost" in url

    def test_dispatcher_uses_injected_factory(self):
        factory = TestingServiceFactory()
        dispatcher = NotificationDispatcher(factory)
        result = dispatcher.dispatch_match_alert("user@university.ac.za", "Laptop")
        assert result["provider"] == "mock"

    def test_production_storage_returns_cloudinary_url(self):
        factory = ProductionServiceFactory()
        storage = factory.create_storage_client()
        url = storage.upload("/tmp/photo.jpg", "photo.jpg")
        assert "cloudinary.com" in url


# ── Builder Tests ─────────────────────────────────────────────────

class TestBuilder:

    def test_builder_creates_valid_report(self):
        report = (
            ReportBuilder()
            .set_user("user-1")
            .set_type(ReportType.LOST)
            .set_item_name("Laptop")
            .set_category(ItemCategory.ELECTRONICS)
            .set_description("Silver laptop with UCT sticker and charger bag")
            .set_location("Library Second Floor")
            .set_date(date.today())
            .build()
        )
        assert report.item_name == "Laptop"
        assert report.report_type == ReportType.LOST

    def test_builder_raises_if_field_missing(self):
        with pytest.raises(ValueError, match="missing required fields"):
            ReportBuilder().set_user("user-1").build()  # Missing all other fields

    def test_builder_allows_up_to_3_photos(self):
        builder = ReportBuilder()
        builder.set_user("u").set_type(ReportType.FOUND).set_item_name("Keys")
        builder.set_category(ItemCategory.KEYS)
        builder.set_description("Keys with blue lanyard and small torch attached")
        builder.set_location("Cafeteria").set_date(date.today())
        for i in range(3):
            photo = Photo("r", f"http://url{i}.jpg", f"id{i}", 500, "image/jpeg")
            builder.add_photo(photo)
        report = builder.build()
        assert len(report.photos) == 3

    def test_builder_rejects_4th_photo(self):
        builder = ReportBuilder()
        for i in range(3):
            photo = Photo("r", f"http://url{i}.jpg", f"id{i}", 500, "image/jpeg")
            builder.add_photo(photo)
        extra = Photo("r", "http://extra.jpg", "extra", 500, "image/jpeg")
        with pytest.raises(ValueError, match="maximum of 3"):
            builder.add_photo(extra)

    def test_director_builds_minimal_lost_report(self):
        director = ReportDirector(ReportBuilder())
        report = director.build_minimal_lost_report(
            "user-1", "Wallet",
            "Brown leather wallet with student ID and bank cards inside",
            "Block A Corridor"
        )
        assert report.report_type == ReportType.LOST
        assert report.item_name == "Wallet"

    def test_builder_reset_allows_reuse(self):
        builder = ReportBuilder()
        builder.set_user("user-1")
        builder.reset()
        with pytest.raises(ValueError, match="missing required fields"):
            builder.build()


# ── Prototype Tests ───────────────────────────────────────────────

class TestPrototype:

    def test_cache_loads_default_prototypes(self):
        cache = ReportPrototypeCache()
        keys = cache.list_keys()
        assert "lost_electronics" in keys
        assert "found_keys" in keys
        assert "lost_documents" in keys

    def test_clone_produces_different_id(self):
        cache = ReportPrototypeCache()
        clone1 = cache.get("lost_electronics")
        clone2 = cache.get("lost_electronics")
        assert clone1.report_id != clone2.report_id

    def test_clone_preserves_item_name(self):
        cache = ReportPrototypeCache()
        clone = cache.get("lost_electronics")
        assert clone.item_name == "Laptop"

    def test_modifying_clone_does_not_affect_original(self):
        original = CloneableReport(
            user_id="template",
            report_type=ReportType.LOST,
            item_name="Phone",
            category=ItemCategory.ELECTRONICS,
            description="Black iPhone with cracked screen and red phone case",
            location="Cafeteria",
            date_lost_or_found=date.today(),
        )
        clone = original.clone()
        # Trigger a status change on the clone
        clone.update_status(clone.status.__class__.MATCHING)
        # Original should be unaffected
        from src.enums import ReportStatus
        assert original.status == ReportStatus.OPEN

    def test_with_user_clones_and_assigns_user(self):
        cache = ReportPrototypeCache()
        clone = cache.get("lost_electronics")
        personalised = clone.with_user("student-456")
        assert personalised.user_id == "student-456"
        assert personalised.report_id != clone.report_id

    def test_unknown_prototype_key_raises(self):
        cache = ReportPrototypeCache()
        with pytest.raises(KeyError, match="No prototype found"):
            cache.get("nonexistent_key")

    def test_register_custom_prototype(self):
        cache = ReportPrototypeCache()
        custom = CloneableReport(
            "template", ReportType.FOUND, "Umbrella", ItemCategory.ACCESSORIES,
            "Black folding umbrella with wooden handle found near main gate",
            "Main Gate", date.today()
        )
        cache.register("found_umbrella", custom)
        clone = cache.get("found_umbrella")
        assert clone.item_name == "Umbrella"


# ── Singleton Tests ───────────────────────────────────────────────

class TestSingleton:

    def test_matching_config_returns_same_instance(self):
        config1 = MatchingConfig()
        config2 = MatchingConfig()
        assert config1 is config2

    def test_matching_config_default_threshold(self):
        config = MatchingConfig()
        assert config.confidence_threshold == 0.70

    def test_updating_threshold_reflects_everywhere(self):
        config1 = MatchingConfig()
        config2 = MatchingConfig()
        config1.update(confidence_threshold=0.80)
        assert config2.confidence_threshold == 0.80
        # Reset for other tests
        config1.update(confidence_threshold=0.70)

    def test_invalid_threshold_raises(self):
        config = MatchingConfig()
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            config.confidence_threshold = 1.5

    def test_weights_must_sum_to_one(self):
        config = MatchingConfig()
        with pytest.raises(ValueError, match="must equal 1.0"):
            config.update(text_weight=0.7, image_weight=0.7)

    def test_db_pool_returns_same_instance(self):
        pool1 = DatabaseConnectionPool()
        pool2 = DatabaseConnectionPool()
        assert pool1 is pool2

    def test_db_pool_get_connection(self):
        pool = DatabaseConnectionPool()
        conn = pool.get_connection()
        assert conn is not None
        pool.release_connection()

    def test_singleton_thread_safety(self):
        """Verify that concurrent instantiation returns the same instance."""
        instances = []

        def create_instance():
            instances.append(MatchingConfig())

        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        first = instances[0]
        assert all(i is first for i in instances), "All threads must get the same instance"