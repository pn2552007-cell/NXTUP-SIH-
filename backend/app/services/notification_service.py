import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("nextup.notifications")

class BaseNotificationProvider(ABC):
    """Abstract Interface for Longitudinal Communication Gateways (WhatsApp/SMS/Email/Portal)"""

    @abstractmethod
    def send_followup_message(
        self,
        trainee_name: str,
        phone_or_email: str,
        checkpoint: str,
        channel: str = "PORTAL"
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def send_verification_request_to_employer(
        self,
        employer_name: str,
        employer_email: str,
        trainee_name: str,
        job_title: str
    ) -> Dict[str, Any]:
        pass


class NotificationService(BaseNotificationProvider):
    """
    Extensible notification service provider for NEXTUP.
    Supports portal notifications, console logging, and hooks for SMS/WhatsApp gateways.
    NOTE: SMS/WhatsApp integration is PLANNED — currently using mock/portal delivery.
    """

    CHECKPOINT_TEMPLATES = {
        "30_DAYS": (
            "Hello {name}! Checking in at your 30-day post-training milestone. "
            "Please confirm your current employment status and role: /trainee/dashboard"
        ),
        "90_DAYS": (
            "Hi {name}, checking in at your 90-day milestone. "
            "Are you currently employed or interviewing? Update your progress: /trainee/dashboard"
        ),
        "6_MONTHS": (
            "Greetings {name}! It has been 6 months since training completion. "
            "Please confirm your retention milestone and current compensation: /trainee/dashboard"
        ),
        "12_MONTHS": (
            "Happy 1-year graduation milestone, {name}! "
            "Share your career progression, promotions, and wage growth: /trainee/dashboard"
        )
    }

    def send_followup_message(
        self,
        trainee_name: str,
        phone_or_email: str,
        checkpoint: str,
        channel: str = "PORTAL"
    ) -> Dict[str, Any]:
        template = self.CHECKPOINT_TEMPLATES.get(
            checkpoint,
            "Hello {name}, checking in on your post-training career outcome journey."
        )
        msg_body = template.format(name=trainee_name)

        logger.info(
            "Longitudinal Notification Queued [%s] via %s to %s: %s",
            checkpoint, channel, phone_or_email, msg_body
        )

        return {
            "channel": channel,
            "recipient": phone_or_email,
            "checkpoint": checkpoint,
            "message": msg_body,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "QUEUED"
        }

    def send_verification_request_to_employer(
        self,
        employer_name: str,
        employer_email: str,
        trainee_name: str,
        job_title: str
    ) -> Dict[str, Any]:
        msg_body = (
            f"NEXTUP Employer Verification: Trainee {trainee_name} has reported joining {employer_name} "
            f"as {job_title}. Please review and verify this placement on the NEXTUP Employer Portal."
        )
        logger.info("Employer Verification Notification sent to %s (%s): %s", employer_name, employer_email, msg_body)
        return {
            "recipient": employer_email,
            "employer_name": employer_name,
            "trainee_name": trainee_name,
            "status": "QUEUED",
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
notification_service = NotificationService()
