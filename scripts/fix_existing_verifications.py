"""
Script to fix existing approved/rejected verifications that have null reviewed_at and admin_notes
"""
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.verification import Verification
from app.core.config import settings

def fix_existing_verifications():
    """Update existing approved/rejected verifications with proper reviewed_at timestamps"""
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find all approved/rejected verifications with null reviewed_at
        verifications = db.query(Verification).filter(
            Verification.status.in_(["APPROVED", "REJECTED"]),
            Verification.reviewed_at.is_(None)
        ).all()
        
        print(f"Found {len(verifications)} verifications to fix")
        
        for ver in verifications:
            # Set reviewed_at to created_at + 1 minute (approximate review time)
            ver.reviewed_at = ver.created_at
            
            # Add default admin notes based on status
            if ver.status == "APPROVED":
                ver.admin_notes = "Verification approved (auto-updated)"
            else:
                ver.admin_notes = "Verification rejected (auto-updated)"
            
            print(f"Updated verification ID {ver.id} for user {ver.user_id}")
        
        # Commit all changes
        db.commit()
        print(f"Successfully updated {len(verifications)} verifications")
        
    except Exception as e:
        print(f"Error updating verifications: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_existing_verifications()
