from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        related_id: Optional[int] = None
    ) -> Notification:
        """Create a new notification for a user"""
        try:
            logger.info(f"Creating notification for user {user_id}: {title}")
            
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type,
                related_id=related_id
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            logger.info(f"Successfully created notification ID {notification.id}")
            return notification
        except Exception as e:
            logger.error(f"Failed to create notification: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def notify_listing_created(db: Session, listing, owner_id: str):
        """Notify when a new listing is created"""
        return NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Listing Created Successfully",
            message=f"Your listing '{listing.title}' has been created and is now live!",
            notification_type="listing_created",
            related_id=listing.id
        )
    
    @staticmethod
    def notify_listing_updated(db: Session, listing, owner_id: str):
        """Notify when a listing is updated"""
        return NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Listing Updated",
            message=f"Your listing '{listing.title}' has been updated successfully!",
            notification_type="listing_updated",
            related_id=listing.id
        )
    
    @staticmethod
    def notify_new_favorite(db: Session, listing, favorited_by_user_id: str):
        """Notify listing owner when someone favorites their listing"""
        return NotificationService.create_notification(
            db=db,
            user_id=listing.owner_id,
            title="Someone Liked Your Listing!",
            message=f"A user has added your listing '{listing.title}' to their favorites!",
            notification_type="new_favorite",
            related_id=listing.id
        )
    
    @staticmethod
    def notify_verification_status(db: Session, user_id: str, status: str):
        """Notify user about verification status change"""
        if status == "APPROVED":
            title = "Account Verified!"
            message = "Congratulations! Your account has been verified. You can now create listings."
        elif status == "REJECTED":
            title = "Verification Rejected"
            message = "Your verification request has been rejected. Please contact support for more information."
        else:
            title = "Verification Status Updated"
            message = f"Your verification status has been updated to: {status}"
            
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title=title,
            message=message,
            notification_type="verification_status",
            related_id=None
        )

    @staticmethod
    def notify_report_reviewed(db: Session, reporter_id: str, report_id: int, status: str, audit_log: str = None):
        """Notify reporter when their report has been reviewed by admin"""
        logger.info(f"Sending report review notification to user {reporter_id} for report {report_id} with status {status}")
        
        status_messages = {
            "RESOLVED": "Your report has been resolved. Thank you for helping keep our community safe!",
            "DISMISSED": "Your report has been reviewed and dismissed. No action was taken at this time.",
            "PENDING": "Your report is still under review. We'll update you once it's resolved.",
            "INVESTIGATING": "Your report is being investigated. We'll keep you updated on the progress."
        }
        
        title = "Report Status Update"
        message = status_messages.get(status, f"Your report status has been updated to: {status}")
        
        if audit_log:
            message += f" Admin notes: {audit_log}"
            
        return NotificationService.create_notification(
            db=db,
            user_id=reporter_id,
            title=title,
            message=message,
            notification_type="report_reviewed",
            related_id=report_id
        )
