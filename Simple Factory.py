"""
simple_factory.py — Simple Factory Pattern
==========================================
USE CASE: CampusFind needs to create different types of Notifications
(MATCH_ALERT, HANDOVER_SCHEDULED, REMINDER) without the calling code
needing to know the construction details of each type.

The NotificationFactory centralises all notification object creation.
This maps to FR-06 (match notifications) and FR-08 (handover notifications).

PATTERN: A single factory class with a static method that returns
different object types based on a parameter.
"""
from src.notification import Notification
from src.enums import NotificationType, NotificationChannel


class NotificationFactory:
    """
    Simple Factory — centralises creation of all Notification types.
    Calling code passes a type string and receives a fully configured Notification.
    """

    @staticmethod
    def create(
        notification_type: str,
        user_id: str,
        related_entity_id: str,
        extra: dict = None,
    ) -> Notification:
        """
        Factory method — returns the appropriate Notification instance.

        Args:
            notification_type: One of 'match_alert', 'handover_scheduled', 'reminder',
                               'verification', 'password_reset', 'daily_digest'
            user_id: Recipient's user ID
            related_entity_id: ID of the triggering entity (match or handover)
            extra: Optional dict for custom subject/body overrides
        """
        extra = extra or {}
        nt = notification_type.lower()

        if nt == "match_alert":
            return Notification(
                user_id=user_id,
                notification_type=NotificationType.MATCH_ALERT,
                channel=NotificationChannel.BOTH,
                subject="CampusFind: A match has been found for your lost item!",
                body=(
                    "Good news! Our system has found a probable match for your lost item. "
                    "Please log in to CampusFind to review the match and arrange collection."
                ),
                related_entity_id=related_entity_id,
            )

        elif nt == "handover_scheduled":
            location = extra.get("location", "Security Desk")
            return Notification(
                user_id=user_id,
                notification_type=NotificationType.HANDOVER_SCHEDULED,
                channel=NotificationChannel.BOTH,
                subject="CampusFind: Your item is ready for collection",
                body=(
                    f"Your matched item is ready for collection at {location}. "
                    "Please click the confirmation link when you collect it."
                ),
                related_entity_id=related_entity_id,
            )

        elif nt == "reminder":
            day = extra.get("day", 3)
            return Notification(
                user_id=user_id,
                notification_type=NotificationType.REMINDER,
                channel=NotificationChannel.BOTH,
                subject=f"CampusFind: Reminder — please collect your item (Day {day})",
                body=(
                    f"This is a reminder that your matched item has not been collected yet. "
                    f"Please collect it as soon as possible to avoid it being marked unclaimed."
                ),
                related_entity_id=related_entity_id,
            )

        elif nt == "verification":
            return Notification(
                user_id=user_id,
                notification_type=NotificationType.VERIFICATION,
                channel=NotificationChannel.EMAIL,
                subject="CampusFind: Verify your email address",
                body="Please click the link below to verify your CampusFind account.",
                related_entity_id=related_entity_id,
            )

        elif nt == "password_reset":
            return Notification(
                user_id=user_id,
                notification_type=NotificationType.PASSWORD_RESET,
                channel=NotificationChannel.EMAIL,
                subject="CampusFind: Password reset request",
                body="Click the link to reset your password. This link expires in 1 hour.",
                related_entity_id=related_entity_id,
            )

        elif nt == "daily_digest":
            return Notification(
                user_id=user_id,
                notification_type=NotificationType.DAILY_DIGEST,
                channel=NotificationChannel.EMAIL,
                subject="CampusFind: Daily Admin Digest",
                body="Here is your daily summary of pending matches and handovers.",
                related_entity_id=related_entity_id,
            )

        else:
            raise ValueError(f"Unknown notification type: '{notification_type}'")