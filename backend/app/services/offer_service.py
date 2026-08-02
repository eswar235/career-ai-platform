"""
Job offer service for managing offers
"""

import logging
import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.application import JobOffer, ApplicationActivity

logger = logging.getLogger(__name__)


class OfferService:
    """Service for job offer management"""

    @staticmethod
    def create_offer(
        db: Session,
        application_id: uuid.UUID,
        salary: Optional[int] = None,
        start_date: Optional[date] = None,
        bonus: Optional[int] = None,
        benefits: Optional[str] = None,
        offer_letter_url: Optional[str] = None,
        offer_expiration_date: Optional[date] = None,
    ) -> JobOffer:
        """Create a new job offer"""
        try:
            # Check if offer already exists
            existing = (
                db.query(JobOffer)
                .filter(JobOffer.application_id == application_id)
                .first()
            )
            if existing:
                raise ValueError("Offer already exists for this application")

            offer = JobOffer(
                application_id=application_id,
                status="received",
                salary=salary,
                start_date=start_date,
                bonus=bonus,
                benefits=benefits,
                offer_letter_url=offer_letter_url,
                offer_expiration_date=offer_expiration_date,
            )

            db.add(offer)
            db.commit()
            db.refresh(offer)

            # Log activity
            OfferService._log_activity(
                db,
                application_id,
                "offer_received",
                f"Job offer received: ${salary}/year" if salary else "Job offer received",
            )

            logger.info(f"Created offer for application {application_id}")
            return offer
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating offer: {str(e)}")
            raise ValueError(f"Failed to create offer: {str(e)}")

    @staticmethod
    def get_offer(
        db: Session,
        offer_id: uuid.UUID,
    ) -> Optional[JobOffer]:
        """Get an offer by ID"""
        try:
            return db.query(JobOffer).filter(JobOffer.id == offer_id).first()
        except Exception as e:
            logger.error(f"Error retrieving offer: {str(e)}")
            raise ValueError(f"Failed to retrieve offer: {str(e)}")

    @staticmethod
    def get_application_offer(
        db: Session,
        application_id: uuid.UUID,
    ) -> Optional[JobOffer]:
        """Get offer for an application"""
        try:
            return (
                db.query(JobOffer)
                .filter(JobOffer.application_id == application_id)
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving offer: {str(e)}")
            raise ValueError(f"Failed to retrieve offer: {str(e)}")

    @staticmethod
    def update_offer(
        db: Session,
        offer_id: uuid.UUID,
        status: Optional[str] = None,
        salary: Optional[int] = None,
        start_date: Optional[date] = None,
        bonus: Optional[int] = None,
        benefits: Optional[str] = None,
        offer_letter_url: Optional[str] = None,
        offer_expiration_date: Optional[date] = None,
        negotiation_notes: Optional[str] = None,
    ) -> JobOffer:
        """Update an offer"""
        try:
            offer = db.query(JobOffer).filter(JobOffer.id == offer_id).first()
            if not offer:
                raise ValueError("Offer not found")

            old_status = offer.status

            if status is not None:
                offer.status = status
            if salary is not None:
                offer.salary = salary
            if start_date is not None:
                offer.start_date = start_date
            if bonus is not None:
                offer.bonus = bonus
            if benefits is not None:
                offer.benefits = benefits
            if offer_letter_url is not None:
                offer.offer_letter_url = offer_letter_url
            if offer_expiration_date is not None:
                offer.offer_expiration_date = offer_expiration_date
            if negotiation_notes is not None:
                offer.negotiation_notes = negotiation_notes

            # Set accepted date if accepting
            if status == "accepted" and not offer.accepted_date:
                offer.accepted_date = datetime.utcnow()

            db.commit()
            db.refresh(offer)

            # Log status change
            if status and old_status != status:
                OfferService._log_activity(
                    db,
                    offer.application_id,
                    "offer_status_changed",
                    f"Offer status changed to {status}",
                )

            logger.info(f"Updated offer {offer_id}")
            return offer
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating offer: {str(e)}")
            raise ValueError(f"Failed to update offer: {str(e)}")

    @staticmethod
    def accept_offer(
        db: Session,
        offer_id: uuid.UUID,
    ) -> JobOffer:
        """Accept a job offer"""
        try:
            offer = db.query(JobOffer).filter(JobOffer.id == offer_id).first()
            if not offer:
                raise ValueError("Offer not found")

            offer.status = "accepted"
            offer.accepted_date = datetime.utcnow()

            db.commit()
            db.refresh(offer)

            OfferService._log_activity(
                db,
                offer.application_id,
                "offer_accepted",
                "Job offer accepted",
            )

            logger.info(f"Accepted offer {offer_id}")
            return offer
        except Exception as e:
            db.rollback()
            logger.error(f"Error accepting offer: {str(e)}")
            raise ValueError(f"Failed to accept offer: {str(e)}")

    @staticmethod
    def decline_offer(
        db: Session,
        offer_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> JobOffer:
        """Decline a job offer"""
        try:
            offer = db.query(JobOffer).filter(JobOffer.id == offer_id).first()
            if not offer:
                raise ValueError("Offer not found")

            offer.status = "declined"
            if reason:
                offer.negotiation_notes = f"Declined: {reason}"

            db.commit()
            db.refresh(offer)

            OfferService._log_activity(
                db,
                offer.application_id,
                "offer_declined",
                f"Job offer declined{': ' + reason if reason else ''}",
            )

            logger.info(f"Declined offer {offer_id}")
            return offer
        except Exception as e:
            db.rollback()
            logger.error(f"Error declining offer: {str(e)}")
            raise ValueError(f"Failed to decline offer: {str(e)}")

    @staticmethod
    def delete_offer(
        db: Session,
        offer_id: uuid.UUID,
    ) -> None:
        """Delete an offer"""
        try:
            offer = db.query(JobOffer).filter(JobOffer.id == offer_id).first()
            if not offer:
                raise ValueError("Offer not found")

            application_id = offer.application_id
            db.delete(offer)
            db.commit()

            OfferService._log_activity(
                db, application_id, "offer_removed", "Offer record deleted"
            )

            logger.info(f"Deleted offer {offer_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting offer: {str(e)}")
            raise ValueError(f"Failed to delete offer: {str(e)}")

    @staticmethod
    def _log_activity(
        db: Session,
        application_id: uuid.UUID,
        activity_type: str,
        description: Optional[str] = None,
    ) -> None:
        """Log an activity"""
        try:
            activity = ApplicationActivity(
                application_id=application_id,
                activity_type=activity_type,
                description=description,
            )
            db.add(activity)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to log activity: {str(e)}")
